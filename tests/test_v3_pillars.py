"""
TenderLens v1.0.1 — Comprehensive Unit & Integration Tests for Pillars A–E
"""

import pytest
from contracts.schema import BidderProfile
from backend.services.document_processor import ProcessedClauseChunk
from backend.engine.deterministic_gatekeeper import TenderStatutoryCriteria
from backend.engine.qualification_engine import QualificationEngine


def make_sample_msme_bidder() -> BidderProfile:
    return BidderProfile(
        company_name="Apex Solar & Grid MSME Pvt Ltd",
        entity_type="System Integrator",
        is_msme_registered=True,
        msme_category="SMALL",
        is_startup_recognized=True,
        turnover_year_1_lakhs=80.0,
        turnover_year_2_lakhs=95.0,
        turnover_year_3_lakhs=125.0,  # Avg = 100 Lakhs (₹1 Cr)
        years_in_business=2,
        local_content_percentage=62.0,
        held_certifications=["ISO-9001"],
        past_similar_project_values_lakhs=[45.0, 55.0],
        available_emd_working_capital_inr=2000000.0,
        active_simultaneous_bids_count=4
    )


def test_pillar_a_prebid_legal_representation_on_msme_trap():
    """Verifies Pillar A auto-drafts a formal representation when Buyer ATC revokes MSME exemptions."""
    bidder = make_sample_msme_bidder()
    chunks = [
        ProcessedClauseChunk(
            document_name="Buyer_ATC_Override.pdf",
            precedence_rank=3,
            page_number=4,
            clause_id="ATC-4.2",
            text_content="Minimum annual turnover of Rs. 500 Lakhs required. No exemption to MSME or Startup allowed. Only make allowed: ProprietaryBrandX."
        )
    ]

    scorecard = QualificationEngine.evaluate_tender(
        tender_id="GEM/2026/B/900123",
        tender_title="Supply of BHEL High Voltage Substation Panels",
        source_portal="GeM",
        bidder_profile=bidder,
        chunks=chunks
    )

    assert scorecard.prebid_legal_pack is not None
    assert scorecard.prebid_legal_pack.total_challenges >= 2
    categories = [r.violation_category for r in scorecard.prebid_legal_pack.representations]
    assert "ILLEGAL_MSME_EXEMPTION_REVOCATION" in categories
    assert "PROPRIETARY_BRAND_LOCK" in categories
    assert "F.20/2/2014-PPD" in scorecard.prebid_legal_pack.formal_letter_markdown


def test_pillar_b_consortium_matchmaker_bridges_turnover_and_cert_gap():
    """Verifies Pillar B detects exact ₹400L turnover shortfall & missing BIS cert and recommends JV partner."""
    bidder = make_sample_msme_bidder()
    criteria = TenderStatutoryCriteria(
        min_annual_turnover_lakhs=500.0,
        min_experience_years=5,
        is_turnover_exemption_revoked_by_atc=True,
        is_experience_exemption_revoked_by_atc=True,
        oem_authorization_mandatory=True,
        mandatory_certifications=["ISO-9001", "BIS"]
    )

    scorecard = QualificationEngine.evaluate_tender(
        tender_id="GEM/2026/B/900456",
        tender_title="Turnkey Transformer Installation",
        source_portal="GeM",
        bidder_profile=bidder,
        chunks=[],
        explicit_criteria=criteria
    )

    assert scorecard.recommendation == "RED_FLAG_NO_BID"
    rec = scorecard.consortium_recommendation
    assert rec is not None
    assert rec.has_shortfall is True
    gap_types = {g.shortfall_type for g in rec.identified_gaps}
    assert "TURNOVER_GAP" in gap_types
    assert "CERTIFICATION_GAP" in gap_types
    assert len(rec.recommended_partners) >= 1
    assert rec.post_consortium_recommendation == "STRONG_BID"


