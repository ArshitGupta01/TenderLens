"""
TenderLens - Fair Play Guardian & Zero-History Equalizer Tests (v1.1.0)
========================================================================
Tests the 3 Hackathon-Winning Core Capabilities:
1. Startup Statutory Shield (GFR 173(i) & GeM GTC 4(xiii)(h) override)
2. Zero-History Competency Engine (4-Vector Technical Equivalence & QC Proforma)
3. Mandatory 25% MSE Subcontracting & Split-Order Quota Gateway (PPP-MSE Order 2012)
"""

import pytest
from contracts.schema import BidderProfile, LabTestReportItem
from backend.engine.deterministic_gatekeeper import (
    DeterministicGatekeeper,
    TenderStatutoryCriteria
)
from backend.engine.fair_play_guardian import FairPlayGuardianEngine


def test_illegal_atc_revocation_overridden_by_shield():
    """
    Test 1: A zero-turnover DPIIT Startup facing an unlawful Buyer ATC revocation
    must receive ILLEGAL_ATC_REVOCATION_OVERRIDDEN_BY_SHIELD and pass Gate 1 and Gate 2.
    """
    startup = BidderProfile(
        company_name="AetherGrid Hardware Labs Pvt. Ltd.",
        entity_type="OEM",
        years_in_business=0,
        is_msme_registered=True,
        msme_category="MICRO",
        is_startup_recognized=True,
        dpiit_recognition_number="DIPP-STARTUP-REC-94182",
        turnover_year_1_lakhs=0.0,
        turnover_year_2_lakhs=0.0,
        turnover_year_3_lakhs=0.0,
        local_content_percentage=82.0,
        held_certifications=["ISO-9001", "BIS"]
    )

    tender = TenderStatutoryCriteria(
        min_annual_turnover_lakhs=200.0,
        min_experience_years=3,
        estimated_bid_value_lakhs=500.0,
        emd_amount_inr=1000000.0,
        is_turnover_exemption_revoked_by_atc=True,
        is_experience_exemption_revoked_by_atc=True,
        is_public_safety_or_security_exception=False
    )

    # 1. Run Statutory Shield Audit
    audit, alerts = FairPlayGuardianEngine.run_startup_statutory_shield(
        tender_id="GEM/2026/B/9941208",
        tender_title="Supply & Commissioning of Indigenous Smart LV Switchgear Panels",
        bidder=startup,
        criteria=tender
    )

    assert audit.statutory_shield_invoked is True
    assert audit.audit_verdict == "ILLEGAL_ATC_REVOCATION_OVERRIDDEN_BY_SHIELD"
    assert audit.turnover_waived_lakhs == 200.0
    assert audit.experience_waived_years == 3
    assert audit.emd_waived_inr == 1000000.0
    assert len(alerts) >= 1
    assert any(a.violation_type == "ULTRA_VIRES_STARTUP_MSE_REVOCATION" for a in alerts)

    # 2. Verify Gate 1 & Gate 2 pass via Statutory Shield in Deterministic Gatekeeper
    gates = DeterministicGatekeeper.evaluate(bidder=startup, tender=tender)
    turnover_gate = next(g for g in gates if g.rule_name == "3-Year Average Annual Turnover")
    exp_gate = next(g for g in gates if g.rule_name == "Experience & Past Performance")

    assert turnover_gate.passed is True
    assert turnover_gate.is_hard_disqualifier is False
    assert "STATUTORY SHIELD OVERRIDE" in turnover_gate.reason

    assert exp_gate.passed is True
    assert exp_gate.is_hard_disqualifier is False
    assert "STATUTORY SHIELD OVERRIDE" in exp_gate.reason


