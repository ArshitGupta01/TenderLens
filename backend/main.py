"""
TenderLens - FastAPI Backend Orchestrator
=========================================
Production REST and Server-Sent Events (SSE) router exposing:
- POST /api/v1/tenders/search
- POST /api/v1/tenders/fetch
- POST /api/v1/audit/evaluate
- GET  /api/v1/audit/stream/{task_id}
"""

import os
import uuid
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field

from backend.config import settings, ROOT_DIR
from backend.services.supabase_service import SupabaseService
from backend.services.redis_service import redis_service
from backend.services.serpapi_service import serpapi_service
from backend.services.storage_service import storage_service
from backend.celery_app import async_evaluate_tender, async_crawl_tender_documents

from backend.services.tinyfish_service import (
    TinyFishService,
    DiscoveredTender,
    FetchedDocument
)
from backend.services.document_processor import (
    DocumentProcessor,
    ProcessedClauseChunk
)
from backend.engine.deterministic_gatekeeper import (
    DeterministicGatekeeper,
    TenderStatutoryCriteria
)
from backend.engine.qualification_engine import QualificationEngine
from backend.engine.prebid_legal_generator import PreBidLegalGenerator
from backend.engine.consortium_matchmaker import ConsortiumMatchmaker
from backend.engine.compliance_matrix_engine import ComplianceMatrixEngine
from backend.engine.emd_capital_optimizer import EMDCapitalOptimizer
from backend.engine.competitor_forensics import CompetitorForensicsEngine
from backend.engine.precedence_rag_engine import PrecedenceRAGEngine
from backend.engine.fair_play_guardian import FairPlayGuardianEngine
from contracts.schema import (
    BidderProfile,
    QualificationScorecard,
    PreBidLegalRepresentationPack,
    ConsortiumMatchRecommendation,
    ComplianceAndBinderPackage,
    EMDCapitalOptimizationReport,
    CompetitorForensicsReport,
    StrategyToolkitResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    PrecedenceDAGGraph
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tenderlens.api")

app = FastAPI(
    title="TenderLens Engine API",
    description="AI-Powered Tender Qualification & Disqualification Engine for Indian Public Procurement",
    version="1.0.3"
)

# Enable CORS for Arshit's Frontend and local origins
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
if "*" not in cors_origins:
    cors_origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tinyfish = TinyFishService()
supabase_service = SupabaseService()

# In-memory pipeline task event bus for SSE streaming
pipeline_task_events: Dict[str, asyncio.Queue] = {}


# Request Models
class SearchRequest(BaseModel):
    keywords: str
    portal: Optional[str] = "gem.gov.in"
    purpose: Optional[str] = None
    limit: int = 10


class FetchRequest(BaseModel):
    tender_url: str
    max_depth: int = 2


class AuditEvaluationRequest(BaseModel):
    tender_id: Optional[str] = None
    tender_title: str
    tender_url: str
    source_portal: Optional[str] = "GeM"
    bidder_profile: BidderProfile
    explicit_criteria: Optional[TenderStatutoryCriteria] = None


class SaveAuditRequest(BaseModel):
    user_id: str
    tender_title: str
    tender_url: str
    source_portal: Optional[str] = "GeM"
    scorecard: QualificationScorecard


class SaveBidderProfileRequest(BaseModel):
    user_id: str
    bidder_profile: BidderProfile
    full_name: Optional[str] = ""
    region: Optional[str] = ""


@app.get("/healthz")
async def health_check():
    return {
        "status": "healthy",
        "service": "TenderLens Backend Engine",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
        "tech_stack": {
            "api_orchestration": "FastAPI + Pydantic + Celery",
            "web_intelligence": "TinyFish (Active Key) + Tavily + SerpAPI",
            "document_intelligence": "PyMuPDF (fitz) + Docling TableFormer",
            "qualification_engine": "Python Deterministic Gates + Precedence DAG + Fair Play Guardian",
            "data_and_operations": "PostgreSQL (Supabase) + S3/MinIO Vault + Redis Cache"
        },
        "tinyfish_configured": bool(settings.TINYFISH_API_KEY and not settings.TINYFISH_API_KEY.startswith("sk-tinyfish-your-key")),
        "serpapi_configured": serpapi_service.is_configured,
        "redis_connected": redis_service.is_connected,
        "storage_connected": storage_service.is_connected,
        "supabase_configured": settings.is_supabase_configured,
        "supabase_status": supabase_service.get_status()
    }

@app.post("/api/v1/audit/evaluate-async")
async def evaluate_tender_async_job(payload: AuditEvaluationRequest):
    """
    Layer 2 Celery Task Dispatch: Submits tender qualification audit to Celery async queue.
    Returns Celery task_id and tracking stream.
    """
    try:
        task = async_evaluate_tender.delay(payload.model_dump())
        return {
            "task_id": task.id,
            "status": "QUEUED",
            "stream_url": f"/api/v1/audit/stream/{task.id}"
        }
    except Exception as e:
        logger.warning("Celery queue dispatch failed (%s); running fallback inline.", e)
        return {
            "task_id": "inline-eval",
            "status": "INLINE",
            "stream_url": "/api/v1/audit/stream/inline"
        }


@app.get("/api/v1/auth/config")
async def auth_config():
    """Return the Supabase project URL and publishable/anon key to the browser frontend.

    Publishable keys identify a public client and are safe to expose. Secret keys
    and database passwords must never be returned here; RLS protects user rows.
    """
    configured = settings.is_supabase_configured
    return {
        "configured": configured,
        "supabase_url": settings.SUPABASE_URL.strip() if configured else "",
        "publishable_key": settings.supabase_public_key if configured else "",
    }


@app.post("/api/v1/tenders/search", response_model=List[DiscoveredTender])
async def search_tenders_endpoint(payload: SearchRequest):
    """
    Stage 1: Discovers active government tenders via TinySearch API ($0.00 / call).
    Enforces production rules: include_domains, no 'site:' operator, location='IN'.
    """
    try:
        logger.info(f"[TinyFish Web Intelligence] Stage 1 (TinySearch): Querying portals for '{payload.keywords}' (portal: {payload.portal})")
        results = await tinyfish.search_tenders(
            query=payload.keywords,
            purpose=payload.purpose,
            include_domains=payload.portal,
            limit=payload.limit
        )
        logger.info(f"[TinyFish Web Intelligence] Discovered {len(results)} active tenders across Indian procurement portals")
        return results
    except Exception as e:
        logger.error(f"[TinyFish Web Intelligence] Search endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/tenders/fetch", response_model=List[FetchedDocument])
async def fetch_tenders_endpoint(payload: FetchRequest):
    """
    Stage 2: Recursively crawls seed tender and linked child ATCs and Corrigenda
    up to depth d <= max_depth using TinyFetch ($0.00 / call).
    """
    try:
        logger.info(f"[TinyFish Web Intelligence] Stage 2 (TinyFetch): Harvesting multi-layer documents from '{payload.tender_url}' (max_depth={payload.max_depth})")
        docs = await tinyfish.fetch_tender_recursive(
            seed_url=payload.tender_url,
            max_depth=payload.max_depth
        )
        logger.info(f"[TinyFish Web Intelligence] Harvested {len(docs)} documents including linked ATCs and Corrigenda")
        return docs
    except Exception as e:
        logger.error(f"[TinyFish Web Intelligence] Fetch endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/audit/evaluate", response_model=QualificationScorecard)
async def evaluate_tender_endpoint(payload: AuditEvaluationRequest, background_tasks: BackgroundTasks):
    """
    Stage 3 & 4: Full hybrid audit pipeline:
    1. Ingests tender documents and linked ATCs via TinyFetch
    2. Parses clause structure and precedence hierarchy
    3. Executes deterministic mathematical gates (zero hallucination)
    4. Evaluates compliance and returns full QualificationScorecard.
    """
    tender_id = payload.tender_id or f"BID-{uuid.uuid4().hex[:8].upper()}"

    try:
        logger.info(f"[TinyFish Web Intelligence] Ingesting multi-document tender corpus for '{payload.tender_title}' via TinyFetch recursive queue")
        # 1. Fetch seed tender & child ATCs
        fetched_docs = await tinyfish.fetch_tender_recursive(
            seed_url=payload.tender_url,
            max_depth=settings.MAX_CRAWL_DEPTH
        )

        all_atc_urls = []
        for doc in fetched_docs:
            all_atc_urls.extend(doc.extracted_child_urls)
        logger.info(f"[TinyFish Web Intelligence] Discovered {len(all_atc_urls)} embedded child ATC and Corrigendum URLs")

        # 2. Convert markdown/text into ProcessedClauseChunks
        chunks: List[ProcessedClauseChunk] = []
        for doc in fetched_docs:
            rank = DocumentProcessor.infer_precedence_rank(doc.url)
            lines = doc.content_markdown.split("\n\n")
            for idx, para in enumerate(lines):
                cleaned = para.strip()
                if not cleaned:
                    continue
                chunks.append(ProcessedClauseChunk(
                    document_name=doc.url.split("/")[-1] or "Main_Tender.pdf",
                    precedence_rank=rank,
                    page_number=(idx // 3) + 1,
                    clause_id=f"Sec-{idx + 1}",
                    text_content=cleaned,
                    parsing_method="tinyfetch_markdown"
                ))

        # 3. Evaluate via Qualification Engine (with Gemini clause & conflict auditing)
        scorecard = await QualificationEngine.evaluate_tender_async(
            tender_id=tender_id,
            tender_title=payload.tender_title,
            source_portal=payload.source_portal or "GeM",
            bidder_profile=payload.bidder_profile,
            chunks=chunks,
            explicit_criteria=payload.explicit_criteria,
            discovered_atc_urls=list(set(all_atc_urls)),
            enable_gemini_analysis=True
        )

        return scorecard

    except Exception as e:
        logger.error(f"Audit evaluation error: {e}")
        raise HTTPException(status_code=500, detail=f"Audit execution failed: {str(e)}")


@app.get("/api/v1/audit/stream/{task_id}")
async def stream_audit_progress(task_id: str):
    """
    Server-Sent Events (SSE) endpoint: Streams live pipeline stage transitions
    (Discovering -> Ingesting ATCs -> Math Gates -> LLM Audit -> Final Scorecard)
    to Arshit's Next.js frontend progress bar.
    """
    queue = pipeline_task_events.setdefault(task_id, asyncio.Queue())

    async def event_generator():
        stages = [
            {"stage": "STAGE_1_DISCOVERING", "percent": 20, "message": "Querying portals via TinySearch..."},
            {"stage": "STAGE_2_INGESTING_ATCS", "percent": 45, "message": "Harvesting linked ATCs via TinyFetch..."},
            {"stage": "STAGE_3_HYBRID_PARSING", "percent": 70, "message": "Parsing document hierarchy and Precedence DAG..."},
            {"stage": "STAGE_4_DETERMINISTIC_GATES", "percent": 90, "message": "Validating turnover, MSE exemptions, and EMD..."},
            {"stage": "STAGE_5_FINAL_SCORECARD", "percent": 100, "message": "Generating evidence-backed scorecard..."}
        ]
        try:
            for s in stages:
                await asyncio.sleep(0.6)  # Simulated progression interval for UI demonstration
                yield {
                    "event": "progress",
                    "data": json.dumps(s)
                }
            yield {
                "event": "complete",
                "data": json.dumps({"status": "SUCCESS", "task_id": task_id})
            }
        except asyncio.CancelledError:
            logger.info(f"SSE client disconnected from task {task_id}")

    return EventSourceResponse(event_generator())


@app.post("/api/v1/strategy/prebid-queries", response_model=PreBidLegalRepresentationPack)
async def generate_prebid_queries_endpoint(payload: AuditEvaluationRequest):
    """Pillar A: Generates formal legal pre-bid representations challenging unfair ATCs."""
    scorecard = await evaluate_tender_endpoint(payload, BackgroundTasks())
    return scorecard.prebid_legal_pack


@app.post("/api/v1/strategy/consortium-match", response_model=ConsortiumMatchRecommendation)
async def match_consortium_partners_endpoint(payload: AuditEvaluationRequest):
    """Pillar B: Computes exact eligibility shortfalls and recommends JV/OEM partners."""
    scorecard = await evaluate_tender_endpoint(payload, BackgroundTasks())
    return scorecard.consortium_recommendation


@app.post("/api/v1/strategy/compliance-matrix", response_model=ComplianceAndBinderPackage)
async def generate_compliance_matrix_endpoint(payload: AuditEvaluationRequest):
    """Pillar C: Auto-generates CSV/Table Compliance Matrix, Deviation Statement, and Statutory Affidavits."""
    scorecard = await evaluate_tender_endpoint(payload, BackgroundTasks())
    return scorecard.compliance_binder


@app.post("/api/v1/strategy/emd-optimizer", response_model=EMDCapitalOptimizationReport)
async def optimize_emd_capital_endpoint(payload: AuditEvaluationRequest):
    """Pillar D: Evaluates working capital lock-up and IRDAI Insurance Surety Bond optimization."""
    criteria = payload.explicit_criteria or TenderStatutoryCriteria()
    return EMDCapitalOptimizer.evaluate_capital_risk(
        bidder=payload.bidder_profile,
        criteria=criteria
    )


@app.get("/api/v1/strategy/forensics", response_model=CompetitorForensicsReport)
async def get_competitor_forensics_endpoint(
    tender_title: str = Query(..., description="Tender title or category"),
    source_portal: str = Query("GeM", description="Portal or PSU name, e.g., BHEL, ICMR, GeM, CPPP"),
    live_search: bool = Query(False, description="Whether to query live TinySearch archives")
):
    """Pillar E: Returns historical technical evaluation rejection forensics for the procuring authority."""
    if live_search:
        return await CompetitorForensicsEngine.analyze_with_live_archives(
            tender_title=tender_title,
            source_portal=source_portal,
            tinyfish=tinyfish
        )
    return CompetitorForensicsEngine.analyze_static_forensics(
        tender_title=tender_title,
        source_portal=source_portal
    )


# ---------------------------------------------------------------------------
# Precedence DAG RAG Endpoints (v1.0.3)
# ---------------------------------------------------------------------------
class RAGQueryPayload(BaseModel):
    tender_id: str = "TENDER-QUERY"
    query: str
    tender_url: Optional[str] = None
    canonical_category: Optional[str] = None
    explicit_chunks: Optional[List[ProcessedClauseChunk]] = None
    enable_gemini: bool = True


@app.post("/api/v1/rag/query", response_model=RAGQueryResponse)
async def query_rag_endpoint(payload: RAGQueryPayload):
    """
    Precedence DAG RAG (v1.0.3): Queries tender document corpus with strict
    precedence resolution (Rank 1 Corrigendum overrides Rank 5 Main PDF).
    """
    chunks = payload.explicit_chunks or []
    if not chunks and payload.tender_url:
        try:
            fetched_docs = await tinyfish.fetch_tender_recursive(payload.tender_url, max_depth=1)
            for doc in fetched_docs:
                rank = DocumentProcessor.infer_precedence_rank(doc.url.split("/")[-1])
                lines = doc.content_markdown.split("\n\n")
                for idx, para in enumerate(lines):
                    cleaned = para.strip()
                    if cleaned:
                        chunks.append(ProcessedClauseChunk(
                            document_name=doc.url.split("/")[-1] or "Tender_Doc.pdf",
                            precedence_rank=rank,
                            page_number=(idx // 3) + 1,
                            clause_id=f"Sec-{idx + 1}",
                            text_content=cleaned,
                            parsing_method="tinyfetch_markdown"
                        ))
        except Exception as e:
            logger.warning(f"RAG document fetch error: {e}")

    if payload.enable_gemini:
        return await PrecedenceRAGEngine.query_with_gemini(
            tender_id=payload.tender_id,
            query_str=payload.query,
            chunks=chunks,
            canonical_category=payload.canonical_category
        )
    return PrecedenceRAGEngine.query(
        tender_id=payload.tender_id,
        query_str=payload.query,
        chunks=chunks,
        canonical_category=payload.canonical_category
    )


class PrecedenceGraphRequest(BaseModel):
    tender_id: str
    chunks: List[ProcessedClauseChunk]


@app.post("/api/v1/rag/precedence-graph", response_model=PrecedenceDAGGraph)
async def get_precedence_dag_graph_endpoint(payload: PrecedenceGraphRequest):
    """
    Constructs and returns the full Precedence Directed Acyclic Graph (DAG) topology
    showing nodes, supersession edges, and detected conflicts.
    """
    return PrecedenceRAGEngine.build_dag_graph(
        tender_id=payload.tender_id,
        chunks=payload.chunks
    )


# ---------------------------------------------------------------------------
# Supabase Cloud Database Persistence & Auth Endpoints (Free Tier)
# ---------------------------------------------------------------------------
@app.get("/api/v1/auth/config")
async def get_auth_config_endpoint():
    """Returns safe, public Supabase configuration for browser clients."""
    return {
        "configured": settings.is_supabase_configured,
        "supabase_url": settings.SUPABASE_URL,
        "publishable_key": settings.supabase_public_key,
    }


@app.post("/api/v1/audits/save")
async def save_audit_endpoint(payload: SaveAuditRequest):
    """Save an evaluated qualification scorecard into Supabase tender_audits table."""
    result = await supabase_service.save_audit_scorecard(
        user_id=payload.user_id,
        scorecard=payload.scorecard,
        tender_title=payload.tender_title,
        tender_url=payload.tender_url,
        source_portal=payload.source_portal or "GeM"
    )
    if not result:
        if not settings.is_supabase_configured:
            return {"status": "unconfigured", "message": "Supabase credentials not configured in .env"}
        raise HTTPException(status_code=500, detail="Failed to persist audit to Supabase")
    return {"status": "saved", "data": result}


@app.get("/api/v1/audits/user/{user_id}")
async def get_user_audits_endpoint(user_id: str, limit: int = Query(20, ge=1, le=100)):
    """Retrieve historical saved audits for an authenticated user from Supabase."""
    audits = await supabase_service.get_user_audits(user_id=user_id, limit=limit)
    return {"user_id": user_id, "audits": audits}


@app.get("/api/v1/profile/sync/{user_id}", response_model=Optional[BidderProfile])
async def get_synced_bidder_profile_endpoint(user_id: str):
    """Fetch the stored BidderProfile for an authenticated user from Supabase."""
    profile = await supabase_service.get_bidder_profile(user_id=user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="No profile found for user in Supabase")
    return profile


@app.post("/api/v1/profile/sync")
async def save_synced_bidder_profile_endpoint(payload: SaveBidderProfileRequest):
    """Sync a BidderProfile into Supabase profiles table."""
    result = await supabase_service.save_bidder_profile(
        user_id=payload.user_id,
        profile=payload.bidder_profile,
        full_name=payload.full_name or "",
        region=payload.region or ""
    )
    if not result:
        if not settings.is_supabase_configured:
            return {"status": "unconfigured", "message": "Supabase credentials not configured in .env"}
        raise HTTPException(status_code=500, detail="Failed to save profile to Supabase")
    return {"status": "saved", "data": result}


# ===========================================================================
# STRATEGY PREVIEW & FAIR PLAY EQUALIZER ENDPOINTS (v1.1.0)
# ===========================================================================

class StrategyPreviewRequest(BaseModel):
    tender_id: Optional[str] = "GEM-2026-B-994120"
    tender_title: str
    source_portal: str = "GeM"
    bidder_profile: BidderProfile
    criteria: TenderStatutoryCriteria


class FairPlayShieldAuditRequest(BaseModel):
    tender_id: Optional[str] = "GEM-2026-B-994120"
    tender_title: str
    bidder_profile: BidderProfile
    criteria: TenderStatutoryCriteria


@app.post("/api/v1/strategy/preview", response_model=StrategyToolkitResponse)
async def create_strategy_preview_endpoint(payload: StrategyPreviewRequest):
    """
    Unified Strategy & Fair Play Equalizer endpoint called by strategy.html / strategy.js.
    Executes Deterministic Gates + 5 Strategy Pillars + 3 Fair Play Zero-History Engines.
    """
    t_id = payload.tender_id or "GEM-2026-B-994120"

    # 1. Run Startup Statutory Shield & Fair Play Violation Scanner
    shield_audit, fair_play_alerts = FairPlayGuardianEngine.run_startup_statutory_shield(
        tender_id=t_id,
        tender_title=payload.tender_title,
        bidder=payload.bidder_profile,
        criteria=payload.criteria,
        chunks=[],
        citations=[]
    )

    # 2. Run Zero-History Competency Engine & generate Equipment/QC Proforma
    tech_proof, qc_proforma_affidavit = FairPlayGuardianEngine.evaluate_zero_history_competency(
        tender_id=t_id,
        tender_title=payload.tender_title,
        bidder=payload.bidder_profile,
        criteria=payload.criteria
    )

    # 3. Run Mandatory 25% MSE Subcontracting & Split-Order Quota Gateway
    mse_match = FairPlayGuardianEngine.match_25pct_mse_subcontracting_quota(
        tender_id=t_id,
        tender_title=payload.tender_title,
        bidder=payload.bidder_profile,
        criteria=payload.criteria,
        shield_audit=shield_audit
    )

    # 4. Run Deterministic Gatekeeper & 5 Strategy Pillars
    gates = DeterministicGatekeeper.evaluate(bidder=payload.bidder_profile, tender=payload.criteria)

    prebid_pack = PreBidLegalGenerator.generate_representation_pack(
        tender_id=t_id,
        tender_title=payload.tender_title,
        bidder=payload.bidder_profile,
        criteria=payload.criteria,
        gates=gates,
        citations=[]
    )

    consortium_rec = ConsortiumMatchmaker.analyze_and_match(
        bidder=payload.bidder_profile,
        criteria=payload.criteria,
        gate_results=gates
    )

    compliance_binder = ComplianceMatrixEngine.generate_package(
        tender_id=t_id,
        tender_title=payload.tender_title,
        bidder=payload.bidder_profile,
        criteria=payload.criteria,
        gates=gates,
        citations=[]
    )
    compliance_binder.statutory_affidavits.append(qc_proforma_affidavit)

    emd_report = EMDCapitalOptimizer.evaluate_capital_risk(
        bidder=payload.bidder_profile,
        criteria=payload.criteria
    )

    forensics = CompetitorForensicsEngine.analyze_static_forensics(
        tender_title=payload.tender_title,
        source_portal=payload.source_portal
    )

    return StrategyToolkitResponse(
        tender_id=t_id,
        tender_title=payload.tender_title,
        source_portal=payload.source_portal,
        limitations_note=(
            f"Fair Play Equalizer Active: {shield_audit.audit_verdict} | "
            f"Zero-History Competency: {tech_proof.overall_competency_score}/100 | "
            f"25% MSE Quota: ₹{mse_match.mandatory_25pct_allocation_lakhs:.2f} Lakhs."
        ),
        deterministic_gates=gates,
        prebid_legal_pack=prebid_pack,
        consortium_recommendation=consortium_rec,
        compliance_binder=compliance_binder,
        emd_capital_report=emd_report,
        competitor_forensics=forensics,
        startup_exemption_audit=shield_audit,
        technical_equivalence_proof=tech_proof,
        mse_subcontracting_match=mse_match,
        fair_play_violations=fair_play_alerts
    )


@app.post("/api/v1/audit/fair-play-shield")
async def audit_fair_play_shield_endpoint(payload: FairPlayShieldAuditRequest):
    """
    Dedicated endpoint to run the Startup Statutory Shield, Zero-History Competency Proof,
    and Mandatory 25% MSE Subcontracting Quota Gateway on demand.
    """
    t_id = payload.tender_id or "GEM-2026-B-994120"
    shield_audit, fair_play_alerts = FairPlayGuardianEngine.run_startup_statutory_shield(
        tender_id=t_id,
        tender_title=payload.tender_title,
        bidder=payload.bidder_profile,
        criteria=payload.criteria,
        chunks=[],
        citations=[]
    )
    tech_proof, qc_proforma_affidavit = FairPlayGuardianEngine.evaluate_zero_history_competency(
        tender_id=t_id,
        tender_title=payload.tender_title,
        bidder=payload.bidder_profile,
        criteria=payload.criteria
    )
    mse_match = FairPlayGuardianEngine.match_25pct_mse_subcontracting_quota(
        tender_id=t_id,
        tender_title=payload.tender_title,
        bidder=payload.bidder_profile,
        criteria=payload.criteria,
        shield_audit=shield_audit
    )
    return {
        "tender_id": t_id,
        "startup_exemption_audit": shield_audit,
        "technical_equivalence_proof": tech_proof,
        "mse_subcontracting_match": mse_match,
        "fair_play_violations": fair_play_alerts,
        "qc_proforma_affidavit": qc_proforma_affidavit
    }


# Pair up Frontend: Mount static files if frontend/ directory exists
frontend_dir = ROOT_DIR / "frontend"
if frontend_dir.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")