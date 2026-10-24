"""
TenderLens - Test Suite: Precedence DAG RAG Engine (v1.0.3)
===========================================================
Tests:
1. Canonical attribute categorization (Turnover, EMD, Experience, MII, MAF, etc.)
2. Strict legal precedence override (Rank 1 Corrigendum supersedes Rank 5 Main PDF)
3. Audit trail preservation of superseded baseline terms
4. Conflict & Safe Uncertainty detection for contradictions at the same precedence rank
5. Precedence DAG Graph topology generation for visualization
6. FastAPI REST endpoints for RAG query and DAG graph
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.document_processor import ProcessedClauseChunk, BoundingBox
from backend.engine.precedence_rag_engine import PrecedenceRAGEngine
from contracts.schema import RAGPrecedenceCitation

client = TestClient(app)


def test_01_canonical_category_classification():
    """Verify regex classifier correctly identifies canonical procurement categories."""
    assert PrecedenceRAGEngine.classify_clause_category("The average annual turnover must be 50 Lakhs") == "TURNOVER"
    assert PrecedenceRAGEngine.classify_clause_category("Past experience of 3 years in similar works") == "EXPERIENCE"
    assert PrecedenceRAGEngine.classify_clause_category("Earnest money deposit (EMD) of Rs 100,000 required") == "EMD"
    assert PrecedenceRAGEngine.classify_clause_category("Make in India local content must be at least 50%") == "MII_LOCAL_CONTENT"
    assert PrecedenceRAGEngine.classify_clause_category("Manufacturer Authorization Form (MAF) is mandatory") == "OEM_MAF"
    assert PrecedenceRAGEngine.classify_clause_category("Valid ISO-9001 and BIS certification required") == "CERTIFICATIONS"
    assert PrecedenceRAGEngine.classify_clause_category("Liquidated damages of 0.5% per week of delay") == "LIQUIDATED_DAMAGES"
    assert PrecedenceRAGEngine.classify_clause_category("Disputes subject to arbitration in New Delhi") == "ARBITRATION"
    assert PrecedenceRAGEngine.classify_clause_category("General boilerplate instructions for bidding") == "GENERAL"


def test_02_precedence_dag_strict_override():
    """
    Core RAG Differentiator: Flat vector RAG fails by averaging or confusing clauses.
    Precedence DAG RAG strictly enforces Rank 1 Corrigendum > Rank 5 Main PDF.
    """
    chunks = [
        ProcessedClauseChunk(
            document_name="Main_Tender_Baseline.pdf",
            precedence_rank=5,
            page_number=4,
            clause_id="Cl-4.1",
            text_content="Baseline Requirement: Average annual turnover of the bidder shall be minimum Rs 50 Lakhs in the last 3 financial years.",
            parsing_method="pymupdf_fitz",
            bbox=BoundingBox(x0=50.0, y0=100.0, x1=500.0, y1=150.0)
        ),
        ProcessedClauseChunk(
            document_name="Corrigendum_2_Final.pdf",
            precedence_rank=1,
            page_number=1,
            clause_id="Corr-2.1",
            text_content="Corrigendum Amendment: In supersession of clause 4.1, the minimum average annual turnover is enhanced to Rs 150 Lakhs.",
            parsing_method="pymupdf_fitz",
            bbox=BoundingBox(x0=50.0, y0=80.0, x1=520.0, y1=130.0)
        )
    ]

    response = PrecedenceRAGEngine.query(
        tender_id="GEM-2026-DAG-01",
        query_str="What is the annual turnover requirement?",
        chunks=chunks
    )

    assert response.tender_id == "GEM-2026-DAG-01"
    assert response.winning_citation is not None
    # Winning citation MUST be from Corrigendum 2 (Rank 1)
    assert response.winning_citation.document_name == "Corrigendum_2_Final.pdf"
    assert response.winning_citation.precedence_rank == 1
    assert response.winning_citation.clause_id == "Corr-2.1"
    assert response.winning_citation.is_superseded is False

    # Precedence override must be flagged as applied
    assert response.precedence_applied is True

    # Audit trail must preserve the superseded baseline clause
    assert len(response.audit_trail) == 2
    baseline = next(c for c in response.audit_trail if c.document_name == "Main_Tender_Baseline.pdf")
    assert baseline.is_superseded is True
    assert "Corrigendum_2_Final.pdf" in baseline.superseded_by


def test_03_same_rank_conflict_safe_uncertainty():
    """
    Safe Uncertainty Rule: When two clauses at the same precedence rank conflict,
    the engine flags conflict_detected = True and creates a CONFLICTS_WITH edge.
    """
    chunks = [
        ProcessedClauseChunk(
            document_name="Buyer_ATC_Section_A.pdf",
            precedence_rank=3,
            page_number=2,
            clause_id="ATC-A-1",
            text_content="Buyer ATC Clause: MSME bidders are exempt from Earnest Money Deposit (EMD) under GFR Rule 170.",
            parsing_method="pymupdf_fitz"
        ),
        ProcessedClauseChunk(
            document_name="Buyer_ATC_Section_B.pdf",
            precedence_rank=3,
            page_number=5,
            clause_id="ATC-B-4",
            text_content="Buyer ATC Clause: No exemption from EMD shall be granted to any category of bidder for this bid.",
            parsing_method="pymupdf_fitz"
        )
    ]

    response = PrecedenceRAGEngine.query(
        tender_id="GEM-2026-CONFLICT",
        query_str="Is EMD exemption allowed for MSME?",
        chunks=chunks
    )

    assert response.conflict_detected is True
    assert "Safe Uncertainty" in response.answer


def test_04_precedence_dag_graph_generation():
    """Verify complete DAG topology creation with nodes and superseding edges."""
    chunks = [
        ProcessedClauseChunk(
            document_name="Main_Tender.pdf",
            precedence_rank=5,
            page_number=3,
            clause_id="Sec-3",
            text_content="Minimum past experience of 3 years required.",
            parsing_method="pymupdf_fitz"
        ),
        ProcessedClauseChunk(
            document_name="Corrigendum_1.pdf",
            precedence_rank=2,
            page_number=1,
            clause_id="Corr-1.1",
            text_content="Past experience requirement is revised to 5 years.",
            parsing_method="pymupdf_fitz"
        )
    ]

    graph = PrecedenceRAGEngine.build_dag_graph(
        tender_id="GEM-GRAPH-TEST",
        chunks=chunks
    )

    assert graph.tender_id == "GEM-GRAPH-TEST"
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    assert graph.edges[0].relation_type == "SUPERSEDES"
    assert graph.total_overrides == 1
    assert graph.detected_conflicts == 0


def test_05_fastapi_rag_endpoints():
    """Tests POST /api/v1/rag/query and POST /api/v1/rag/precedence-graph REST endpoints."""
    chunks_payload = [
        {
            "document_name": "Main_Bid.pdf",
            "precedence_rank": 5,
            "page_number": 2,
            "clause_id": "Cl-2",
            "text_content": "Make in India local content requirement: 20% minimum.",
            "parsing_method": "pymupdf_fitz"
        },
        {
            "document_name": "Corrigendum_1.pdf",
            "precedence_rank": 1,
            "page_number": 1,
            "clause_id": "Corr-1",
            "text_content": "Corrigendum Revision: Local content requirement is updated to minimum 50% (Class-I only).",
            "parsing_method": "pymupdf_fitz"
        }
    ]

    # Test Query Endpoint
    query_req = {
        "tender_id": "GEM-RAG-API-TEST",
        "query": "What is the Make in India local content threshold?",
        "explicit_chunks": chunks_payload,
        "enable_gemini": False
    }

    res = client.post("/api/v1/rag/query", json=query_req)
    assert res.status_code == 200
    data = res.json()

    assert data["tender_id"] == "GEM-RAG-API-TEST"
    assert data["winning_citation"]["document_name"] == "Corrigendum_1.pdf"
    assert data["winning_citation"]["precedence_rank"] == 1
    assert data["precedence_applied"] is True

    # Test Graph Endpoint
    graph_req = {
        "tender_id": "GEM-RAG-API-TEST",
        "chunks": chunks_payload
    }
    graph_res = client.post("/api/v1/rag/precedence-graph", json=graph_req)
    assert graph_res.status_code == 200
    graph_data = graph_res.json()
    assert len(graph_data["nodes"]) == 2
    assert len(graph_data["edges"]) == 1
    assert graph_data["edges"][0]["relation_type"] == "SUPERSEDES"
