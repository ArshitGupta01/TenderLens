"""
TenderLens - Real End-to-End Pipeline & Edge Case Test Suite
===========================================================
Executes a real test of all TenderLens components:
1. Live TinyFish Search API (Free tier: $0.00 cost, preserving $5 credits)
2. Document Intelligence & Precedence DAG Rank Assignment
3. Deterministic Gatekeeper across 4 critical Indian procurement edge cases:
   - Case A: MSME Turnover Relaxation under PPP-2012 / GFR Rule 173(i)
   - Case B: The Buyer ATC Revocation Disqualification Trap
   - Case C: Make in India (MII) Class-I vs Class-II Disqualification
   - Case D: GFR 170 EMD Exemption vs Mandatory Deposit
4. Full QualificationEngine Scorecard Synthesis
5. Live FastAPI Endpoint Verification (/api/v1/audit/evaluate)
"""

import asyncio
from fastapi.testclient import TestClient

from backend.services.tinyfish_service import TinyFishService
from backend.engine.deterministic_gatekeeper import (
    DeterministicGatekeeper,
    TenderStatutoryCriteria
)
from backend.engine.qualification_engine import QualificationEngine
from backend.main import app
from contracts.schema import BidderProfile


def test_01_live_tinyfish_search_zero_cost():
    """Verify live search across Indian portals via TinySearch ($0.00 cost)."""
    svc = TinyFishService()
    results = asyncio.run(svc.search_tenders(
        query="rooftop solar panels",
        purpose="Find active GeM tenders for solar installation to verify eligibility",
        include_domains="gem.gov.in",
        limit=2
    ))

    # Assert search returned live Indian tender specifications
    assert len(results) > 0, "TinySearch should return at least 1 live tender"
    first = results[0]
    assert first.url.startswith("http"), "Discovered tender must have valid URL"
    assert "gem.gov.in" in first.url or "gem" in first.title.lower() or len(first.snippet) > 0


def test_02_edge_case_msme_relaxation_pass():
    """
    Edge Case 1: MSME Turnover Relaxation (PPP-2012 / GFR 173(i)).
    Bidder has ₹30 Lakhs avg turnover vs ₹100 Lakhs requirement.
    Since bidder is a registered Micro enterprise, turnover gate MUST pass.
    """
    bidder = BidderProfile(
        company_name="Shree Ram Micro Transformers",
        entity_type="Manufacturer",
        is_msme_registered=True,
        msme_category="MICRO",
        is_startup_recognized=False,
        turnover_year_1_lakhs=25.0,
        turnover_year_2_lakhs=30.0,
        turnover_year_3_lakhs=35.0,  # Avg 30 Lakhs
        years_in_business=4,
        local_content_percentage=75.0,
        held_certifications=["ISO-9001", "BIS"]
    )
    tender = TenderStatutoryCriteria(
        min_annual_turnover_lakhs=100.0,
        min_experience_years=3,
        emd_amount_inr=50000.0,
        msme_turnover_relaxation_allowed=True,
        is_turnover_exemption_revoked_by_atc=False
    )

    results = DeterministicGatekeeper.evaluate(bidder, tender)
    turnover_gate = next(r for r in results if r.rule_name == "3-Year Average Annual Turnover")

    assert turnover_gate.passed is True
    assert turnover_gate.is_hard_disqualifier is False
    assert "PPP-2012" in turnover_gate.reason


def test_03_edge_case_buyer_atc_revocation_trap():
    """
    Edge Case 2: The Buyer ATC Disqualification Trap.
    Same MSME bidder, but Buyer ATC explicitly revokes turnover relaxation.
    The Precedence DAG must override baseline and trigger RED FLAG.
    """
    bidder = BidderProfile(
        company_name="Shree Ram Micro Transformers",
        entity_type="Manufacturer",
        is_msme_registered=True,
        msme_category="MICRO",
        turnover_year_1_lakhs=25.0,
        turnover_year_2_lakhs=30.0,
        turnover_year_3_lakhs=35.0,
        years_in_business=4,
        local_content_percentage=75.0,
        held_certifications=["ISO-9001"]
    )
    tender = TenderStatutoryCriteria(
        min_annual_turnover_lakhs=100.0,
        is_turnover_exemption_revoked_by_atc=True  # Buyer ATC override!
    )

    scorecard = QualificationEngine.evaluate_tender(
        tender_id="GEM-TRAP-01",
        tender_title="Supply of Distribution Transformers",
        source_portal="GeM",
        bidder_profile=bidder,
        chunks=[],
        explicit_criteria=tender
    )

    assert scorecard.recommendation == "RED_FLAG_NO_BID"
    assert scorecard.score <= 2.0
    assert any(g.rule_name == "3-Year Average Annual Turnover" and not g.passed for g in scorecard.deterministic_gates)


