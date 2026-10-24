"""
TenderLens Shared Contract Schema (Pydantic & JSON) — v2.0.0
============================================================
This file defines the shared contract between Research/Evaluation (Argon)
and Backend/Frontend Engineering (Mohit & Arshit).

Rule: All additions use safe default factories to remain 100% backwards
compatible with baseline tests and callers.

v2.0.0 Additions (Zero-History Pipeline):
- ZeroHistoryCompetencyProfile  : Alternative evidence map for DPIIT startups
- MSESubcontractingOpportunity  : PPP-2012 Section 4 mandatory 25% subcontracting
- StartupRunwayTender           : GeM/CPPP tenders accessible to zero-history firms
- BidderProfile.competency_profile (optional, backwards-compatible)
"""

from typing import List, Optional, Dict, Any, Literal
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


# ---------------------------------------------------------------------------
# v2.0.0 — Zero-History Pipeline: Alternative Competency Evidence
# ---------------------------------------------------------------------------

class ZeroHistoryCompetencySignal(BaseModel):
    """A single piece of alternative competency evidence for a zero-history startup."""
    signal_type: str  # "NABL_ACCREDITATION", "STQC_CERT", "DPIIT_RECOGNITION", "IP_PATENT",
                      # "INCUBATOR_LETTER", "GEM_SELLER_RATING", "PILOT_PROJECT", "AWARD"
    evidence_id: str  # Certificate number, patent number, recognition number, etc.
    issuing_authority: str  # "NABL", "STQC", "MeitY", "DPIIT", "IIT Delhi Incubation Cell", etc.
    validity_date: Optional[str] = None  # ISO date string "YYYY-MM-DD"
    statutory_exemption_mapped: str = ""  # e.g. "GFR Rule 173(i) — Startup Turnover Waiver"
    trust_tier: int = 1  # 1 = Highest (NABL/STQC), 2 = High (DPIIT/IP), 3 = Medium (Incubator)
    description: str = ""


class ZeroHistoryCompetencyProfile(BaseModel):
    """
    Alternative evidence map replacing financial history for DPIIT-recognized startups.
    Implements the 'Startup Statutory Shield' — a zero-history bidder proves capability
    through technical certifications and statutory recognition rather than balance sheets.

    Legal Basis:
    - GFR 2017 Rule 173(i): Central Government may relax prior turnover/experience for startups
    - DPIIT Startup India Procurement Policy: Allows GoI entities to procure from recognized startups
    - MoF OM F.20/2/2014-PPD: Prohibits buyers from imposing conditions beyond GFR
    """
    dpiit_recognition_number: Optional[str] = Field(
        default=None,
        description="DPIIT Startup India recognition certificate number (e.g. DIPP12345)"
    )
    dpiit_recognition_date: Optional[str] = Field(
        default=None,
        description="ISO date YYYY-MM-DD of DPIIT recognition grant"
    )
    years_since_incorporation: int = Field(
        default=0,
        description="Company age in years (must be <= 10 for startup status under DPIIT)"
    )
    competency_signals: List[ZeroHistoryCompetencySignal] = Field(
        default_factory=list,
        description="Ordered list of alternative evidence signals (NABL, STQC, IP, incubator, etc.)"
    )
    gem_seller_rating: Optional[float] = Field(
        default=None,
        ge=0.0, le=5.0,
        description="Current GeM seller rating (0–5), if registered on GeM portal"
    )
    incubator_name: Optional[str] = Field(
        default=None,
        description="Name of recognized incubator (IIT/NIT/NASSCOM/FICCI/SIDBI)"
    )
    pilot_project_count: int = Field(
        default=0,
        description="Number of documented pilot projects (PoC letters from govt/PSU accepted)"
    )
    # Computed fields (populated by StartupStatutoryShield engine)
    applicable_exemptions: List[str] = Field(
        default_factory=list,
        description="Statutory exemptions provably applicable to this bidder"
    )
    shield_strength_score: float = Field(
        default=0.0,
        ge=0.0, le=10.0,
        description="0-10 shield strength: how robustly the bidder can invoke startup exemptions"
    )
    shield_override_risk: str = Field(
        default="UNKNOWN",
        description="SAFE / ATC_OVERRIDE_RISK / SHIELD_FULLY_BLOCKED"
    )


