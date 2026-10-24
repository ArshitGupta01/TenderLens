"""
TenderLens - Gemini Clause & Conflict Auditor Tests
===================================================
Tests gemini-3.8-flash integration for semantic clause conflict detection,
statutory exemption revocation identification, and async evaluation synthesis.
"""

import pytest
from backend.config import settings
from contracts.schema import BidderProfile
from backend.services.document_processor import ProcessedClauseChunk
from backend.engine.qualification_engine import QualificationEngine


@pytest.mark.asyncio
async def test_gemini_model_configuration():
    """Verify that GEMINI_MODEL is set to gemini-3.8-flash."""
    assert settings.GEMINI_MODEL == "gemini-3.8-flash"


@pytest.mark.asyncio
async def test_gemini_clause_conflict_live_or_fallback():
    """
    Tests semantic clause auditing via gemini-3.8-flash.
    If GEMINI_API_KEY is available, tests live conflict detection.
    """
    bidder = BidderProfile(
        company_name="Apex Tech India Pvt Ltd",
        entity_type="PRIVATE_LIMITED",
        is_msme_registered=True,
        msme_category="MICRO",
        is_startup=True,
        turnover_year_1_lakhs=30.0,
        turnover_year_2_lakhs=35.0,
        turnover_year_3_lakhs=40.0,
        years_in_business=3,
        local_content_percentage=55.0,
        held_certifications=["ISO-9001"]
    )

    # Chunks containing an ambiguous ATC clause attempting to revoke MSME relaxation
    chunks = [
        ProcessedClauseChunk(
            document_name="Buyer_ATC_Revocation.pdf",
            precedence_rank=3,
            page_number=1,
            clause_id="ATC-Clause-4.1",
            text_content="Buyer uploaded ATC: In deviation from standard GeM policy, no exemption in turnover or past experience shall be allowed for MSME or Startup bidders for this procurement.",
            parsing_method="pymupdf_fast"
        )
    ]

    citations = await QualificationEngine.analyze_clauses_with_gemini(
        chunks=chunks,
        bidder=bidder,
        model=settings.GEMINI_MODEL
    )

    if settings.GEMINI_API_KEY:
        # Live test with active key
        assert isinstance(citations, list)
        if citations:
            assert "gemini-3.8-flash" in citations[0].document_name.lower()
            assert citations[0].status == "AMBIGUOUS_MANUAL_REVIEW"
            assert len(citations[0].verbatim_text) > 0
    else:
        # Graceful fallback when key is not provided
        assert citations == []


@pytest.mark.asyncio
async def test_evaluate_tender_async_with_gemini():
    """
    Tests full async tender evaluation incorporating Gemini clause analysis.
    """
    bidder = BidderProfile(
        company_name="Beta Solutions LLP",
        entity_type="LLP",
        is_msme_registered=True,
        msme_category="SMALL",
        is_startup=False,
        turnover_year_1_lakhs=120.0,
        turnover_year_2_lakhs=150.0,
        turnover_year_3_lakhs=180.0,
        years_in_business=5,
        local_content_percentage=60.0,
        held_certifications=["ISO-9001", "BIS"]
    )

    chunks = [
        ProcessedClauseChunk(
            document_name="Main_Tender.pdf",
            precedence_rank=5,
            page_number=1,
            clause_id="Cl-1",
            text_content="Average annual turnover in last 3 financial years shall be Rs 100 Lakhs. Experience of 3 years required. EMD Rs 50000.",
            parsing_method="pymupdf_fast"
        )
    ]

    scorecard = await QualificationEngine.evaluate_tender_async(
        tender_id="BID-TEST-GEMINI-01",
        tender_title="Supply of IT Peripherals to State Informatics",
        source_portal="GeM",
        bidder_profile=bidder,
        chunks=chunks,
        enable_gemini_analysis=True
    )

    assert scorecard.tender_id == "BID-TEST-GEMINI-01"
    assert scorecard.recommendation in ["STRONG_BID", "CONDITIONAL_BID"]
    assert scorecard.score >= 3.0
    assert len(scorecard.deterministic_gates) == 6
