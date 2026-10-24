"""
TenderLens Shared Contract Schema (Pydantic & JSON)
==================================================
This file defines the shared contract between Research/Evaluation (Argon)
and Backend/Frontend Engineering.

Rule: Neither party changes field names without a quick sync.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BidderProfile(BaseModel):
    """Bidder business profile used for automated qualification checks."""
    company_name: str
    entity_type: str  # OEM, Manufacturer, Trader, EPC, Reseller
    is_msme_registered: bool = False
    msme_category: Optional[str] = None  # MICRO, SMALL, MEDIUM
    is_startup_recognized: bool = False
    turnover_year_1_lakhs: float = Field(ge=0)
    turnover_year_2_lakhs: float = Field(ge=0)
    turnover_year_3_lakhs: float = Field(ge=0)
    years_in_business: int = Field(ge=0, le=150)
    local_content_percentage: float = Field(default=20.0, ge=0, le=100)  # Make in India compliance
    held_certifications: List[str] = Field(default_factory=list)  # e.g., ["ISO-9001", "BIS"]
    past_similar_project_values_lakhs: List[float] = Field(default_factory=list, max_length=100)
    available_emd_working_capital_inr: Optional[float] = Field(default=None, ge=0)
    active_simultaneous_bids_count: int = Field(default=1, ge=1, le=100)


class ClauseCitation(BaseModel):
    """Evidence anchor linking findings to exact source coordinates."""
    document_name: str  # e.g., "Main_Tender.pdf", "Buyer_ATC.pdf", "Corrigendum_1.pdf"
    page_number: int
    clause_id: str
    verbatim_text: str
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH_DISQUALIFIER
    status: str = "COMPLIANT"  # COMPLIANT, NON_COMPLIANT, CONDITIONAL, AMBIGUOUS_MANUAL_REVIEW


class GateResult(BaseModel):
    """Deterministic mathematical rule check (Python verified, zero hallucination)."""
    rule_name: str
    passed: bool
    is_hard_disqualifier: bool
    bidder_value: Any
    required_value: Any
    reason: str
    statutory_citation: Optional[str] = None
    review_required: bool = False


class PreBidRepresentationItem(BaseModel):
    query_id: str
    document_name: str
    page_number: Optional[int] = None
    clause_reference: str
    impugned_clause_excerpt: str
    violation_category: str
    statutory_authority_cited: str
    formal_argument: str
    requested_corrigendum_amendment: str


class PreBidLegalRepresentationPack(BaseModel):
    tender_id: str
    tender_title: str
    bidder_company: str
    total_challenges: int
    representations: List[PreBidRepresentationItem] = Field(default_factory=list)
    formal_letter_markdown: str = ""


class ConsortiumPartnerProfile(BaseModel):
    partner_id: str
    company_name: str
    entity_type: str
    role_in_consortium: str = "TECH_OR_FIN_PARTNER"
    is_msme_registered: bool = False
    avg_annual_turnover_lakhs: float = 0.0
    years_in_business: int = 0
    highest_single_project_value_lakhs: float = 0.0
    local_content_percentage: float = 50.0
    held_certifications: List[str] = Field(default_factory=list)
    synergy_rationale: str = ""


class ShortfallGapItem(BaseModel):
    gate_name: str
    shortfall_type: str
    bidder_current_value: Any
    tender_required_value: Any
    numerical_gap_lakhs_or_years: float = 0.0
    bridging_strategy: str


class ConsortiumMatchRecommendation(BaseModel):
    has_shortfall: bool
    identified_gaps: List[ShortfallGapItem] = Field(default_factory=list)
    recommended_partners: List["ConsortiumPartnerProfile"] = Field(default_factory=list)
    post_consortium_recommendation: str = "NOT_ASSESSED"
    post_consortium_score: Optional[float] = None
    actionable_summary: str = ""


class ComplianceMatrixRow(BaseModel):
    sl_no: int
    document_name: str
    page_number: Optional[int] = None
    clause_id: str
    requirement_summary: str
    compliance_status: str
    bidder_proof_and_datasheet_mapping: str
    deviation_statement: str = ""


class StatutoryAffidavitDraft(BaseModel):
    doc_code: str
    title: str
    governing_statute: str
    content_markdown: str


class ComplianceAndBinderPackage(BaseModel):
    compliance_rows: List[ComplianceMatrixRow] = Field(default_factory=list)
    has_material_deviations: bool = False
    csv_export_string: str = ""
    statutory_affidavits: List[StatutoryAffidavitDraft] = Field(default_factory=list)
    review_note: str = ""


class EMDCapitalOptimizationReport(BaseModel):
    emd_required_inr: float
    is_statutorily_exempt: Optional[bool] = None
    exemption_statute: str = "Not assessed"
    effective_cash_lockup_inr: float
    estimated_lockup_days: Optional[int] = None
    annual_cost_rate_pct: Optional[float] = None
    estimated_opportunity_cost_inr: Optional[float] = None
    portfolio_capital_utilization_pct: Optional[float] = None
    surety_bond_permitted: Optional[bool] = None
    recommended_instrument: str = "CHECK_TENDER_TERMS"
    liquidity_advisory: str


class HistoricalDisqualificationPattern(BaseModel):
    authority_or_portal: str
    common_rejection_trigger: str
    historical_frequency_weight: str = "UNVERIFIED"
    defensive_countermeasure: str
    reference_source: str = ""


class CompetitorForensicsReport(BaseModel):
    target_authority: str
    source_portal: str
    historical_patterns: List[HistoricalDisqualificationPattern] = Field(default_factory=list)
    strategic_bid_advice: str = ""


class StrategyToolkitResponse(BaseModel):
    tender_id: str
    tender_title: str
    source_portal: str
    limitations_note: str
    deterministic_gates: List[GateResult] = Field(default_factory=list)
    prebid_legal_pack: PreBidLegalRepresentationPack
    consortium_recommendation: ConsortiumMatchRecommendation
    compliance_binder: ComplianceAndBinderPackage
    emd_capital_report: EMDCapitalOptimizationReport
    competitor_forensics: CompetitorForensicsReport


class QualificationScorecard(BaseModel):
    """The master output report displayed on frontend and evaluated in benchmarks."""
    tender_id: str
    tender_title: str
    source_portal: str  # "GeM", "CPPP", "BHEL", etc.
    recommendation: str  # "STRONG_BID", "CONDITIONAL_BID", "RED_FLAG_NO_BID"
    score: float  # 0.0 to 5.0
    deterministic_gates: List[GateResult]
    clause_citations: List[ClauseCitation]
    discovered_atc_urls: List[str] = Field(default_factory=list)
    executive_summary: str
    prebid_legal_pack: Optional[PreBidLegalRepresentationPack] = None
    consortium_recommendation: Optional[ConsortiumMatchRecommendation] = None
    compliance_binder: Optional[ComplianceAndBinderPackage] = None
    emd_capital_report: Optional[EMDCapitalOptimizationReport] = None
    competitor_forensics: Optional[CompetitorForensicsReport] = None
