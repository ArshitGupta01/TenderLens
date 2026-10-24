"""
TenderLens Shared Contract Schema (Pydantic & JSON) — v1.0.3
============================================================
This file defines the shared contract between Research/Evaluation (Argon)
and Backend/Frontend Engineering (Mohit & Arshit).

Rule: All v1.0.3 additions use safe default factories to remain 100% backwards
compatible with baseline tests and callers.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ConsortiumPartnerProfile(BaseModel):
    """Partner entity profile for Joint Venture (JV) or Consortium bidding (Pillar B)."""
    partner_id: str
    company_name: str
    entity_type: str  # OEM, Manufacturer, EPC, System Integrator, MSME
    role_in_consortium: str = "TECH_OR_FIN_PARTNER"  # LEAD_MEMBER, OEM_PARTNER, FINANCIAL_PARTNER, TECH_SPECIALIST
    is_msme_registered: bool = False
    avg_annual_turnover_lakhs: float = 0.0
    years_in_business: int = 0
    highest_single_project_value_lakhs: float = 0.0
    local_content_percentage: float = 50.0
    held_certifications: List[str] = Field(default_factory=list)
    synergy_rationale: str = ""


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

    # --- v1.0.1 Optional Extensions (Backwards-Compatible Defaults) ---
    past_similar_project_values_lakhs: List[float] = Field(
        default_factory=list,
        description="Completed similar project values (in ₹ Lakhs) over last 7 years for CPWD 80/50/40 check"
    )
    available_emd_working_capital_inr: float = Field(
        default=2500000.0,
        description="Liquid working capital available for EMD/BG allocation in INR (default ₹25 Lakhs)"
    )
    active_simultaneous_bids_count: int = Field(
        default=1,
        description="Number of concurrent tenders where bidder has locked or plans to lock EMD"
    )
    consortium_partners: List[ConsortiumPartnerProfile] = Field(
        default_factory=list,
        description="Optional JV / Consortium partner entities evaluated jointly"
    )


class ClauseCitation(BaseModel):
    """Evidence anchor linking findings to exact source coordinates."""
    document_name: str  # e.g., "Main_Tender.pdf", "Buyer_ATC.pdf", "Corrigendum_1.pdf"
    page_number: int
    clause_id: str
    verbatim_text: str
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH_DISQUALIFIER
    status: str = "COMPLIANT"  # COMPLIANT, NON_COMPLIANT, CONDITIONAL, AMBIGUOUS_MANUAL_REVIEW
    bbox: Optional[Dict[str, float]] = None  # Optional {"x0": ..., "y0": ..., "x1": ..., "y1": ...}


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


# ---------------------------------------------------------------------------
# Pillar A: Pre-Bid Query & Legal Pushback Models
# ---------------------------------------------------------------------------
class PreBidRepresentationItem(BaseModel):
    """Single actionable pre-bid query or legal challenge to a restrictive clause."""
    query_id: str
    document_name: str
    page_number: Optional[int] = 1
    clause_reference: str
    impugned_clause_excerpt: str
    violation_category: str  # e.g., "ILLEGAL_MSME_REVOCATION", "PROPRIETARY_BRAND_LOCK", "DISPROPORTIONATE_TURNOVER", "CORRIGENDUM_CONTRADICTION"
    statutory_authority_cited: str  # e.g., "MoF OM No. F.20/2/2014-PPD & GFR 2017 Rule 173(i)"
    formal_argument: str
    requested_corrigendum_amendment: str


class PreBidLegalRepresentationPack(BaseModel):
    """Complete pre-bid clarification & legal representation package."""
    tender_id: str
    tender_title: str
    bidder_company: str
    total_challenges: int
    representations: List[PreBidRepresentationItem] = Field(default_factory=list)
    formal_letter_markdown: str = ""


# ---------------------------------------------------------------------------
# Pillar B: Dynamic Consortium & Partner Matching Models
# ---------------------------------------------------------------------------
class ShortfallGapItem(BaseModel):
    """Quantified eligibility shortfall that can be bridged via a JV/Consortium."""
    gate_name: str
    shortfall_type: str  # "TURNOVER_GAP", "EXPERIENCE_GAP", "OEM_MAF_REQUIRED", "CERTIFICATION_GAP", "MII_LOCAL_CONTENT_GAP"
    bidder_current_value: Any
    tender_required_value: Any
    numerical_gap_lakhs_or_years: float = 0.0
    bridging_strategy: str


class ConsortiumMatchRecommendation(BaseModel):
    """Actionable consortium recommendation transforming a No-Bid into a Strong Bid."""
    has_shortfall: bool
    identified_gaps: List[ShortfallGapItem] = Field(default_factory=list)
    recommended_partners: List[ConsortiumPartnerProfile] = Field(default_factory=list)
    post_consortium_recommendation: str = "STRONG_BID"
    post_consortium_score: Optional[float] = 4.8
    actionable_summary: str = ""


# ---------------------------------------------------------------------------
# Pillar C: Automated Compliance Matrix, Deviation & Statutory Affidavits
# ---------------------------------------------------------------------------
class ComplianceMatrixRow(BaseModel):
    """Single row of a portal-ready Technical/Commercial Compliance & Deviation Matrix."""
    sl_no: int
    document_name: str
    page_number: Optional[int] = 1
    clause_id: str
    requirement_summary: str
    compliance_status: str  # "COMPLIED", "DEVIATION", "CLARIFICATION_REQUIRED"
    bidder_proof_and_datasheet_mapping: str
    deviation_statement: str = "Nil Deviation — Strictly Complied"


class StatutoryAffidavitDraft(BaseModel):
    """Auto-drafted non-price statutory declaration ready for stamp paper / e-Sign."""
    doc_code: str  # "GFR_170_BID_SECURITY", "DPIIT_MII_LOCAL_CONTENT", "GFR_144_XI_LAND_BORDER", "NON_BLACKLISTING", "OEM_MAF_FORMAT"
    title: str
    governing_statute: str
    content_markdown: str


class ComplianceAndBinderPackage(BaseModel):
    """Bundled Compliance Matrix, Deviation Statement, CSV export, and Statutory Affidavits."""
    compliance_rows: List[ComplianceMatrixRow] = Field(default_factory=list)
    has_material_deviations: bool = False
    csv_export_string: str = ""
    statutory_affidavits: List[StatutoryAffidavitDraft] = Field(default_factory=list)
    review_note: str = ""


# ---------------------------------------------------------------------------
# Pillar D: EMD Capital Risk & Surety Bond Optimization Models
# ---------------------------------------------------------------------------
class EMDCapitalOptimizationReport(BaseModel):
    """Working capital risk analysis and Surety Bond / e-BG optimization."""
    emd_required_inr: float
    is_statutorily_exempt: Optional[bool] = False
    exemption_statute: str = "Not assessed"
    effective_cash_lockup_inr: float = 0.0
    estimated_lockup_days: Optional[int] = 120
    annual_cost_rate_pct: Optional[float] = 12.0
    opportunity_cost_at_12pct_pa_inr: float = 0.0
    estimated_opportunity_cost_inr: Optional[float] = 0.0
    portfolio_capital_utilization_pct: Optional[float] = 0.0
    surety_bond_permitted: Optional[bool] = True
    recommended_instrument: str = "CHECK_TENDER_TERMS"  # "BID_SECURITY_DECLARATION_NIL_COST", "IRDAI_INSURANCE_SURETY_BOND", "NESL_E_BG", "FD_OR_TRADITIONAL_BG"
    liquidity_advisory: str = ""


# ---------------------------------------------------------------------------
# Pillar E: Competitor Disqualification Forensics Models
# ---------------------------------------------------------------------------
class HistoricalDisqualificationPattern(BaseModel):
    """Forensic insight into why bidders get rejected in a specific PSU/portal."""
    authority_or_portal: str
    common_rejection_trigger: str
    historical_frequency_weight: str = "MODERATE"  # "HIGH", "MODERATE", "EMERGING"
    defensive_countermeasure: str
    reference_source: str = ""


class CompetitorForensicsReport(BaseModel):
    """Historical evaluation intelligence for the procuring organization."""
    target_authority: str
    source_portal: str
    historical_patterns: List[HistoricalDisqualificationPattern] = Field(default_factory=list)
    strategic_bid_advice: str = ""


# ---------------------------------------------------------------------------
# Master Output Scorecard (v1.0.1 Core & Strategic Pillars)
# ---------------------------------------------------------------------------
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

    # --- v1.0.1 Active Execution & Strategy Pillars (Optional for backwards compatibility) ---
    prebid_legal_pack: Optional[PreBidLegalRepresentationPack] = None
    consortium_recommendation: Optional[ConsortiumMatchRecommendation] = None
    compliance_binder: Optional[ComplianceAndBinderPackage] = None
    emd_capital_report: Optional[EMDCapitalOptimizationReport] = None
    competitor_forensics: Optional[CompetitorForensicsReport] = None


class StrategyToolkitResponse(BaseModel):
    """Combined strategy response model."""
    tender_id: str
    tender_title: str
    source_portal: str
    limitations_note: str = ""
    deterministic_gates: List[GateResult] = Field(default_factory=list)
    prebid_legal_pack: PreBidLegalRepresentationPack
    consortium_recommendation: ConsortiumMatchRecommendation
    compliance_binder: ComplianceAndBinderPackage
    emd_capital_report: EMDCapitalOptimizationReport
    competitor_forensics: CompetitorForensicsReport


# ---------------------------------------------------------------------------
# Precedence DAG RAG Engine Models (v1.0.3)
# ---------------------------------------------------------------------------
class RAGPrecedenceCitation(BaseModel):
    """Grounding citation for RAG answers with precedence and coordinate metadata."""
    document_name: str
    precedence_rank: int  # 1 = Latest Corr, 2 = Prior Corr, 3 = Buyer ATC, 4 = Text ATC, 5 = Main PDF
    page_number: int
    clause_id: str
    verbatim_text: str
    category: str = "GENERAL"  # TURNOVER, EXPERIENCE, EMD, MII_LOCAL_CONTENT, OEM_MAF, CERTIFICATIONS, LIQUIDATED_DAMAGES, ARBITRATION, PAYMENT_TERMS, GENERAL
    bbox: Optional[Dict[str, float]] = None
    is_superseded: bool = False
    superseded_by: Optional[str] = None


class RAGQueryRequest(BaseModel):
    """Request model for querying the tender corpus via Precedence DAG RAG."""
    tender_id: str = "TENDER-QUERY"
    query: str
    canonical_category: Optional[str] = None
    include_superseded: bool = False


class RAGQueryResponse(BaseModel):
    """Response model returning precedence-grounded answers and audit trails."""
    tender_id: str
    query: str
    answer: str
    winning_citation: Optional[RAGPrecedenceCitation] = None
    audit_trail: List[RAGPrecedenceCitation] = Field(default_factory=list)
    conflict_detected: bool = False
    precedence_applied: bool = False
    confidence_score: float = 1.0


class PrecedenceDAGNode(BaseModel):
    """Node in the Precedence Directed Acyclic Graph representing a clause version."""
    node_id: str
    document_name: str
    precedence_rank: int
    clause_id: str
    category: str
    page_number: int
    text_snippet: str
    bbox: Optional[Dict[str, float]] = None


class PrecedenceDAGEdge(BaseModel):
    """Edge in the Precedence DAG representing supersession or amendment."""
    source_node_id: str
    target_node_id: str
    relation_type: str = "SUPERSEDES"  # "SUPERSEDES", "AMENDS", "CLARIFIES", "CONFLICTS_WITH"
    explanation: str = ""


class PrecedenceDAGGraph(BaseModel):
    """Full Directed Acyclic Graph topology for visualization and audit."""
    tender_id: str
    nodes: List[PrecedenceDAGNode] = Field(default_factory=list)
    edges: List[PrecedenceDAGEdge] = Field(default_factory=list)
    total_overrides: int = 0
    detected_conflicts: int = 0

