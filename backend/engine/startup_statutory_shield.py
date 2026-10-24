"""
TenderLens - Startup Statutory Shield Engine (v2.0.0)
=====================================================
THE HACKATHON DIFFERENTIATOR: India's first Zero-History-to-First-Win
procurement eligibility engine for DPIIT-recognized startups.

PROBLEM SOLVED:
  50,000+ DPIIT startups in India have ZERO financial history.
  Every tender requires "3-year turnover ≥ ₹X crore."
  Every other AI tool says ❌ NO BID.
  This engine says: "Here's the law that says you CAN bid."

STATUTORY FOUNDATION:
  - GFR 2017 Rule 173(i)   : MoF may relax prior turnover/experience for startups
  - DPIIT Notification 2019 : Recognized startups ≤ 10 yrs, < ₹100Cr turnover
  - MoF OM F.20/2/2014-PPD  : Buyers CANNOT revoke MSME exemptions without legal basis
  - PPP-MSE Order 2012 §4   : 25% of procurement ≥ ₹200L must go to MSEs as subcontract
  - GeM Startup Policy 2021  : Relaxed norms for startups on GeM portal

UNIQUE CAPABILITIES:
  1. Trust-tiered competency evidence scoring (NABL > STQC > IP > Incubator > GeM rating)
  2. ATC Override Risk detector (checks if buyer illegally blocked exemptions)
  3. Startup Runway Tender classifier (which live tenders are accessible to day-0 firms)
  4. MSE 25% Subcontracting Gateway (fallback pipeline when direct bid blocked)
  5. Auto-generates GFR 173(i) pre-bid legal letter challenging illegal turnover blocks
"""

import logging
from typing import List, Optional
from datetime import date

from contracts.schema import (
    BidderProfile,
    ZeroHistoryCompetencyProfile,
    ZeroHistoryCompetencySignal,
    MSESubcontractingOpportunity,
    StartupRunwayTender,
    StartupShieldReport,
    GateResult,
)
from backend.engine.deterministic_gatekeeper import TenderStatutoryCriteria

logger = logging.getLogger("tenderlens.startup_shield")

# ---------------------------------------------------------------------------
# Trust Tier Weights for Shield Strength Calculation
# ---------------------------------------------------------------------------
SIGNAL_TRUST_WEIGHTS = {
    "NABL_ACCREDITATION": 2.5,       # Tier 1 — Strongest (NABL is GoI accreditation body)
    "STQC_CERT":          2.5,       # Tier 1 — Strongest (MeitY quality certification)
    "BIS_CERTIFICATION":  2.0,       # Tier 1 — Strong (Bureau of Indian Standards)
    "IP_PATENT":          2.0,       # Tier 2 — High (proves technical capability)
    "DPIIT_RECOGNITION":  1.5,       # Tier 2 — High (core statutory basis)
    "GEM_SELLER_RATING":  1.0,       # Tier 2 — High (proves live GoI procurement track)
    "INCUBATOR_LETTER":   1.0,       # Tier 3 — Medium (IIT/NIT/NASSCOM backed)
    "POC_PILOT_LETTER":   0.75,      # Tier 3 — Medium (documented pilot with govt/PSU)
    "AWARD":              0.5,       # Tier 3 — Supportive (SIH, startup awards, etc.)
    "PILOT_PROJECT":      0.75,      # Tier 3 — Medium
}

# Statutory exemptions mapped to evidence types
EVIDENCE_TO_EXEMPTION = {
    "DPIIT_RECOGNITION": "GFR Rule 173(i) — Prior Turnover Criteria Waiver for DPIIT-Recognised Startups",
    "NABL_ACCREDITATION": "Technical Competency Certification (Alternative to Prior Experience — MoF OM F.20/2/2014-PPD)",
    "STQC_CERT": "MeitY Quality Certification — Proves Technical Competency Without Financial History",
    "BIS_CERTIFICATION": "BIS Product Certification — Statutory Quality Proof (BIS Act 2016)",
    "IP_PATENT": "Intellectual Property — Demonstrates Innovation Capacity (DPIIT IP Policy 2016)",
    "GEM_SELLER_RATING": "GeM Seller Track Record — Prior Govt Procurement Evidence (GeM Startup Policy 2021)",
    "INCUBATOR_LETTER": "Recognised Incubator Endorsement — Startup India Hub Network",
    "POC_PILOT_LETTER": "Government/PSU Pilot PoC — Alternative Experience Proof (GFR Rule 173(i))",
    "PILOT_PROJECT": "Documented Pilot Project — Alternative Prior Performance (GFR Rule 173(i))",
}

