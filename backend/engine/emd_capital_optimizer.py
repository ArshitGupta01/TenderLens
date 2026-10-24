"""Estimate EMD cash-lockup scenarios without deciding exemptions or permitted instruments."""

from contracts.schema import BidderProfile, EMDCapitalOptimizationReport
from backend.engine.deterministic_gatekeeper import TenderStatutoryCriteria


class EMDCapitalOptimizer:
    @classmethod
    def evaluate_capital_risk(
        cls,
        bidder: BidderProfile,
        criteria: TenderStatutoryCriteria,
    ) -> EMDCapitalOptimizationReport:
        emd = max(0.0, float(criteria.emd_amount_inr))
        bid_count = max(1, int(bidder.active_simultaneous_bids_count))
        cash_scenario = emd * bid_count
        days = criteria.estimated_emd_lockup_days
        rate = criteria.annual_capital_cost_rate_pct
        opportunity_cost = None
        if days is not None and rate is not None:
            opportunity_cost = round(cash_scenario * (rate / 100.0) * (days / 365.0), 2)
        capital = bidder.available_emd_working_capital_inr
        utilization = round((cash_scenario / capital) * 100.0, 1) if capital and capital > 0 else None

        return EMDCapitalOptimizationReport(
            emd_required_inr=emd,
            is_statutorily_exempt=None,
            exemption_statute="Not assessed; check the bidder's current registration and the complete tender terms.",
            effective_cash_lockup_inr=cash_scenario,
            estimated_lockup_days=days,
            annual_cost_rate_pct=rate,
            estimated_opportunity_cost_inr=opportunity_cost,
            portfolio_capital_utilization_pct=utilization,
            surety_bond_permitted=criteria.surety_bond_permitted_by_tender,
            recommended_instrument="CHECK_TENDER_TERMS",
            liquidity_advisory=(
                "Scenario only: the cash-lockup figure assumes the entered EMD is held in cash for each active bid. "
                "No exemption, security instrument, refund timing or bank/insurer charge has been verified."
            ),
        )