def test_04_edge_case_make_in_india_class_trap():
    """
    Edge Case 3: Make in India (DPIIT 2017) Local Content Trap.
    Tender restricts bidding strictly to Class-I (>=50%).
    Bidder has 40% local content (Class-II). Must fail.
    """
    bidder = BidderProfile(
        company_name="Global Component Importers LLP",
        entity_type="Reseller",
        is_msme_registered=False,
        turnover_year_1_lakhs=500.0,
        turnover_year_2_lakhs=500.0,
        turnover_year_3_lakhs=500.0,
        years_in_business=8,
        local_content_percentage=40.0,  # Class-II
        held_certifications=[]
    )
    tender = TenderStatutoryCriteria(
        min_local_content_percentage=50.0,
        allow_class_2_suppliers=False  # Only Class-I allowed
    )

    results = DeterministicGatekeeper.evaluate(bidder, tender)
    mii_gate = next(r for r in results if "Make in India" in r.rule_name)

    assert mii_gate.passed is False
    assert mii_gate.is_hard_disqualifier is True
    assert "fails the minimum 50.0% threshold" in mii_gate.reason


def test_05_edge_case_emd_exemption_rule_170():
    """
    Edge Case 4: GFR Rule 170(i) EMD Exemption vs Commercial Mandate.
    Registered MSME is exempt, while Commercial Bidder must deposit EMD.
    """
    msme_bidder = BidderProfile(
        company_name="Green Tech Micro",
        entity_type="OEM",
        is_msme_registered=True,
        turnover_year_1_lakhs=100.0,
        turnover_year_2_lakhs=100.0,
        turnover_year_3_lakhs=100.0,
        years_in_business=3,
        local_content_percentage=80.0,
        held_certifications=[]
    )
    commercial_bidder = BidderProfile(
        company_name="Mega Infra Corp",
        entity_type="EPC",
        is_msme_registered=False,
        turnover_year_1_lakhs=1000.0,
        turnover_year_2_lakhs=1000.0,
        turnover_year_3_lakhs=1000.0,
        years_in_business=10,
        local_content_percentage=80.0,
        held_certifications=[]
    )

    tender = TenderStatutoryCriteria(emd_amount_inr=350000.0)

    msme_res = DeterministicGatekeeper.evaluate(msme_bidder, tender)
    comm_res = DeterministicGatekeeper.evaluate(commercial_bidder, tender)

    msme_emd = next(r for r in msme_res if "EMD" in r.rule_name)
    comm_emd = next(r for r in comm_res if "EMD" in r.rule_name)

    assert "Exempt from ₹350,000.00 EMD" in msme_emd.reason
    assert "Mandatory EMD deposit required: ₹350,000.00" in comm_emd.reason


def test_06_fastapi_live_audit_evaluation():
    """Test full FastAPI REST endpoint with payload conforming to contracts/schema.py."""
    client = TestClient(app)
    payload = {
        "tender_id": "GEM-2026-B-LIVE-TEST",
        "tender_title": "Design, Supply & Erection of 11kV Substation",
        "tender_url": "https://gem.gov.in/tender/sample-substation",
        "source_portal": "GeM",
        "bidder_profile": {
            "company_name": "Haryana Electricals Pvt Ltd",
            "entity_type": "OEM",
            "is_msme_registered": True,
            "msme_category": "SMALL",
            "turnover_year_1_lakhs": 220.0,
            "turnover_year_2_lakhs": 240.0,
            "turnover_year_3_lakhs": 260.0,
            "years_in_business": 6,
            "local_content_percentage": 65.0,
            "held_certifications": ["ISO-9001", "BIS"]
        },
        "explicit_criteria": {
            "min_annual_turnover_lakhs": 200.0,
            "min_experience_years": 4,
            "emd_amount_inr": 100000.0,
            "min_local_content_percentage": 50.0,
            "mandatory_certifications": ["ISO-9001", "BIS"]
        }
    }

    response = client.post("/api/v1/audit/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["recommendation"] == "STRONG_BID"
    assert data["score"] >= 4.0
    assert len(data["deterministic_gates"]) == 6
    assert data["tender_id"] == "GEM-2026-B-LIVE-TEST"
