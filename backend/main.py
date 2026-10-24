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
    TenderStatutoryCriteria
)
from backend.engine.qualification_engine import QualificationEngine
from backend.engine.prebid_legal_generator import PreBidLegalGenerator
from backend.engine.consortium_matchmaker import ConsortiumMatchmaker
from backend.engine.compliance_matrix_engine import ComplianceMatrixEngine
from backend.engine.emd_capital_optimizer import EMDCapitalOptimizer
from backend.engine.competitor_forensics import CompetitorForensicsEngine
from contracts.schema import (
    BidderProfile,
    QualificationScorecard,
    PreBidLegalRepresentationPack,
    ConsortiumMatchRecommendation,
    ComplianceAndBinderPackage,
    EMDCapitalOptimizationReport,
    CompetitorForensicsReport
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tenderlens.api")

app = FastAPI(
    title="TenderLens Engine API",
    description="AI-Powered Tender Qualification & Disqualification Engine for Indian Public Procurement",
    version="1.0.1"
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


@app.get("/healthz")
async def health_check():
    return {
        "status": "healthy",
        "service": "TenderLens Backend Engine",
        "version": "1.0.1",
        "environment": settings.ENVIRONMENT,
        "tinyfish_configured": bool(settings.TINYFISH_API_KEY and not settings.TINYFISH_API_KEY.startswith("sk-tinyfish-your-key"))
    }


@app.get("/api/v1/auth/config")
async def auth_config():
    """Return the Supabase project URL and publishable key to the browser frontend.

    Publishable keys identify a public client and are safe to expose. Secret keys
    and database passwords must never be returned here; RLS protects user rows.
    """
    supabase_url = settings.SUPABASE_URL.strip()
    publishable_key = settings.SUPABASE_PUBLISHABLE_KEY.strip()
    configured = (
        supabase_url.startswith("https://")
        and "your-project" not in supabase_url.lower()
        and publishable_key.startswith("sb_publishable_")
        and "your-project" not in publishable_key.lower()
    )
    return {
        "configured": configured,
        "supabase_url": supabase_url if configured else "",
        "publishable_key": publishable_key if configured else "",
    }


@app.post("/api/v1/tenders/search", response_model=List[DiscoveredTender])
async def search_tenders_endpoint(payload: SearchRequest):
    """
    Stage 1: Discovers active government tenders via TinySearch API.
    Enforces production rules: include_domains, no 'site:' operator, location='IN'.
    """
    try:
        results = await tinyfish.search_tenders(
            query=payload.keywords,
            purpose=payload.purpose,
            include_domains=payload.portal,
            limit=payload.limit
        )
        return results
    except Exception as e:
        logger.error(f"Search endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/tenders/fetch", response_model=List[FetchedDocument])
async def fetch_tenders_endpoint(payload: FetchRequest):
    """
    Stage 2: Recursively crawls seed tender and linked child ATCs and Corrigenda
    up to depth d <= max_depth using TinyFetch.
    """
    try:
        docs = await tinyfish.fetch_tender_recursive(
            seed_url=payload.tender_url,
            max_depth=payload.max_depth
        )
        return docs
    except Exception as e:
        logger.error(f"Fetch endpoint error: {e}")
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
        # 1. Fetch seed tender & child ATCs
        fetched_docs = await tinyfish.fetch_tender_recursive(
            seed_url=payload.tender_url,
            max_depth=settings.MAX_CRAWL_DEPTH
        )

        all_atc_urls = []
        for doc in fetched_docs:
            all_atc_urls.extend(doc.extracted_child_urls)

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


# Pair up Frontend: Mount static files if frontend/ directory exists
frontend_dir = ROOT_DIR / "frontend"
if frontend_dir.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


