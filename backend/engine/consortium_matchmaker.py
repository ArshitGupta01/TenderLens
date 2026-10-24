"""Identify capability gaps without inventing partners or eligibility outcomes."""

from typing import List

from contracts.schema import (
    BidderProfile,
    ConsortiumMatchRecommendation,
    GateResult,
    ShortfallGapItem,
)
from backend.engine.deterministic_gatekeeper import TenderStatutoryCriteria


class ConsortiumMatchmaker:
    @classmethod
    def analyze_and_match(
        cls,
        bidder: BidderProfile,
        criteria: TenderStatutoryCriteria,
        gate_results: List[GateResult],
    ) -> ConsortiumMatchRecommendation:
        average_turnover = (
            bidder.turnover_year_1_lakhs
            + bidder.turnover_year_2_lakhs
            + bidder.turnover_year_3_lakhs
        ) / 3.0
        gaps: List[ShortfallGapItem] = []

        for gate in gate_results:
            if gate.review_required:
                gaps.append(ShortfallGapItem(
                    gate_name=gate.rule_name,
                    shortfall_type="RULE_REVIEW_REQUIRED",
                    bidder_current_value=gate.bidder_value,
                    tender_required_value=gate.required_value,
                    numerical_gap_lakhs_or_years=0.0,
                    bridging_strategy=(
                        f"Do not treat this as a confirmed gap. {gate.reason} "
                        "Verify the current tender wording and eligibility evidence before considering any partner."
                    ),
                ))
                continue
            if gate.passed:
                continue
            if gate.rule_name == "3-Year Average Annual Turnover":
                gap = max(0.0, round(criteria.min_annual_turnover_lakhs - average_turnover, 2))
                gaps.append(ShortfallGapItem(
                    gate_name=gate.rule_name,
                    shortfall_type="TURNOVER_GAP",
                    bidder_current_value=f"₹{average_turnover:.2f} lakh average (entered)",
                    tender_required_value=f"₹{criteria.min_annual_turnover_lakhs:.2f} lakh (entered)",
                    numerical_gap_lakhs_or_years=gap,
                    bridging_strategy="Check whether the tender permits JV/consortium credentials and how each member's turnover is counted.",
                ))
            elif gate.rule_name == "Experience & Past Performance":
                gap = max(0, criteria.min_experience_years - bidder.years_in_business)
                gaps.append(ShortfallGapItem(
                    gate_name=gate.rule_name,
                    shortfall_type="EXPERIENCE_GAP",
                    bidder_current_value=f"{bidder.years_in_business} years (entered)",
                    tender_required_value=f"{criteria.min_experience_years} years (entered)",
                    numerical_gap_lakhs_or_years=float(gap),
                    bridging_strategy="Check whether the tender allows consortium experience and which member's completed work may count.",
                ))
            elif gate.rule_name == "Mandatory Certifications":
                held = {item.strip().casefold() for item in bidder.held_certifications}
                missing = [item for item in criteria.mandatory_certifications if item.strip().casefold() not in held]
                gaps.append(ShortfallGapItem(
                    gate_name=gate.rule_name,
                    shortfall_type="CERTIFICATION_GAP",
                    bidder_current_value=bidder.held_certifications,
                    tender_required_value=criteria.mandatory_certifications,
                    numerical_gap_lakhs_or_years=float(len(missing)),
                    bridging_strategy="Confirm whether another consortium member may provide the required certification and verify that member's evidence.",
                ))
            elif gate.rule_name == "Public Procurement (Preference to Make in India)":
                gap = max(0.0, criteria.min_local_content_percentage - bidder.local_content_percentage)
                gaps.append(ShortfallGapItem(
                    gate_name=gate.rule_name,
                    shortfall_type="MII_LOCAL_CONTENT_GAP",
                    bidder_current_value=f"{bidder.local_content_percentage:.1f}% (entered)",
                    tender_required_value=f"{criteria.min_local_content_percentage:.1f}% (entered)",
                    numerical_gap_lakhs_or_years=round(gap, 1),
                    bridging_strategy="Check the tender's local-content calculation and whether partner contributions may be combined.",
                ))
            elif gate.rule_name == "Entity Role & OEM Authorization (MAF)" and "CONDITIONAL REQUIREMENT" in gate.reason:
                gaps.append(ShortfallGapItem(
                    gate_name=gate.rule_name,
                    shortfall_type="OEM_MAF_REQUIRED",
                    bidder_current_value=bidder.entity_type,
                    tender_required_value="Tender-specific OEM authorization, if required by the source clause",
                    numerical_gap_lakhs_or_years=0.0,
                    bridging_strategy="Confirm the exact authorization format, product scope and signing authority in the original tender.",
                ))

        if gaps:
            confirmed_gaps = [item for item in gaps if item.shortfall_type != "RULE_REVIEW_REQUIRED"]
            review_count = len(gaps) - len(confirmed_gaps)
            summary = (
                f"{len(confirmed_gaps)} possible gap(s) and {review_count} rule(s) needing review were found from the values entered. "
                "No partner registry is connected and no JV outcome is assumed. "
                "Confirm tender-specific consortium rules and verify every partner credential before relying on a combined bid profile."
            )
        else:
            summary = (
                "No capability gaps were identified from the entered values. This does not verify supporting documents or establish that a consortium is permitted."
            )

        return ConsortiumMatchRecommendation(
            has_shortfall=any(item.shortfall_type != "RULE_REVIEW_REQUIRED" for item in gaps),
            identified_gaps=gaps,
            recommended_partners=[],
            post_consortium_recommendation="NOT_ASSESSED",
            post_consortium_score=None,
            actionable_summary=summary,
        )