class MSESubcontractingOpportunity(BaseModel):
    """
    An opportunity for a zero-history MSE/startup to obtain work via mandatory
    25% MSE subcontracting under PPP-MSE Order 2012, Section 4.

    When a startup cannot bid directly on a large tender, prime contractors who win
    that tender are legally required to subcontract ≥25% of the contract value to MSEs.
    TenderLens surfaces these opportunities to zero-history firms.
    """
    tender_title: str
    tender_id: str
    tender_estimated_value_lakhs: float
    mandatory_mse_share_lakhs: float  # 25% of tender value
    domain_category: str  # "IT_SERVICES", "CIVIL", "GOODS_SUPPLY", "CONSULTING"
    domain_match_score: float = Field(ge=0.0, le=1.0)  # How well startup matches
    statutory_basis: str = "Public Procurement Policy for MSEs Order 2012, Section 4"
    prime_contractor_guidance: str = ""  # What to say to the prime contractor
    outreach_template: str = ""  # Auto-generated pitch message


class StartupRunwayTender(BaseModel):
    """
    A tender identified as accessible to zero-history DPIIT-recognized startups.
    These tenders have explicitly relaxed norms under GeM Startup Policy or GFR 173(i).
    """
    tender_id: str
    title: str
    estimated_value_lakhs: float
    portal: str  # "GeM", "CPPP", "BHEL", etc.
    startup_accessibility_score: float = Field(ge=0.0, le=10.0)  # 10 = fully accessible
    accessibility_factors: List[str] = Field(default_factory=list)
    blocking_factors: List[str] = Field(default_factory=list)
    recommended_action: str  # "DIRECT_BID", "CONSORTIUM_BID", "SUBCONTRACT_SEEK"
    shield_applicable: bool = False


class StartupShieldReport(BaseModel):
    """Full output of the Startup Statutory Shield analysis engine."""
    company_name: str
    is_shield_active: bool
    shield_strength_score: float  # 0-10
    shield_override_risk: str  # SAFE / ATC_OVERRIDE_RISK / SHIELD_FULLY_BLOCKED
    statutory_basis_summary: str
    applicable_exemptions: List[str] = Field(default_factory=list)
    competency_evidence_map: List[ZeroHistoryCompetencySignal] = Field(default_factory=list)
    runway_tenders: List[StartupRunwayTender] = Field(default_factory=list)
    subcontracting_opportunities: List[MSESubcontractingOpportunity] = Field(default_factory=list)
    pre_bid_shield_letter: str = ""  # Auto-generated legal letter invoking GFR 173(i)
    actionable_next_steps: List[str] = Field(default_factory=list)


# ===========================================================================
# v1.1.0 ADDITIONS TO contracts/schema.py — FAIR PLAY & ZERO-HISTORY EQUALIZER
# ===========================================================================

class LabTestReportItem(BaseModel):
    """Third-party laboratory or statutory quality test certificate held by a zero-history bidder."""
    certificate_id: str = Field(description="e.g., NABL-TC-2026-8841, STQC-IOT-402, BIS-CM/L-7712")
    issuing_agency: str = Field(description="e.g., NABL Accredited Lab, STQC MeitY, BIS, CSIR, CPRI")
    standard_tested: str = Field(description="e.g., IS 13252 (Part 1), IEC 60947-2, ISO/IEC 27001")
    product_or_model_covered: str
    issue_date: str = "2026-06-15"
    is_valid_and_active: bool = True
    parameter_match_score_pct: float = Field(default=100.0, ge=0.0, le=100.0)


