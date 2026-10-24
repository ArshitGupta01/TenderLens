"""
TenderLens - Qualification Engine: Deterministic Gatekeeper (v1.0.1)
==================================================================
Executes pure-Python mathematical and statutory checks with zero hallucination:
1. 3-Year Average Turnover + MSE PPP-2012 / GFR 173(i) exemption (with JV aggregation)
2. Years of Experience & Similar Work (CPWD 80/50/40 ratio)
3. EMD Exemption under GFR 2017 Rule 170(i)
4. Make in India (MII) Class-I / Class-II supplier classification (DPIIT Order 2017)
5. Entity Type & OEM Authorization Form (MAF) requirement
6. Mandatory Certifications set-difference verification
7. Optional CPWD 80/50/40 Similar Work Gate (when estimated_bid_value_lakhs is specified)
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from contracts.schema import BidderProfile, GateResult


class TenderStatutoryCriteria(BaseModel):
    min_annual_turnover_lakhs: float = 0.0
    min_experience_years: int = 0
    estimated_bid_value_lakhs: Optional[float] = None
    emd_amount_inr: float = 0.0
    min_local_content_percentage: float = 20.0
    mandatory_certifications: List[str] = Field(default_factory=list)
    oem_authorization_mandatory: bool = False
    msme_turnover_relaxation_allowed: bool = True
    msme_experience_relaxation_allowed: bool = True
    is_turnover_exemption_revoked_by_atc: bool = False
    is_experience_exemption_revoked_by_atc: bool = False
    allow_class_2_suppliers: bool = True
    allow_insurance_surety_bond: bool = True
    proprietary_brand_lock_detected: bool = False
    proprietary_brand_details: Optional[str] = None


class DeterministicGatekeeper:
    @staticmethod
    def verify_cpwd_80_50_40(
        project_values_lakhs: List[float],
        estimated_cost_lakhs: float
    ) -> tuple[bool, str]:
        """
        Deterministic verification of CPWD / CVC Similar Work criteria:
        - Option A: At least 1 completed work costing not less than 80% of estimated cost
        - Option B: At least 2 completed works each costing not less than 50% of estimated cost
        - Option C: At least 3 completed works each costing not less than 40% of estimated cost
        """
        if estimated_cost_lakhs <= 0:
            return True, "No estimated bid cost specified for CPWD 80/50/40 ratio check."

        t80 = round(0.80 * estimated_cost_lakhs, 2)
        t50 = round(0.50 * estimated_cost_lakhs, 2)
        t40 = round(0.40 * estimated_cost_lakhs, 2)

        c80 = sum(1 for v in project_values_lakhs if v >= t80)
        c50 = sum(1 for v in project_values_lakhs if v >= t50)
        c40 = sum(1 for v in project_values_lakhs if v >= t40)

        if c80 >= 1:
            return True, f"Satisfies CPWD 80% gate: {c80} project(s) >= ₹{t80:.2f}L (80% of ₹{estimated_cost_lakhs:.2f}L)."
        if c50 >= 2:
            return True, f"Satisfies CPWD 50% gate: {c50} projects >= ₹{t50:.2f}L each (50% of ₹{estimated_cost_lakhs:.2f}L)."
        if c40 >= 3:
            return True, f"Satisfies CPWD 40% gate: {c40} projects >= ₹{t40:.2f}L each (40% of ₹{estimated_cost_lakhs:.2f}L)."

        return False, (
            f"Fails CPWD 80/50/40 Similar Work threshold for ₹{estimated_cost_lakhs:.2f}L bid. "
            f"Requires 1 work >= ₹{t80:.2f}L, OR 2 works >= ₹{t50:.2f}L, OR 3 works >= ₹{t40:.2f}L."
        )

    @classmethod
    def evaluate(
        cls,
        bidder: BidderProfile,
        tender: TenderStatutoryCriteria
    ) -> List[GateResult]:
        """
        Runs the full suite of deterministic gates against the bidder profile.
        Supports standalone entity or Consortium/JV aggregated credentials.
        """
        results: List[GateResult] = []

        # Aggregate Consortium / JV partner credentials if present
        partner_turnover = sum(p.avg_annual_turnover_lakhs for p in bidder.consortium_partners)
        partner_max_exp = max([p.years_in_business for p in bidder.consortium_partners], default=0)
        partner_certs = [c for p in bidder.consortium_partners for c in p.held_certifications]
        partner_has_oem = any(p.entity_type.upper() in ["OEM", "MANUFACTURER"] for p in bidder.consortium_partners)

        # -------------------------------------------------------------
        # 1. 3-Year Average Annual Turnover Gate
        # -------------------------------------------------------------
        base_avg_turnover = (
            bidder.turnover_year_1_lakhs +
            bidder.turnover_year_2_lakhs +
            bidder.turnover_year_3_lakhs
        ) / 3.0
        avg_turnover = base_avg_turnover + partner_turnover

        turnover_passed = avg_turnover >= tender.min_annual_turnover_lakhs
        turnover_hard_disqualifier = False
        statutory_note = "General Financial Rules (GFR) 2017 / GeM GTC"
        reason = ""

        if turnover_passed:
            jv_tag = f" (including ₹{partner_turnover:.2f}L from JV partner)" if partner_turnover > 0 else ""
            reason = f"Bidder average 3-year turnover of ₹{avg_turnover:.2f} Lakhs{jv_tag} meets or exceeds required ₹{tender.min_annual_turnover_lakhs:.2f} Lakhs."
        else:
            is_eligible_for_exemption = (bidder.is_msme_registered or bidder.is_startup_recognized)
            if is_eligible_for_exemption and tender.msme_turnover_relaxation_allowed and not tender.is_turnover_exemption_revoked_by_atc:
                turnover_passed = True
                statutory_note = "Public Procurement Policy for MSEs Order, 2012 / GFR Rule 173(i)"
                reason = (
                    f"Turnover relaxation granted under PPP-2012: Bidder is a registered "
                    f"{'MSME (' + str(bidder.msme_category) + ')' if bidder.is_msme_registered else 'DPIIT Startup'}. "
                    f"Minimum turnover criteria waived."
                )
            elif is_eligible_for_exemption and tender.is_turnover_exemption_revoked_by_atc:
                turnover_passed = False
                turnover_hard_disqualifier = True
                statutory_note = "Buyer Added ATC Override (Precedence Rank 3 / Corrigendum Rank 1)"
                reason = (
                    f"Turnover below threshold (₹{avg_turnover:.2f} Lakhs < ₹{tender.min_annual_turnover_lakhs:.2f} Lakhs). "
                    f"CRITICAL DISQUALIFIER: Buyer ATC / Corrigendum explicitly revokes MSME turnover relaxation for this procurement."
                )
            else:
                turnover_passed = False
                turnover_hard_disqualifier = True
                reason = (
                    f"Turnover below threshold: Bidder average of ₹{avg_turnover:.2f} Lakhs is less than required ₹{tender.min_annual_turnover_lakhs:.2f} Lakhs. "
                    f"Bidder is not eligible for statutory exemptions."
                )

        results.append(GateResult(
            rule_name="3-Year Average Annual Turnover",
            passed=turnover_passed,
            is_hard_disqualifier=turnover_hard_disqualifier,
            bidder_value=f"₹{avg_turnover:.2f} Lakhs (Avg 3Y)",
            required_value=f"₹{tender.min_annual_turnover_lakhs:.2f} Lakhs",
            reason=reason,
            statutory_citation=statutory_note
        ))

        # -------------------------------------------------------------
        # 2. Years in Business / Experience Gate
        # -------------------------------------------------------------
        effective_years = max(bidder.years_in_business, partner_max_exp)
        exp_passed = effective_years >= tender.min_experience_years
        exp_hard_disqualifier = False
        exp_statutory_note = "Standard Procurement Experience Baseline"

        if exp_passed:
            exp_reason = f"Bidder has {effective_years} years in business, satisfying the {tender.min_experience_years} years requirement."
        else:
            is_eligible_for_exemption = (bidder.is_msme_registered or bidder.is_startup_recognized)
            if is_eligible_for_exemption and tender.msme_experience_relaxation_allowed and not tender.is_experience_exemption_revoked_by_atc:
                exp_passed = True
                exp_statutory_note = "DPIIT Notification / GFR Rule 173(i) Startup Relaxation"
                exp_reason = f"Experience criteria relaxed under DPIIT startup / MSE policy (bidder has {effective_years} years vs {tender.min_experience_years} years required)."
            elif is_eligible_for_exemption and tender.is_experience_exemption_revoked_by_atc:
                exp_passed = False
                exp_hard_disqualifier = True
                exp_statutory_note = "Buyer ATC Override"
                exp_reason = f"Experience below threshold ({effective_years} < {tender.min_experience_years} yrs). Buyer ATC explicitly prohibits experience relaxation."
            else:
                exp_passed = False
                exp_hard_disqualifier = True
                exp_reason = f"Insufficient experience: {effective_years} years in business vs minimum {tender.min_experience_years} years mandated."

        results.append(GateResult(
            rule_name="Experience & Past Performance",
            passed=exp_passed,
            is_hard_disqualifier=exp_hard_disqualifier,
            bidder_value=f"{effective_years} Years",
            required_value=f"{tender.min_experience_years} Years",
            reason=exp_reason,
            statutory_citation=exp_statutory_note
        ))

        # -------------------------------------------------------------
        # 3. Earnest Money Deposit (EMD) Exemption Gate
        # -------------------------------------------------------------
        is_emd_exempt = bidder.is_msme_registered or bidder.is_startup_recognized
        emd_passed = True
        emd_reason = ""
        emd_citation = "General Financial Rules (GFR) 2017 Rule 170(i)"

        if tender.emd_amount_inr <= 0:
            emd_reason = "No Earnest Money Deposit required for this bid."
        elif is_emd_exempt:
            emd_reason = (
                f"Exempt from ₹{tender.emd_amount_inr:,.2f} EMD under GFR Rule 170(i) "
                f"as a registered {'MSME' if bidder.is_msme_registered else 'DPIIT Startup'}. "
                f"A Bid Security Declaration must be submitted in lieu."
            )
        else:
            emd_reason = (
                f"Mandatory EMD deposit required: ₹{tender.emd_amount_inr:,.2f}. "
                f"Bidder is not exempt and must provide Insurance Surety Bond / e-BG / DD prior to bid closing."
            )

        results.append(GateResult(
            rule_name="Earnest Money Deposit (EMD)",
            passed=emd_passed,
            is_hard_disqualifier=False,
            bidder_value="MSE/Startup Exempt" if is_emd_exempt else "Commercial Bidder",
            required_value=f"₹{tender.emd_amount_inr:,.2f}",
            reason=emd_reason,
            statutory_citation=emd_citation
        ))

        # -------------------------------------------------------------
        # 4. Make in India (MII) Preference Gate
        # -------------------------------------------------------------
        bidder_local_pct = bidder.local_content_percentage
        mii_class = "Class-I Local Supplier (>= 50%)" if bidder_local_pct >= 50.0 else (
            "Class-II Local Supplier (20% - 49%)" if bidder_local_pct >= 20.0 else "Non-Local Supplier (< 20%)"
        )

        mii_passed = bidder_local_pct >= tender.min_local_content_percentage
        if not tender.allow_class_2_suppliers and bidder_local_pct < 50.0:
            mii_passed = False

        results.append(GateResult(
            rule_name="Public Procurement (Preference to Make in India)",
            passed=mii_passed,
            is_hard_disqualifier=not mii_passed,
            bidder_value=f"{bidder_local_pct:.1f}% ({mii_class})",
            required_value=f"{tender.min_local_content_percentage:.1f}% (Min Local Content)",
            reason=(
                f"Bidder qualifies as {mii_class} meeting the tender's {tender.min_local_content_percentage}% local content threshold."
                if mii_passed else
                f"Bidder local content ({bidder_local_pct:.1f}%) fails the minimum {tender.min_local_content_percentage}% threshold required by DPIIT MII order."
            ),
            statutory_citation="DPIIT Public Procurement (Preference to Make in India) Order, 2017"
        ))

        # -------------------------------------------------------------
        # 5. Entity Role & OEM Authorization (MAF) Gate
        # -------------------------------------------------------------
        is_oem = bidder.entity_type.upper() in ["OEM", "MANUFACTURER"] or partner_has_oem
        maf_required = tender.oem_authorization_mandatory and not is_oem

        maf_passed = True
        maf_hard = False
        maf_reason = ""

        if is_oem:
            maf_reason = f"Bidder (or Consortium OEM Partner) is an Original Equipment Manufacturer ({bidder.entity_type}). No secondary MAF required."
        elif maf_required:
            maf_passed = True
            maf_hard = False
            maf_reason = (
                f"Bidder is a {bidder.entity_type}. Tender explicitly requires a Manufacturer Authorization Form (MAF). "
                f"CONDITIONAL REQUIREMENT: Bidder must secure and upload signed OEM MAF certificate."
            )
        else:
            maf_reason = f"Entity role ({bidder.entity_type}) accepted without mandatory MAF."

        results.append(GateResult(
            rule_name="Entity Role & OEM Authorization (MAF)",
            passed=maf_passed,
            is_hard_disqualifier=maf_hard,
            bidder_value=bidder.entity_type,
            required_value="OEM or Authorized Reseller with MAF" if tender.oem_authorization_mandatory else "Any Registered Entity",
            reason=maf_reason,
            statutory_citation="GeM ATC Bidder Specific Authorization Guidelines"
        ))

        # -------------------------------------------------------------
        # 6. Mandatory Certifications Set-Difference Gate
        # -------------------------------------------------------------
        def normalize_cert(cert_str: str) -> str:
            return cert_str.upper().replace(" ", "").replace("-", "").replace(":", "")

        combined_certs = list(set(bidder.held_certifications + partner_certs))
        held_normalized = {normalize_cert(c) for c in combined_certs}
        missing_certs: List[str] = []

        for req_cert in tender.mandatory_certifications:
            if normalize_cert(req_cert) not in held_normalized:
                missing_certs.append(req_cert)

        certs_passed = len(missing_certs) == 0
        results.append(GateResult(
            rule_name="Mandatory Certifications",
            passed=certs_passed,
            is_hard_disqualifier=not certs_passed,
            bidder_value=combined_certs if combined_certs else "None Registered",
            required_value=tender.mandatory_certifications if tender.mandatory_certifications else "None Specified",
            reason=(
                "All mandatory technical, quality, and statutory certificates are verified."
                if certs_passed else
                f"DISQUALIFIER: Missing {len(missing_certs)} required certification(s): {', '.join(missing_certs)}."
            ),
            statutory_citation="Technical Specifications & Eligibility Annexure"
        ))

        # -------------------------------------------------------------
        # 7. Optional CPWD 80/50/40 Similar Work Gate
        # -------------------------------------------------------------
        if tender.estimated_bid_value_lakhs and tender.estimated_bid_value_lakhs > 0 and bidder.past_similar_project_values_lakhs:
            all_projects = list(bidder.past_similar_project_values_lakhs)
            for p in bidder.consortium_partners:
                if p.highest_single_project_value_lakhs > 0:
                    all_projects.append(p.highest_single_project_value_lakhs)

            cpwd_passed, cpwd_reason = cls.verify_cpwd_80_50_40(
                project_values_lakhs=all_projects,
                estimated_cost_lakhs=tender.estimated_bid_value_lakhs
            )
            if not cpwd_passed and (bidder.is_msme_registered or bidder.is_startup_recognized) and not tender.is_experience_exemption_revoked_by_atc:
                cpwd_passed = True
                cpwd_reason += " [Relaxed under MSE/Startup Past Performance Exemption - GFR Rule 173(i)]."

            results.append(GateResult(
                rule_name="CPWD 80/50/40 Similar Work Experience",
                passed=cpwd_passed,
                is_hard_disqualifier=not cpwd_passed,
                bidder_value=f"Projects: {all_projects} Lakhs",
                required_value=f"80%/50%/40% of ₹{tender.estimated_bid_value_lakhs:.2f} Lakhs",
                reason=cpwd_reason,
                statutory_citation="CPWD Works Manual / CVC Guidelines on Similar Works"
            ))

        return results
