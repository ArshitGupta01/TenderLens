"""
TenderLens - Pillar D: EMD Capital Risk & Surety Bond Optimizer
===============================================================
Calculates working capital lock-up across simultaneous bids and evaluates
modern Indian liquidity instruments:
1. GFR 2017 Rule 170(i) Complete Exemption (Udyam MSEs & DPIIT Startups)
2. IRDAI Insurance Surety Bonds (MoF OM No. F.1/1/2022-PPD dated 02.02.2022)
3. NeSL Electronic Bank Guarantee (e-BG) vs Traditional Cash FDR/DD Lock-up
"""

from contracts.schema import BidderProfile, EMDCapitalOptimizationReport
from backend.engine.deterministic_gatekeeper import TenderStatutoryCriteria


class EMDCapitalOptimizer:
    @classmethod
    def evaluate_capital_risk(
        cls,
        bidder: BidderProfile,
        criteria: TenderStatutoryCriteria
    ) -> EMDCapitalOptimizationReport:
        emd_inr = max(0.0, float(criteria.emd_amount_inr))
        is_exempt = bool(bidder.is_msme_registered or bidder.is_startup_recognized)
        if criteria.emd_exemption_confirmed_by_tender is False:
            is_exempt = False

        lockup_days = int(criteria.estimated_emd_lockup_days or 120)
        rate_pct = float(criteria.annual_capital_cost_rate_pct if criteria.annual_capital_cost_rate_pct is not None else 12.0)
        annual_rate = max(0.0, rate_pct) / 100.0

        surety_allowed = (
            bool(criteria.surety_bond_permitted_by_tender)
            if criteria.surety_bond_permitted_by_tender is not None
            else bool(criteria.allow_insurance_surety_bond)
        )

        if emd_inr <= 0.0:
            return EMDCapitalOptimizationReport(
                emd_required_inr=0.0,
                is_statutorily_exempt=True,
                exemption_statute="Tender Schedule — Nil EMD Mandated",
                effective_cash_lockup_inr=0.0,
                estimated_lockup_days=0,
                annual_cost_rate_pct=rate_pct,
                opportunity_cost_at_12pct_pa_inr=0.0,
                estimated_opportunity_cost_inr=0.0,
                portfolio_capital_utilization_pct=0.0,
                surety_bond_permitted=surety_allowed,
                recommended_instrument="NO_INSTRUMENT_REQUIRED",
                liquidity_advisory="Zero EMD required for this tender. 100% of working capital remains liquid."
            )

        if is_exempt:
            saved_opportunity_cost = round(emd_inr * annual_rate * (lockup_days / 365.0), 2)
            return EMDCapitalOptimizationReport(
                emd_required_inr=emd_inr,
                is_statutorily_exempt=True,
                exemption_statute="GFR 2017 Rule 170(i) & Public Procurement Policy for MSEs Order 2012",
                effective_cash_lockup_inr=0.0,
                estimated_lockup_days=lockup_days,
                annual_cost_rate_pct=rate_pct,
                opportunity_cost_at_12pct_pa_inr=0.0,
                estimated_opportunity_cost_inr=0.0,
                portfolio_capital_utilization_pct=0.0,
                surety_bond_permitted=surety_allowed,
                recommended_instrument="BID_SECURITY_DECLARATION_NIL_COST",
                liquidity_advisory=(
                    f"LIQUIDITY PROTECTED: As a registered {'MSME' if bidder.is_msme_registered else 'DPIIT Startup'}, "
                    f"do NOT lock up ₹{emd_inr:,.2f} in FDR/BG (subject to governing tender schedule). Upload the auto-generated GFR Rule 170(i) Bid Security "
                    f"Declaration in Pillar C, saving ₹{saved_opportunity_cost:,.2f} in annualized working capital interest."
                )
            )

        # Commercial (Non-MSME) Bidder Capital Risk Calculation
        concurrent_bids = max(1, bidder.active_simultaneous_bids_count)
        total_portfolio_emd = emd_inr * concurrent_bids
        avail_cap = max(1.0, bidder.available_emd_working_capital_inr)
        utilization_pct = round((total_portfolio_emd / avail_cap) * 100.0, 1)
        opportunity_cost = round(emd_inr * annual_rate * (lockup_days / 365.0), 2)

        if surety_allowed:
            # Insurance Surety Bond typically requires ~1.25% premium and 0%–10% collateral vs 100% FDR margin
            surety_cash_outflow = round(emd_inr * 0.015, 2)
            return EMDCapitalOptimizationReport(
                emd_required_inr=emd_inr,
                is_statutorily_exempt=False,
                exemption_statute="MoF OM No. F.1/1/2022-PPD (Amendment to GFR Rule 170 & 171 — Insurance Surety Bonds)",
                effective_cash_lockup_inr=surety_cash_outflow,
                estimated_lockup_days=lockup_days,
                annual_cost_rate_pct=rate_pct,
                opportunity_cost_at_12pct_pa_inr=opportunity_cost,
                estimated_opportunity_cost_inr=opportunity_cost,
                portfolio_capital_utilization_pct=utilization_pct,
                surety_bond_permitted=True,
                recommended_instrument="IRDAI_INSURANCE_SURETY_BOND",
                liquidity_advisory=(
                    f"CAPITAL OPTIMIZATION: Across {concurrent_bids} simultaneous bid(s), traditional FDR/Bank Guarantees "
                    f"would lock up ₹{total_portfolio_emd:,.2f} ({utilization_pct}% of your ₹{avail_cap:,.0f} EMD budget) "
                    f"with ₹{opportunity_cost:,.2f} interest cost per bid. Under MoF OM F.1/1/2022-PPD (GFR Rule 170(i)), "
                    f"submit an IRDAI-regulated Insurance Surety Bond (estimated outlay ~₹{surety_cash_outflow:,.2f}) to "
                    f"free up 98.5% of your working capital."
                )
            )

        return EMDCapitalOptimizationReport(
            emd_required_inr=emd_inr,
            is_statutorily_exempt=False,
            exemption_statute="Standard Commercial EMD — NeSL e-BG / Bank FDR",
            effective_cash_lockup_inr=emd_inr,
            estimated_lockup_days=lockup_days,
            annual_cost_rate_pct=rate_pct,
            opportunity_cost_at_12pct_pa_inr=opportunity_cost,
            estimated_opportunity_cost_inr=opportunity_cost,
            portfolio_capital_utilization_pct=utilization_pct,
            surety_bond_permitted=False,
            recommended_instrument="NESL_E_BG",
            liquidity_advisory=(
                f"HIGH WORKING CAPITAL LOCK-UP: ₹{emd_inr:,.2f} required ({utilization_pct}% portfolio utilization across "
                f"{concurrent_bids} bids). Use NeSL Electronic Bank Guarantee (e-BG) with credit line limits rather than "
                f"100% cash-margin FDR to preserve liquidity."
            )
        )