class FairPlayViolationAlert(BaseModel):
    """Alert flagging anti-competitive, cartel-driven, or statutorily void buyer clauses."""
    alert_id: str
    violation_type: Literal[
        "ULTRA_VIRES_STARTUP_MSE_REVOCATION",
        "DISPROPORTIONATE_TURNOVER_RATIO",
        "PROPRIETARY_BRAND_LOCK_WITHOUT_EQUIVALENT",
        "RESTRICTIVE_GEOGRAPHIC_OR_INCUMBENT_LOCK",
        "FOREIGN_CERTIFICATION_WITHOUT_INDIAN_STANDARD",
        "ILLEGAL_EMD_DEMAND_ON_EXEMPT_ENTITY"
    ]
    severity: Literal["CRITICAL", "HIGH", "MODERATE"] = "CRITICAL"
    source_document: str
    page_number: int = 1
    clause_id: str
    impugned_text: str
    violated_statute: str = Field(
        description="Exact rule violated, e.g., GeM GTC Clause 4(xiii)(h), GFR 2017 Rule 173(i), CVC OM 12-02-1-CTE-6"
    )
    is_clause_ab_initio_void: bool = True
    cartel_risk_index: float = Field(default=0.85, ge=0.0, le=1.0)
    recommended_remedy: str


class StartupExemptionAudit(BaseModel):
    """Audit output of the Startup Statutory Shield (Feature 1A)."""
    bidder_company: str
    is_dpiit_startup: bool
    dpiit_recognition_number: Optional[str] = "DIPP-STARTUP-REC-94182"
    is_udyam_msme: bool
    msme_category: Optional[str] = None  # MICRO, SMALL, MEDIUM
    bidder_role_eligible_for_exemption: bool = True
    gem_bid_baseline_grants_exemption: bool = True
    atc_attempts_revocation: bool = False
    is_public_safety_or_national_security_tender: bool = False
    has_competent_authority_prior_approval: bool = False
    revocation_legally_valid: bool = False
    statutory_shield_invoked: bool = False
    governing_statutes: List[str] = Field(
        default_factory=lambda: [
            "GFR 2017 Rule 173(i) (Startup & MSE Prior Turnover/Experience Relaxation)",
            "MoF DoE OM No. F.20/2/2014-PPD(Pt.) dated 25.07.2016 & 20.09.2016",
            "GeM General Terms & Conditions (GTC) Clause 4(xiii)(h) & Clause 4(xxii)",
            "GFR 2017 Rule 170(i) (100% EMD Waiver for Startups & MSEs)"
        ]
    )
    turnover_waived_lakhs: float = 0.0
    experience_waived_years: int = 0
    emd_waived_inr: float = 0.0
    audit_verdict: Literal[
        "EXEMPTION_GRANTED_CLEAN",
        "ILLEGAL_ATC_REVOCATION_OVERRIDDEN_BY_SHIELD",
        "LAWFUL_SAFETY_SECURITY_EXCEPTION_APPLIES",
        "INELIGIBLE_ENTITY_OR_TRADER_EXCLUSION"
    ] = "EXEMPTION_GRANTED_CLEAN"
    legal_shield_summary: str


class TechnicalEquivalenceProof(BaseModel):
    """Output of the Zero-History Competency Engine (Feature 1B) proving capability without balance sheets."""
    is_zero_history_bidder: bool = True
    overall_competency_score: float = Field(ge=0.0, le=100.0, description="Composite score out of 100")
    qualifies_for_technical_equivalence: bool = True
    lab_and_standards_score: float = Field(default=40.0, ge=0.0, le=40.0)
    plant_and_capacity_score: float = Field(default=25.0, ge=0.0, le=25.0)
    ip_and_mii_content_score: float = Field(default=20.0, ge=0.0, le=20.0)
    founder_pedigree_score: float = Field(default=15.0, ge=0.0, le=15.0)
    verified_lab_reports: List[LabTestReportItem] = Field(default_factory=list)
    matched_tender_specifications: List[str] = Field(default_factory=list)
    proforma_for_equipment_and_qc_markdown: str = Field(
        default="",
        description="Auto-drafted statutory Annexure: Proforma for Equipment and Quality Control under MoF OM F.20/2/2014-PPD"
    )
    evaluator_justification_note: str


