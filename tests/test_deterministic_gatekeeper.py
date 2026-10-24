"""
TenderLens - Test Suite: Deterministic Gatekeeper & Qualification Engine
========================================================================
Validates pure-Python statutory gates and Precedence DAG synthesis.
"""

from contracts.schema import BidderProfile
from backend.engine.deterministic_gatekeeper import (
    DeterministicGatekeeper,
    TenderStatutoryCriteria
)
from backend.engine.qualification_engine import QualificationEngine


def test_turnover_direct_pass():
    """Bidder whose 3-year average turnover exceeds the threshold should pass directly."""
    bidder = BidderProfile(
        company_name="Apex Power Systems Pvt Ltd",
        entity_type="OEM",
        is_msme_registered=False,
        turnover_year_1_lakhs=450.0,
        turnover_year_2_lakhs=500.0,
        turnover_year_3_lakhs=550.0,
        years_in_business=6,
        local_content_percentage=65.0,
        held_certifications=["ISO-9001", "BIS"]
    )
    tender = TenderStatutoryCriteria(
        min_annual_turnover_lakhs=400.0,
        min_experience_years=3,
        emd_amount_inr=50000.0,
        min_local_content_percentage=50.0,
        mandatory_certifications=["ISO-9001"]
    )

    results = DeterministicGatekeeper.evaluate(bidder, tender)
    turnover_gate = next(r for r in results if r.rule_name == "3-Year Average Annual Turnover")

    assert turnover_gate.passed is True
    assert turnover_gate.is_hard_disqualifier is False
    assert "meets or exceeds" in turnover_gate.reason


def test_msme_turnover_exemption_pass():
    """MSME bidder below threshold should pass via Public Procurement Policy 2012."""
    bidder = BidderProfile(
        company_name="Vikas Micro Transformers",
        entity_type="Manufacturer",
        is_msme_registered=True,
        msme_category="MICRO",
        turnover_year_1_lakhs=25.0,
        turnover_year_2_lakhs=30.0,
        turnover_year_3_lakhs=35.0,  # Avg 30 Lakhs
        years_in_business=4,
        local_content_percentage=70.0,
        held_certifications=["ISO-9001"]
    )
    tender = TenderStatutoryCriteria(
        min_annual_turnover_lakhs=100.0,  # Threshold is 100 Lakhs
        min_experience_years=3,
        msme_turnover_relaxation_allowed=True,
        is_turnover_exemption_revoked_by_atc=False
    )

    results = DeterministicGatekeeper.evaluate(bidder, tender)
    turnover_gate = next(r for r in results if r.rule_name == "3-Year Average Annual Turnover")

    assert turnover_gate.passed is True
    assert "PPP-2012" in turnover_gate.reason
    assert "relaxation granted" in turnover_gate.reason.lower()


def test_atc_revocation_disqualifier():
    """When Buyer ATC explicitly revokes MSME relaxation, bidder MUST be disqualified."""
    bidder = BidderProfile(
        company_name="Vikas Micro Transformers",
        entity_type="Manufacturer",
        is_msme_registered=True,
        msme_category="MICRO",
        turnover_year_1_lakhs=25.0,
        turnover_year_2_lakhs=30.0,
        turnover_year_3_lakhs=35.0,  # Avg 30 Lakhs
        years_in_business=4,
        local_content_percentage=70.0,
        held_certifications=[]
    )
    tender = TenderStatutoryCriteria(
        min_annual_turnover_lakhs=100.0,
        is_turnover_exemption_revoked_by_atc=True  # Buyer ATC override!
    )

    results = DeterministicGatekeeper.evaluate(bidder, tender)
    turnover_gate = next(r for r in results if r.rule_name == "3-Year Average Annual Turnover")

    assert turnover_gate.passed is False
    assert turnover_gate.is_hard_disqualifier is True
    assert "CRITICAL DISQUALIFIER" in turnover_gate.reason


def test_emd_exemption_rule_170():
    """Registered MSME / Startup is exempt from EMD under GFR Rule 170(i)."""
    msme_bidder = BidderProfile(
        company_name="Small Tech LLP",
        entity_type="OEM",
        is_msme_registered=True,
        turnover_year_1_lakhs=50.0,
        turnover_year_2_lakhs=50.0,
        turnover_year_3_lakhs=50.0,
        years_in_business=2,
        local_content_percentage=50.0,
        held_certifications=[]
    )
    tender = TenderStatutoryCriteria(emd_amount_inr=250000.0)

    results = DeterministicGatekeeper.evaluate(msme_bidder, tender)
    emd_gate = next(r for r in results if r.rule_name == "Earnest Money Deposit (EMD)")

    assert "Exempt from ₹250,000.00 EMD" in emd_gate.reason
    assert "GFR Rule 170(i)" in emd_gate.reason


def test_missing_mandatory_certification():
    """Missing mandatory certificates must trigger a hard disqualification."""
    bidder = BidderProfile(
        company_name="Solar Solutions India",
        entity_type="OEM",
        turnover_year_1_lakhs=200.0,
        turnover_year_2_lakhs=200.0,
        turnover_year_3_lakhs=200.0,
        years_in_business=5,
        local_content_percentage=60.0,
        held_certifications=["ISO-9001"]  # Missing BIS
    )
    tender = TenderStatutoryCriteria(
        mandatory_certifications=["ISO-9001", "BIS"]
    )

    results = DeterministicGatekeeper.evaluate(bidder, tender)
    cert_gate = next(r for r in results if r.rule_name == "Mandatory Certifications")

    assert cert_gate.passed is False
    assert cert_gate.is_hard_disqualifier is True
    assert "Missing 1 required certification(s): BIS" in cert_gate.reason


def test_scorecard_strong_bid_synthesis():
    """A qualified bidder receives STRONG_BID recommendation with score >= 4.0."""
    bidder = BidderProfile(
        company_name="Alpha Tech",
        entity_type="OEM",
        is_msme_registered=True,
        turnover_year_1_lakhs=300.0,
        turnover_year_2_lakhs=300.0,
        turnover_year_3_lakhs=300.0,
        years_in_business=5,
        local_content_percentage=80.0,
        held_certifications=["ISO-9001", "BIS"]
    )
    criteria = TenderStatutoryCriteria(
        min_annual_turnover_lakhs=200.0,
        min_experience_years=3,
        emd_amount_inr=100000.0,
        mandatory_certifications=["ISO-9001"],
        min_local_content_percentage=50.0
    )

    scorecard = QualificationEngine.evaluate_tender(
        tender_id="GEM-2026-B-9988",
        tender_title="Supply of Smart Energy Meters",
        source_portal="GeM",
        bidder_profile=bidder,
        chunks=[],
        explicit_criteria=criteria
    )

    assert scorecard.recommendation == "STRONG_BID"
    assert scorecard.score >= 4.0
    assert len(scorecard.deterministic_gates) == 6