# PPP-MSE 2012 threshold: tenders above this require 25% MSE subcontracting
MSE_SUBCONTRACTING_TRIGGER_LAKHS = 200.0
MSE_MANDATORY_SUBCONTRACT_PCT = 0.25


class StartupStatutoryShield:
    """
    The Zero-History Procurement Enabler for DPIIT-Recognized Startups.

    Evaluates a bidder's competency profile against the tender's criteria and:
    1. Determines if statutory shield is applicable and at what strength
    2. Maps each piece of competency evidence to a specific statutory exemption
    3. Detects ATC Override Risk (illegal buyer revocation of exemptions)
    4. Generates the MSE 25% subcontracting opportunity as a fallback
    5. Produces a pre-bid legal representation letter invoking GFR 173(i)
    """

    @staticmethod
    def compute_shield_strength(
        competency: ZeroHistoryCompetencyProfile,
        is_msme_registered: bool,
        is_startup_recognized: bool,
    ) -> float:
        """
        Calculates the 0–10 Shield Strength Score.

        Score composition:
        - DPIIT recognition base: +1.5 points
        - MSME registration base: +1.0 points
        - Each competency signal: +trust_weight (capped at 10.0 total)
        - GeM seller rating bonus: up to +0.5
        - Pilot project bonus: +0.25 per pilot (max +1.0)
        - Age penalty: -0.5 if company > 8 years old (nearing 10-yr DPIIT cap)
        """
        score = 0.0

        # Base points from statutory recognition
        if is_startup_recognized or competency.dpiit_recognition_number:
            score += 1.5
        if is_msme_registered:
            score += 1.0

        # Evidence signals
        for signal in competency.competency_signals:
            weight = SIGNAL_TRUST_WEIGHTS.get(signal.signal_type, 0.25)
            score += weight

        # GeM seller rating bonus (0–5 scale → 0–0.5 bonus)
        if competency.gem_seller_rating is not None:
            score += (competency.gem_seller_rating / 5.0) * 0.5

        # Pilot project bonus
        pilot_bonus = min(competency.pilot_project_count * 0.25, 1.0)
        score += pilot_bonus

        # Age penalty if nearing DPIIT 10-year cap
        if competency.years_since_incorporation >= 9:
            score -= 0.5

        return round(min(score, 10.0), 2)

    @staticmethod
    def detect_shield_override_risk(
        tender: TenderStatutoryCriteria,
    ) -> str:
        """
        Determines whether a buyer's ATC/Corrigendum has illegally blocked startup exemptions.

        Returns:
          SAFE              — No ATC override detected, shield fully operational
          ATC_OVERRIDE_RISK — Buyer ATC revokes exemptions; may be legally challenged
          SHIELD_FULLY_BLOCKED — Override exists AND was issued via valid Corrigendum (Rank 1)
        """
        if not tender.is_turnover_exemption_revoked_by_atc and not tender.is_experience_exemption_revoked_by_atc:
            return "SAFE"

        # Buyer ATCs (Rank 3-4) that revoke MSME exemptions without Corrigendum authority
        # are challengeable under MoF OM F.20/2/2014-PPD
        # We treat this as ATC_OVERRIDE_RISK (can be challenged in pre-bid)
        # If a Rank 1 Corrigendum revokes it, SHIELD_FULLY_BLOCKED
        # Since we can't always distinguish the source here, use conservative risk signal
        if tender.is_turnover_exemption_revoked_by_atc or tender.is_experience_exemption_revoked_by_atc:
            return "ATC_OVERRIDE_RISK"

        return "SAFE"

    @classmethod
    def map_competency_to_exemptions(
        cls,
        competency: ZeroHistoryCompetencyProfile,
        is_msme_registered: bool,
        is_startup_recognized: bool,
    ) -> List[str]:
        """Maps each competency signal to its specific statutory exemption text."""
        exemptions = []

        # Core statutory bases
        if is_startup_recognized or competency.dpiit_recognition_number:
            exemptions.append(
                "GFR 2017 Rule 173(i): Ministry of Finance may relax prior turnover and experience "
                "norms for DPIIT-recognised startups. This bidder qualifies under this provision."
            )
        if is_msme_registered:
            exemptions.append(
                "Public Procurement Policy for MSEs Order 2012: MSME bidders are exempt from "
                "minimum turnover and experience criteria under this order."
            )

        # Evidence-specific exemptions
        for signal in competency.competency_signals:
            exemption_text = EVIDENCE_TO_EXEMPTION.get(signal.signal_type)
            if exemption_text and exemption_text not in exemptions:
                exemptions.append(f"{signal.signal_type} ({signal.evidence_id}): {exemption_text}")

        return exemptions

    @classmethod
    def generate_mse_subcontracting_opportunities(
        cls,
        tender_title: str,
        tender_id: str,
        tender_value_lakhs: float,
        domain_keywords: Optional[List[str]] = None,
    ) -> List[MSESubcontractingOpportunity]:
        """
        When a startup cannot bid directly (blocked by ATC), checks if the tender
        triggers the PPP-MSE 2012 §4 mandatory 25% subcontracting clause.

        Under PPP-MSE Order 2012 Section 4: Central Government entities that procure
        ≥ ₹200 Lakhs (₹2 Crore) MUST subcontract at least 25% of the order value
        to Micro & Small Enterprises. This creates a mandatory opportunity for MSEs
        even when they cannot bid as the prime contractor.
        """
        opportunities: List[MSESubcontractingOpportunity] = []

        if tender_value_lakhs < MSE_SUBCONTRACTING_TRIGGER_LAKHS:
            logger.info(
                f"Tender value ₹{tender_value_lakhs}L < ₹{MSE_SUBCONTRACTING_TRIGGER_LAKHS}L "
                f"threshold. MSE subcontracting clause not triggered."
            )
            return opportunities

        mandatory_mse_share = round(tender_value_lakhs * MSE_MANDATORY_SUBCONTRACT_PCT, 2)

        # Determine domain category from tender title
        title_lower = tender_title.lower()
        keywords = domain_keywords or []
        if any(k in title_lower for k in ["software", "it ", "digital", "cloud", "app", "web", "cyber", "data", *keywords]):
            domain = "IT_SERVICES"
            domain_match = 0.90
        elif any(k in title_lower for k in ["civil", "construction", "infra", "road", "building"]):
            domain = "CIVIL_WORKS"
            domain_match = 0.75
        elif any(k in title_lower for k in ["supply", "goods", "equipment", "material", "hardware"]):
            domain = "GOODS_SUPPLY"
            domain_match = 0.80
        elif any(k in title_lower for k in ["consult", "advisory", "study", "research", "training"]):
            domain = "CONSULTING_SERVICES"
            domain_match = 0.85
        else:
            domain = "GENERAL"
            domain_match = 0.60

        # Generate the outreach template
        outreach = (
            f"Subject: Partnership Proposal under PPP-MSE Order 2012 §4 for [{tender_title}]\n\n"
            f"Dear Prime Contractor,\n\n"
            f"We are [Your Company], a DPIIT-recognized Micro/Small Enterprise specialising in {domain.replace('_', ' ').title()}.\n\n"
            f"As you may be aware, under the Public Procurement Policy for MSEs Order 2012, Section 4, "
            f"Central Government procurement orders above ₹{MSE_SUBCONTRACTING_TRIGGER_LAKHS:.0f} Lakhs "
            f"require that at least 25% of the contract value (₹{mandatory_mse_share:.2f} Lakhs in this case) "
            f"be subcontracted to Micro & Small Enterprises.\n\n"
            f"We would like to discuss how we can serve as your MSE subcontracting partner for this order, "
            f"enabling you to fulfil your statutory obligation while benefiting from our specialized capabilities.\n\n"
            f"Please find our capability statement attached.\n\nBest regards,\n[Your Company]"
        )

        prime_guidance = (
            f"Prime contractors who win this ₹{tender_value_lakhs:.2f}L tender are legally required to "
            f"subcontract ₹{mandatory_mse_share:.2f}L (25%) to registered MSEs under PPP-MSE Order 2012 §4. "
            f"Non-compliance can result in penal provisions and tender cancellation. "
            f"Contact prime bidders on the portal's vendor database with your capability statement."
        )

        opportunities.append(MSESubcontractingOpportunity(
            tender_title=tender_title,
            tender_id=tender_id,
            tender_estimated_value_lakhs=tender_value_lakhs,
            mandatory_mse_share_lakhs=mandatory_mse_share,
            domain_category=domain,
            domain_match_score=domain_match,
            statutory_basis="Public Procurement Policy for MSEs Order 2012, Section 4",
            prime_contractor_guidance=prime_guidance,
            outreach_template=outreach,
        ))

        return opportunities

    @classmethod
    def generate_pre_bid_shield_letter(
        cls,
        company_name: str,
        tender_title: str,
        tender_id: str,
        exemptions: List[str],
        avg_turnover_lakhs: float,
        required_turnover_lakhs: float,
        override_risk: str,
    ) -> str:
        """
        Generates a formal GFR 173(i) pre-bid representation letter.
        This letter is submitted during the pre-bid clarification window to challenge
        illegal turnover requirements and invoke startup exemptions.
        """
        today = date.today().strftime("%d %B %Y")
        revocation_para = ""
        if override_risk == "ATC_OVERRIDE_RISK":
            revocation_para = (
                "\n## Legal Challenge to ATC Revocation of Startup Exemptions\n\n"
                "It has been observed that Clause [X] of the Buyer-Added ATC / Corrigendum "
                "purports to revoke the MSME/Startup turnover relaxation for this procurement. "
                "This action is contrary to the mandatory provisions of MoF Office Memorandum "
                "No. F.20/2/2014-PPD (as amended) and GFR 2017 Rule 173(i), which vest the "
                "relaxation authority in the Ministry of Finance, not in the procuring entity.\n\n"
                "We respectfully request that this restrictive clause be deleted from the "
                "tender document via a fresh Corrigendum, and that the standard GFR "
                "startup exemptions be restored.\n\n"
            )

        exemption_list = "\n".join([f"- {e}" for e in exemptions])

        letter = f"""# Pre-Bid Legal Representation under GFR 2017 Rule 173(i)
## Subject: Request for Relaxation of Turnover Criterion under Startup India Policy

**Date:** {today}
**Reference:** Tender ID {tender_id} — {tender_title}
**Submitted by:** {company_name}

---

To,  
The Tender Processing Officer / Procuring Entity

---

## Declaration of Status

{company_name} (hereinafter "the Bidder") is a DPIIT-recognised startup / registered MSME
within the meaning of:

1. **Startup India Recognition**: as defined under the DPIIT Notification of 19 February 2019
2. **MSME Classification** (if applicable): as per MSME Development (Amendment) Act 2020

## Statutory Basis for Turnover Relaxation

The Bidder's current 3-year average annual turnover is ₹{avg_turnover_lakhs:.2f} Lakhs,
which is below the prescribed threshold of ₹{required_turnover_lakhs:.2f} Lakhs.

However, the Bidder is entitled to participate in this procurement under the following
statutory provisions:

{exemption_list}

Specifically, **General Financial Rules 2017, Rule 173(i)** empowers the Central Government
to "relax any or all the conditions of eligibility criteria in respect of MSMEs or startups,
for reasons to be recorded in writing." This bidder qualifies for this relaxation on the
following grounds of alternative technical competency:

[Insert: NABL Certificate / STQC Certificate / DPIIT Recognition Number / Incubator Letter]
{revocation_para}
## Request

1. That the minimum annual turnover criterion be waived / relaxed for this Bidder under
   GFR Rule 173(i) and PPP-MSE Order 2012.
2. That the Bidder be permitted to submit its bid on the basis of the technical competency
   evidence furnished above in lieu of financial turnover history.
3. That a written corrigendum be issued confirming this relaxation.

---

*This representation is submitted in good faith prior to the Pre-Bid Meeting and is
legally grounded in the Government of India's Startup India procurement framework.*

**{company_name}**  
[Authorised Signatory]  
[Date: {today}]
"""
        return letter

    @classmethod
    def evaluate(
        cls,
        bidder: BidderProfile,
        tender: TenderStatutoryCriteria,
        tender_id: str = "TENDER-UNKNOWN",
        tender_title: str = "Unnamed Tender",
        tender_value_lakhs: float = 0.0,
    ) -> StartupShieldReport:
        """
        Full Startup Statutory Shield evaluation.

        Returns a StartupShieldReport with:
        - Shield active status and strength score
        - Statutory exemption map
        - Pre-bid legal letter
        - MSE subcontracting opportunities (if value > ₹200L)
        - Actionable next steps ordered by priority
        """
        competency = bidder.competency_profile

        # If no competency profile and not a startup/MSME, shield is irrelevant
        if not competency and not bidder.is_startup_recognized and not bidder.is_msme_registered:
            return StartupShieldReport(
                company_name=bidder.company_name,
                is_shield_active=False,
                shield_strength_score=0.0,
                shield_override_risk="NOT_APPLICABLE",
                statutory_basis_summary=(
                    "Startup Statutory Shield not applicable: Bidder is not a DPIIT-recognised startup "
                    "or registered MSME. Standard financial qualification criteria apply."
                ),
                actionable_next_steps=[
                    "Register as an MSME at udyamregistration.gov.in to unlock turnover exemptions",
                    "Apply for DPIIT Startup Recognition at dpiit.gov.in/startups",
                    "Consider forming a consortium with a qualified MSME partner (Pillar B)",
                ]
            )

        # Use empty competency profile if not provided
        if not competency:
            competency = ZeroHistoryCompetencyProfile()

        # 1. Compute Shield Strength
        shield_strength = cls.compute_shield_strength(
            competency=competency,
            is_msme_registered=bidder.is_msme_registered,
            is_startup_recognized=bidder.is_startup_recognized,
        )

        # 2. Detect Override Risk
        override_risk = cls.detect_shield_override_risk(tender)

        # Downgrade strength if ATC blocked the exemptions
        if override_risk == "ATC_OVERRIDE_RISK":
            shield_strength = round(shield_strength * 0.6, 2)  # Reduced but challengeable
        elif override_risk == "SHIELD_FULLY_BLOCKED":
            shield_strength = round(shield_strength * 0.1, 2)  # Near-zero

        # 3. Map Competency Signals to Exemptions
        exemptions = cls.map_competency_to_exemptions(
            competency=competency,
            is_msme_registered=bidder.is_msme_registered,
            is_startup_recognized=bidder.is_startup_recognized,
        )

        # 4. Is Shield Active?
        avg_turnover = (
            bidder.turnover_year_1_lakhs +
            bidder.turnover_year_2_lakhs +
            bidder.turnover_year_3_lakhs
        ) / 3.0
        is_shield_active = (
            (bidder.is_startup_recognized or bidder.is_msme_registered) and
            shield_strength >= 1.5  # Minimum threshold to claim shield
        )

        # 5. Generate Pre-Bid Legal Letter
        legal_letter = cls.generate_pre_bid_shield_letter(
            company_name=bidder.company_name,
            tender_title=tender_title,
            tender_id=tender_id,
            exemptions=exemptions,
            avg_turnover_lakhs=avg_turnover,
            required_turnover_lakhs=tender.min_annual_turnover_lakhs,
            override_risk=override_risk,
        )

        # 6. MSE Subcontracting Opportunities (fallback when direct bid blocked)
        subcontracting_opps: List[MSESubcontractingOpportunity] = []
        effective_value = tender_value_lakhs if tender_value_lakhs > 0 else (
            tender.estimated_bid_value_lakhs or 0.0
        )
        if effective_value >= MSE_SUBCONTRACTING_TRIGGER_LAKHS and (
            bidder.is_msme_registered or bidder.is_startup_recognized
        ):
            subcontracting_opps = cls.generate_mse_subcontracting_opportunities(
                tender_title=tender_title,
                tender_id=tender_id,
                tender_value_lakhs=effective_value,
            )

        # 7. Startup Runway Tenders (illustrative classification of the current tender)
        runway_tenders: List[StartupRunwayTender] = []
        if is_shield_active:
            accessibility_factors = []
            blocking_factors = []

            if bidder.is_startup_recognized:
                accessibility_factors.append("DPIIT Startup Recognition — GFR 173(i) shield active")
            if bidder.is_msme_registered:
                accessibility_factors.append("MSME Registration — PPP-MSE 2012 turnover waiver")
            if competency.competency_signals:
                accessibility_factors.append(
                    f"{len(competency.competency_signals)} alternative competency signal(s) documented"
                )
            if effective_value <= 2500:  # < ₹25 Crore
                accessibility_factors.append("Tender value < ₹25 Crore — Startup-accessible range")

            if override_risk == "ATC_OVERRIDE_RISK":
                blocking_factors.append("Buyer ATC revokes exemptions — challenge via pre-bid letter")
            if effective_value > 5000:  # > ₹50 Crore
                blocking_factors.append("Large tender (>₹50 Cr) — consider consortium strategy")

            action = "DIRECT_BID" if not blocking_factors else (
                "CONSORTIUM_BID" if effective_value > 5000 else "DIRECT_BID_WITH_LEGAL_CHALLENGE"
            )

            runway_tenders.append(StartupRunwayTender(
                tender_id=tender_id,
                title=tender_title,
                estimated_value_lakhs=effective_value,
                portal="GeM/CPPP",
                startup_accessibility_score=min(shield_strength, 10.0),
                accessibility_factors=accessibility_factors,
                blocking_factors=blocking_factors,
                recommended_action=action,
                shield_applicable=True,
            ))

        # 8. Statutory Basis Summary
        basis_summary = (
            f"Startup Statutory Shield is {'ACTIVE' if is_shield_active else 'WEAK / INACTIVE'} "
            f"with strength score {shield_strength}/10. "
            f"Legal basis: GFR 2017 Rule 173(i) + "
            f"{'PPP-MSE Order 2012' if bidder.is_msme_registered else 'DPIIT Startup Notification 2019'}. "
            f"Shield override risk: {override_risk}."
        )

        # 9. Actionable Next Steps
        next_steps: List[str] = []
        if is_shield_active:
            next_steps.append(
                "📋 Submit the auto-generated Pre-Bid Representation Letter during the pre-bid meeting window"
            )
        if override_risk == "ATC_OVERRIDE_RISK":
            next_steps.append(
                "⚠️ File a formal objection to the ATC clause revoking MSME exemptions (MoF OM F.20/2/2014-PPD)"
            )
        if subcontracting_opps:
            next_steps.append(
                f"🤝 Contact prime contractors who win this tender — PPP-MSE 2012 §4 entitles you to "
                f"₹{subcontracting_opps[0].mandatory_mse_share_lakhs:.2f}L in mandatory subcontracts"
            )
        if not competency.dpiit_recognition_number and bidder.is_startup_recognized:
            next_steps.append(
                "📝 Add your DPIIT recognition number to your bidder profile to strengthen shield citations"
            )
        if not competency.competency_signals:
            next_steps.append(
                "🔬 Upload NABL/STQC/BIS certificates to your profile for Tier-1 shield strength"
            )
        if shield_strength < 3.0:
            next_steps.append(
                "💡 Consider forming a JV with a financially qualified partner (Pillar B Consortium Matchmaker)"
            )

        # Update competency profile with computed values
        competency.applicable_exemptions = exemptions
        competency.shield_strength_score = shield_strength
        competency.shield_override_risk = override_risk

        return StartupShieldReport(
            company_name=bidder.company_name,
            is_shield_active=is_shield_active,
            shield_strength_score=shield_strength,
            shield_override_risk=override_risk,
            statutory_basis_summary=basis_summary,
            applicable_exemptions=exemptions,
            competency_evidence_map=competency.competency_signals,
            runway_tenders=runway_tenders,
            subcontracting_opportunities=subcontracting_opps,
            pre_bid_shield_letter=legal_letter if is_shield_active else "",
            actionable_next_steps=next_steps,
        )