class MSESubcontractingMatch(BaseModel):
    """Output of the Mandatory 25% MSE Subcontracting & Split-Order Quota Gateway (Feature 1C)."""
    eligible_for_25pct_mse_quota: bool = True
    governing_policy: str = "Public Procurement Policy for Micro and Small Enterprises (MSEs) Order, 2012 (as amended)"
    estimated_tender_value_lakhs: float = 0.0
    mandatory_25pct_allocation_lakhs: float = 0.0
    sc_st_mse_subquota_applicable: bool = False
    l1_plus_15pct_price_preference_eligible: bool = True
    recommended_entry_mode: Literal[
        "DIRECT_BID_WITH_L1_PLUS_15_SPLIT_RIGHT",
        "MANDATORY_25PCT_EPC_SUBCONTRACTOR",
        "CLASS_I_MII_COMPONENT_OEM_PARTNER"
    ] = "DIRECT_BID_WITH_L1_PLUS_15_SPLIT_RIGHT"
    matched_prime_epc_partner: Optional[ConsortiumPartnerProfile] = None
    subcontract_scope_description: str = ""
    tripartite_mou_draft_markdown: str = ""


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

    # --- v2.0.0 Zero-History Pipeline (Backwards-Compatible, Optional) ---
    competency_profile: Optional[ZeroHistoryCompetencyProfile] = Field(
        default=None,
        description="Alternative competency evidence for DPIIT-recognized startups with zero financial history"
    )

    # --- v1.1.0 Fair Play & Zero-History Additions ---
    dpiit_recognition_number: Optional[str] = Field(default="DIPP-STARTUP-REC-94182")
    founder_domain_experience_years: int = Field(default=5, ge=0, le=60)
    held_patents_count: int = Field(default=1, ge=0)
    lab_test_reports: List[LabTestReportItem] = Field(default_factory=list)
    plant_and_machinery_valuation_lakhs: float = Field(default=35.0, ge=0.0)
    max_monthly_production_capacity_units: int = Field(default=500, ge=0)
    is_sc_st_owned_mse: bool = False


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

    # --- v2.0.0 Pillar F: Startup Statutory Shield (Zero-History Pipeline) ---
    startup_shield: Optional["StartupShieldReport"] = Field(
        default=None,
        description=(
            "Startup Statutory Shield — activated for DPIIT-recognised startups and MSMEs. "
            "Maps zero-history firms to GFR 173(i) exemptions, detects ATC override risk, "
            "surfaces MSE 25% subcontracting opportunities under PPP-MSE Order 2012."
        )
    )

    # --- v1.1.0 Fair Play & Zero-History Equalizer Outputs ---
    startup_exemption_audit: Optional[StartupExemptionAudit] = None
    technical_equivalence_proof: Optional[TechnicalEquivalenceProof] = None
    mse_subcontracting_match: Optional[MSESubcontractingMatch] = None
    fair_play_violations: List[FairPlayViolationAlert] = Field(default_factory=list)


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

    # --- v1.1.0 Fair Play & Zero-History Equalizer Outputs ---
    startup_exemption_audit: Optional[StartupExemptionAudit] = None
    technical_equivalence_proof: Optional[TechnicalEquivalenceProof] = None
    mse_subcontracting_match: Optional[MSESubcontractingMatch] = None
    fair_play_violations: List[FairPlayViolationAlert] = Field(default_factory=list)


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