def test_zero_history_competency_proforma_generation():
    """
    Test 2: Zero-History Competency Engine proves technical equivalence via NABL lab reports
    and auto-generates the statutory 7-point Proforma for Equipment and Quality Control.
    """
    startup = BidderProfile(
        company_name="AetherGrid Hardware Labs Pvt. Ltd.",
        entity_type="OEM",
        years_in_business=0,
        is_msme_registered=True,
        msme_category="MICRO",
        is_startup_recognized=True,
        turnover_year_1_lakhs=0.0,
        turnover_year_2_lakhs=0.0,
        turnover_year_3_lakhs=0.0,
        local_content_percentage=82.0,
        held_certifications=["ISO-9001", "BIS", "NABL-Type-Test"],
        lab_test_reports=[
            LabTestReportItem(
                certificate_id="NABL-TC-2026-8841",
                issuing_agency="NABL Accredited Testing Lab",
                standard_tested="IS 13252 & IEC 60947-2 Type Test",
                product_or_model_covered="AetherGrid Series-A Switchgear",
                issue_date="2026-06-15",
                is_valid_and_active=True,
                parameter_match_score_pct=100.0
            )
        ],
        plant_and_machinery_valuation_lakhs=35.0,
        max_monthly_production_capacity_units=500,
        founder_domain_experience_years=5
    )

    tender = TenderStatutoryCriteria(
        min_annual_turnover_lakhs=200.0,
        min_experience_years=3,
        mandatory_certifications=["ISO-9001", "BIS"]
    )

    proof, affidavit = FairPlayGuardianEngine.evaluate_zero_history_competency(
        tender_id="GEM/2026/B/9941208",
        tender_title="Supply of Smart LV Switchgear Panels",
        bidder=startup,
        criteria=tender
    )

    assert proof.is_zero_history_bidder is True
    assert proof.overall_competency_score >= 75.0
    assert proof.qualifies_for_technical_equivalence is True
    assert proof.lab_and_standards_score == 40.0
    assert proof.plant_and_capacity_score == 25.0
    assert proof.ip_and_mii_content_score == 20.0
    assert proof.founder_pedigree_score == 15.0

    # Verify Statutory Affidavit Proforma
    assert affidavit.doc_code == "MOE_STARTUP_EQUIPMENT_QC_PROFORMA"
    assert "ANNEXURE-I: PROFORMA FOR EQUIPMENT AND QUALITY CONTROL" in affidavit.content_markdown
    assert "GFR 2017 Rule 173(i)" in affidavit.governing_statute
    assert "AetherGrid Hardware Labs Pvt. Ltd." in affidavit.content_markdown
    assert "Class-I Local Supplier" in affidavit.content_markdown


def test_25pct_mse_quota_calculation():
    """
    Test 3: Mandatory 25% MSE Subcontracting Quota Gateway calculates exact 25% reserve
    on a ₹500 Lakh tender (₹125.00 Lakhs) and pairs startup with Vindhya EPC.
    """
    startup = BidderProfile(
        company_name="AetherGrid Hardware Labs Pvt. Ltd.",
        entity_type="OEM",
        is_msme_registered=True,
        msme_category="MICRO",
        is_startup_recognized=True,
        turnover_year_1_lakhs=0.0,
        turnover_year_2_lakhs=0.0,
        turnover_year_3_lakhs=0.0,
        years_in_business=0,
        local_content_percentage=82.0
    )

    tender = TenderStatutoryCriteria(
        estimated_bid_value_lakhs=500.0,
        min_annual_turnover_lakhs=200.0,
        is_turnover_exemption_revoked_by_atc=True
    )

    audit, _ = FairPlayGuardianEngine.run_startup_statutory_shield(
        tender_id="GEM/2026/B/9941208",
        tender_title="EPC Grid Turnkey Package",
        bidder=startup,
        criteria=tender
    )

    mse_match = FairPlayGuardianEngine.match_25pct_mse_subcontracting_quota(
        tender_id="GEM/2026/B/9941208",
        tender_title="EPC Grid Turnkey Package",
        bidder=startup,
        criteria=tender,
        shield_audit=audit
    )

    assert mse_match.eligible_for_25pct_mse_quota is True
    assert mse_match.estimated_tender_value_lakhs == 500.0
    assert mse_match.mandatory_25pct_allocation_lakhs == 125.0
    assert mse_match.l1_plus_15pct_price_preference_eligible is True
    assert mse_match.matched_prime_epc_partner is not None
    assert "Vindhya EPC" in mse_match.matched_prime_epc_partner.company_name
    assert "TRIPARTITE MSE SUBCONTRACTING & 25% QUOTA ALLOCATION MoU" in mse_match.tripartite_mou_draft_markdown
    assert "₹125.00 Lakhs" in mse_match.tripartite_mou_draft_markdown