def test_pillar_c_compliance_matrix_csv_and_affidavits():
    """Verifies Pillar C exports valid CSV compliance matrix and statutory declarations."""
    bidder = make_sample_msme_bidder()
    criteria = TenderStatutoryCriteria(
        min_annual_turnover_lakhs=80.0,
        emd_amount_inr=150000.0,
        oem_authorization_mandatory=True
    )

    scorecard = QualificationEngine.evaluate_tender(
        tender_id="GEM/2026/B/900789",
        tender_title="ICMR Lab Equipment Procurement",
        source_portal="GeM",
        bidder_profile=bidder,
        chunks=[],
        explicit_criteria=criteria
    )

    binder = scorecard.compliance_binder
    assert binder is not None
    assert len(binder.compliance_rows) >= 6
    assert "Compliance Status" in binder.csv_export_string
    doc_codes = {a.doc_code for a in binder.statutory_affidavits}
    assert "GFR_170_BID_SECURITY" in doc_codes
    assert "DPIIT_MII_LOCAL_CONTENT" in doc_codes
    assert "GFR_144_XI_LAND_BORDER" in doc_codes
    assert "OEM_MAF_FORMAT" in doc_codes


def test_pillar_d_emd_capital_risk_and_surety_optimization():
    """Verifies Pillar D recommends Insurance Surety Bond for commercial bidders and Bid Security Declaration for MSMEs."""
    commercial_bidder = make_sample_msme_bidder()
    commercial_bidder.is_msme_registered = False
    commercial_bidder.is_startup_recognized = False

    criteria = TenderStatutoryCriteria(
        emd_amount_inr=500000.0,
        allow_insurance_surety_bond=True
    )

    scorecard = QualificationEngine.evaluate_tender(
        tender_id="CPPP/2026/BHEL/101",
        tender_title="BHEL Boiler Auxiliaries Supply",
        source_portal="BHEL",
        bidder_profile=commercial_bidder,
        chunks=[],
        explicit_criteria=criteria
    )

    emd = scorecard.emd_capital_report
    assert emd is not None
    assert emd.is_statutorily_exempt is False
    assert emd.recommended_instrument == "IRDAI_INSURANCE_SURETY_BOND"
    assert emd.effective_cash_lockup_inr < emd.emd_required_inr


def test_pillar_e_competitor_disqualification_forensics():
    """Verifies Pillar E identifies PSU-specific (BHEL & ICMR) historical rejection traps."""
    bidder = make_sample_msme_bidder()
    scorecard = QualificationEngine.evaluate_tender(
        tender_id="BHEL/2026/09",
        tender_title="BHEL High Voltage Transformer Supply",
        source_portal="BHEL",
        bidder_profile=bidder,
        chunks=[]
    )

    forensics = scorecard.competitor_forensics
    assert forensics is not None
    assert "BHEL" in forensics.target_authority
    assert len(forensics.historical_patterns) >= 2



def test_strategy_preview_endpoint():
    """Verifies POST /api/v1/strategy/preview returns full 5-Pillar StrategyToolkitResponse."""
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)
    bidder = make_sample_msme_bidder()
    payload = {
        "tender_id": "GEM/2026/B/909999",
        "tender_title": "BHEL 33kV Substation Switchgear & Relay Panels",
        "source_portal": "BHEL",
        "bidder_profile": bidder.model_dump(mode="json"),
        "criteria": {
            "min_annual_turnover_lakhs": 450.0,
            "min_experience_years": 5,
            "estimated_bid_value_lakhs": 300.0,
            "emd_amount_inr": 600000.0,
            "min_local_content_percentage": 50.0,
            "mandatory_certifications": ["ISO-9001", "BIS"],
            "oem_authorization_mandatory": True,
            "is_turnover_exemption_revoked_by_atc": True,
            "is_experience_exemption_revoked_by_atc": True,
            "proprietary_brand_lock_detected": True,
            "proprietary_brand_details": "Only Make Allowed: BrandX Switchgear"
        }
    }
    resp = client.post("/api/v1/strategy/preview", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["tender_id"] == "GEM/2026/B/909999"
    assert len(data["deterministic_gates"]) >= 6
    assert data["prebid_legal_pack"]["total_challenges"] >= 2
    assert data["consortium_recommendation"]["has_shortfall"] is True
    assert len(data["compliance_binder"]["compliance_rows"]) >= 6
    assert len(data["compliance_binder"]["statutory_affidavits"]) >= 3
    assert data["emd_capital_report"]["emd_required_inr"] == 600000.0
    assert len(data["competitor_forensics"]["historical_patterns"]) >= 2
    assert "limitations_note" in data
