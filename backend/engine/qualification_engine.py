"""
TenderLens - Qualification Engine: Hybrid Scorecard & 5-Pillar Synthesizer (v1.0.1)
=================================================================================
Synthesizes:
1. Precedence DAG conflict resolution (Rank 1 Corr -> Rank 5 Main PDF)
2. Deterministic mathematical gates (pure statutory logic)
3. Safe Uncertainty triage (ambiguous/conflicting clauses -> AMBIGUOUS_MANUAL_REVIEW)
4. Evidence-backed ClauseCitation generation with exact document coordinates
5. Active Execution Pillars A, B, C, D, and E.
"""

import os
import re
import asyncio
import logging
from typing import List, Optional

from backend.config import settings
from contracts.schema import (
    BidderProfile,
    ClauseCitation,
    GateResult,
    QualificationScorecard
)
from backend.services.document_processor import ProcessedClauseChunk
from backend.engine.deterministic_gatekeeper import (
    DeterministicGatekeeper,
    TenderStatutoryCriteria
)
from backend.engine.prebid_legal_generator import PreBidLegalGenerator
from backend.engine.consortium_matchmaker import ConsortiumMatchmaker
from backend.engine.compliance_matrix_engine import ComplianceMatrixEngine
from backend.engine.emd_capital_optimizer import EMDCapitalOptimizer
from backend.engine.competitor_forensics import CompetitorForensicsEngine
from backend.engine.startup_statutory_shield import StartupStatutoryShield
from backend.engine.fair_play_guardian import FairPlayGuardianEngine

logger = logging.getLogger("tenderlens.engine")

FAIR_PLAY_GEMINI_PROMPT_TEMPLATE = """You are the TenderLens v1.1.0 Statutory Fair Play & Technical Equivalence Auditor running on {model_name}.
### 1. BIDDER ZERO-HISTORY PROFILE
- Company: {company_name} ({entity_type})
- DPIIT Recognized Startup: {is_startup} | Udyam Registered MSE: {is_msme}
- 3-Year Avg Turnover: ₹{avg_turnover_lakhs} Lakhs | Years in Business: {years_in_business}
- Held Certifications & Lab Reports: {certifications}
- Local Content (DPIIT Make in India): {local_content_pct}%
### 2. HIERARCHICAL TENDER CLAUSES (PRECEDENCE DAG ORDERED: RANK 1 -> RANK 5)
{formatted_precedence_chunks}
### 3. YOUR AUDIT MANDATE
Analyze the clauses under Indian Public Procurement Law (GFR 2017 Rule 173(i), Rule 170(i), Rule 144(i), MoF DoE OM No. F.20/2/2014-PPD(Pt.) dated 20.09.2016, GeM GTC Clause 4(xiii)(h), and CVC Guidelines) and output ONLY valid JSON matching this exact structure:
{{
  "atc_revokes_startup_mse_exemption": true/false,
  "has_valid_public_safety_or_security_justification": true/false,
  "is_atc_revocation_ab_initio_void_under_gem_gtc_4_xiii_h": true/false,
  "detected_cartel_clauses": [
    {{
      "clause_id": "string",
      "violation_type": "ULTRA_VIRES_STARTUP_MSE_REVOCATION | DISPROPORTIONATE_TURNOVER_RATIO | PROPRIETARY_BRAND_LOCK_WITHOUT_EQUIVALENT | RESTRICTIVE_GEOGRAPHIC_OR_INCUMBENT_LOCK",
      "impugned_excerpt": "string",
      "violated_statute": "string"
    }}
  ],
  "technical_parameter_equivalence_pct": 0.0 to 100.0,
  "recommended_gem_incident_argument": "string"
}}
"""


class QualificationEngine:
    @classmethod
    async def analyze_clauses_with_gemini(
        cls,
        chunks: List[ProcessedClauseChunk],
        bidder: BidderProfile,
        model: Optional[str] = None
    ) -> List[ClauseCitation]:
        """
        Uses Gemini (gemini-3.8-flash) to perform semantic clause
        grounding, conflict detection, and ambiguous exception discovery.
        """
        target_model = model or getattr(settings, "GEMINI_MODEL", "gemini-3.8-flash")
        api_key = getattr(settings, "GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return []

        prompt_chunks = []
        for c in sorted(chunks, key=lambda x: x.precedence_rank)[:8]:
            prompt_chunks.append(f"[{c.document_name} | Pg {c.page_number} | {c.clause_id}]: {c.text_content[:250]}")

        prompt_text = (
            f"You are TenderLens Procurement AI running on {target_model}.\n"
            f"Analyze these Indian tender clauses for Bidder: {bidder.company_name} ({bidder.entity_type}, MSME: {bidder.is_msme_registered}).\n"
            f"Identify if any buyer clauses revoke statutory MSME turnover/experience exemptions, impose proprietary brand locks, "
            f"or introduce conflicting requirements between Corrigenda and ATCs.\n\n"
            f"Clauses:\n" + "\n".join(prompt_chunks) + "\n\n"
            f"Respond concisely with any identified conflict or 'NO_CONFLICT'."
        )

        # 1. Primary: Direct google.genai SDK (optimized for gemini-3.8-flash)
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            loop = asyncio.get_event_loop()
            resp = await loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model=target_model,
                    contents=prompt_text
                )
            )
            content = resp.text.strip() if hasattr(resp, "text") and resp.text else ""
            if content and any(w in content.lower() for w in ["conflict", "revok", "not allowed", "supersede", "ambiguous", "non-compliant", "disqualif"]):
                return [ClauseCitation(
                    document_name=f"Gemini-Audit ({target_model})",
                    page_number=1,
                    clause_id="LLM-Clause-Conflict-Audit",
                    verbatim_text=content[:400],
                    risk_level="HIGH_DISQUALIFIER" if "revok" in content.lower() or "disqualif" in content.lower() else "MEDIUM",
                    status="AMBIGUOUS_MANUAL_REVIEW"
                )]
            return []
        except Exception as e:
            logger.info(f"Direct google.genai call fallback: {e}")

        # 2. Secondary Fallback: LangChain ChatGoogleGenerativeAI
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(
                model=target_model,
                google_api_key=api_key,
                temperature=0.1,
                timeout=15
            )
            resp = await llm.ainvoke(prompt_text)
            content = ""
            raw_content = getattr(resp, "content", resp)
            if isinstance(raw_content, str):
                content = raw_content.strip()
            elif isinstance(raw_content, list):
                parts = []
                for p in raw_content:
                    if isinstance(p, str):
                        parts.append(p)
                    elif isinstance(p, dict) and "text" in p:
                        parts.append(p["text"])
                content = " ".join(parts).strip()
            if content and any(w in content.lower() for w in ["conflict", "revok", "not allowed", "supersede", "ambiguous", "disqualif"]):
                return [ClauseCitation(
                    document_name=f"Gemini-Audit ({target_model})",
                    page_number=1,
                    clause_id="LLM-Clause-Conflict-Audit",
                    verbatim_text=content[:400],
                    risk_level="HIGH_DISQUALIFIER" if "revok" in content.lower() or "disqualif" in content.lower() else "MEDIUM",
                    status="AMBIGUOUS_MANUAL_REVIEW"
                )]
            return []
        except Exception as e:
            logger.info(f"LangChain Gemini clause analysis ({target_model}) fallback: {e}")
            return []

    @classmethod
    def extract_criteria_from_chunks(
        cls,
        chunks: List[ProcessedClauseChunk]
    ) -> tuple[TenderStatutoryCriteria, List[ClauseCitation]]:
        """
        Extracts parameterized criteria and grounds them in specific document chunks
        using Precedence DAG ordering (Rank 1 overrides Rank 5).
        """
        sorted_chunks = sorted(chunks, key=lambda c: c.precedence_rank)

        criteria = TenderStatutoryCriteria()
        citations: List[ClauseCitation] = []

        turnover_regex = re.compile(
            r"(?:turnover|annual\s+turnover)(?:[\s\w,()/-]*?(?:last\s*\d+\s*years?|past\s*\d+\s*years?|3\s*financial\s*years?))?[\s\w,()/-]*?(?:rs\.?|inr|₹)?\s*([\d,.]+)\s*(crore|cr|lakh|lac)?",
            re.IGNORECASE
        )
        experience_regex = re.compile(
            r"(?:(\d+)\s*(?:years?|yrs?)[^\n.]*?(?:experience|past\s+performance)|(?:experience|past\s+performance)[^\n.]*?(\d+)\s*(?:years?|yrs?))",
            re.IGNORECASE
        )
        emd_regex = re.compile(r"(?:emd|earnest\s+money)[^\d]*?(?:rs\.?|inr|₹)?\s*([\d,.]+)", re.IGNORECASE)
        no_exemption_regex = re.compile(r"(?:no\s+exemption|not\s+exempted|exemption\s+not\s+allowed|msme\s+relaxation\s+not\s+allowed|no\s+relaxation)", re.IGNORECASE)
        oem_maf_regex = re.compile(r"(?:manufacturer\s+authorization|maf|oem\s+authorization|oem\s+certificate)", re.IGNORECASE)
        brand_lock_regex = re.compile(r"(?:only\s+make\s+allowed|proprietary\s+brand|no\s+equivalent\s+accepted|strictly\s+as\s+per\s+brand)", re.IGNORECASE)

        turnover_resolved = False
        experience_resolved = False
        exemption_override_resolved = False

        for chunk in sorted_chunks:
            text = chunk.text_content
            bbox_dict = chunk.bbox.model_dump() if chunk.bbox else None

            # 1. Turnover Extraction
            if not turnover_resolved:
                t_match = turnover_regex.search(text)
                if t_match:
                    raw_val = t_match.group(1).replace(",", "")
                    unit = (t_match.group(2) or "").lower()
                    try:
                        val = float(raw_val)
                        if "cr" in unit or "crore" in unit:
                            val *= 100.0
                        criteria.min_annual_turnover_lakhs = val
                        turnover_resolved = True
                        citations.append(ClauseCitation(
                            document_name=chunk.document_name,
                            page_number=chunk.page_number,
                            clause_id=chunk.clause_id,
                            verbatim_text=text[:300],
                            risk_level="MEDIUM",
                            status="COMPLIANT",
                            bbox=bbox_dict
                        ))
                    except ValueError:
                        pass

            # 2. Check for MSME Exemption Revocation Traps
            if not exemption_override_resolved and no_exemption_regex.search(text):
                criteria.is_turnover_exemption_revoked_by_atc = True
                criteria.is_experience_exemption_revoked_by_atc = True
                exemption_override_resolved = True
                citations.append(ClauseCitation(
                    document_name=chunk.document_name,
                    page_number=chunk.page_number,
                    clause_id=chunk.clause_id,
                    verbatim_text=text[:300],
                    risk_level="HIGH_DISQUALIFIER",
                    status="NON_COMPLIANT",
                    bbox=bbox_dict
                ))

            # 3. Experience Extraction
            if not experience_resolved:
                e_match = experience_regex.search(text)
                if e_match:
                    try:
                        yrs = int(e_match.group(1) or e_match.group(2))
                        criteria.min_experience_years = yrs
                        experience_resolved = True
                        citations.append(ClauseCitation(
                            document_name=chunk.document_name,
                            page_number=chunk.page_number,
                            clause_id=chunk.clause_id,
                            verbatim_text=text[:300],
                            risk_level="LOW",
                            status="COMPLIANT",
                            bbox=bbox_dict
                        ))
                    except (ValueError, TypeError):
                        pass

            # 4. OEM MAF Detection
            if oem_maf_regex.search(text):
                criteria.oem_authorization_mandatory = True

            # 5. Proprietary Brand Lock Detection
            if brand_lock_regex.search(text):
                criteria.proprietary_brand_lock_detected = True
                criteria.proprietary_brand_details = text[:250]

            # 6. EMD Extraction
            if criteria.emd_amount_inr == 0.0:
                emd_match = emd_regex.search(text)
                if emd_match:
                    try:
                        clean_emd = emd_match.group(1).replace(",", "")
                        criteria.emd_amount_inr = float(clean_emd)
                    except ValueError:
                        pass

        # Detect Common Standard Mandatory Certifications with whole word boundary matching
        cert_keywords = ["ISO-9001", "ISO 9001", "BIS", "CMMI", "CE", "RoHS"]
        full_text = " ".join([c.text_content for c in sorted_chunks])
        for ck in cert_keywords:
            pattern = re.compile(rf"\b{re.escape(ck)}\b", re.IGNORECASE)
            normalized_name = ck.replace(" ", "-").upper()
            if pattern.search(full_text) and normalized_name not in [c.upper() for c in criteria.mandatory_certifications]:
                criteria.mandatory_certifications.append(normalized_name)

        return criteria, citations

    @classmethod
    def evaluate_tender(
        cls,
        tender_id: str,
        tender_title: str,
        source_portal: str,
        bidder_profile: BidderProfile,
        chunks: List[ProcessedClauseChunk],
        explicit_criteria: Optional[TenderStatutoryCriteria] = None,
        discovered_atc_urls: Optional[List[str]] = None,
        gemini_citations: Optional[List[ClauseCitation]] = None
    ) -> QualificationScorecard:
        """
        Executes end-to-end qualification audit + synthesizes all 5 v1.0.1 Strategic Pillars.
        """
        if explicit_criteria:
            criteria = explicit_criteria
            clause_citations: List[ClauseCitation] = []
        else:
            criteria, clause_citations = cls.extract_criteria_from_chunks(chunks)

        if gemini_citations:
            clause_citations.extend(gemini_citations)

        # Run Deterministic Gatekeeper
        gate_results = DeterministicGatekeeper.evaluate(bidder=bidder_profile, tender=criteria)

        # Analyze Failures & Hard Disqualifiers
        hard_failures = [g for g in gate_results if g.is_hard_disqualifier and not g.passed]
        ambiguities = [c for c in clause_citations if c.status == "AMBIGUOUS_MANUAL_REVIEW"]

        if len(hard_failures) > 0:
            recommendation = "RED_FLAG_NO_BID"
            score = max(0.5, 2.0 - (len(hard_failures) * 0.5))
            summary = (
                f"RED FLAG: Bidder is legally or technically disqualified due to {len(hard_failures)} "
                f"unmet mandatory criteria: {', '.join([h.rule_name for h in hard_failures])}. "
                f"Bidding standalone will risk EMD forfeiture and rejection during technical evaluation."
            )
        elif len(ambiguities) > 0 or criteria.is_turnover_exemption_revoked_by_atc:
            recommendation = "CONDITIONAL_BID"
            score = 3.2
            summary = (
                f"CONDITIONAL BID: Financial and experience gates pass, but ambiguous buyer ATC clauses "
                f"or special conditional mandates (such as OEM MAF upload or corrigendum revisions) require clarification prior to bid submission."
            )
        else:
            recommendation = "STRONG_BID"
            passed_count = sum(1 for g in gate_results if g.passed)
            score = round(4.0 + (passed_count / max(len(gate_results), 1) * 1.0), 1)
            score = min(score, 5.0)
            summary = (
                f"STRONG BID: High qualification confidence. Bidder meets or exceeds all turnover, "
                f"experience, EMD exemption, Make in India local content, and mandatory certification requirements."
            )

        # Synthesize the 5 Strategic Differentiator Pillars
        prebid_pack = PreBidLegalGenerator.generate_representation_pack(
            tender_id=tender_id,
            tender_title=tender_title,
            bidder=bidder_profile,
            criteria=criteria,
            gates=gate_results,
            citations=clause_citations
        )
        consortium_rec = ConsortiumMatchmaker.analyze_and_match(
            bidder=bidder_profile,
            criteria=criteria,
            gate_results=gate_results
        )
        compliance_binder = ComplianceMatrixEngine.generate_package(
            tender_id=tender_id,
            tender_title=tender_title,
            bidder=bidder_profile,
            criteria=criteria,
            gates=gate_results,
            citations=clause_citations
        )
        emd_report = EMDCapitalOptimizer.evaluate_capital_risk(
            bidder=bidder_profile,
            criteria=criteria
        )
        forensics_report = CompetitorForensicsEngine.analyze_static_forensics(
            tender_title=tender_title,
            source_portal=source_portal
        )

        # Pillar F (v2.0.0): Startup Statutory Shield — Zero-History-to-First-Win Pipeline
        # Activated automatically for DPIIT startups and MSMEs
        startup_shield_report = None
        if bidder_profile.is_startup_recognized or bidder_profile.is_msme_registered or bidder_profile.competency_profile:
            try:
                startup_shield_report = StartupStatutoryShield.evaluate(
                    bidder=bidder_profile,
                    tender=criteria,
                    tender_id=tender_id,
                    tender_title=tender_title,
                    tender_value_lakhs=criteria.estimated_bid_value_lakhs or 0.0,
                )
                logger.info(
                    f"Startup Shield evaluated for {bidder_profile.company_name}: "
                    f"active={startup_shield_report.is_shield_active}, "
                    f"strength={startup_shield_report.shield_strength_score}/10"
                )
            except Exception as e:
                logger.warning(f"Startup Statutory Shield evaluation failed: {e}")

        # Fair Play & Zero-History Equalizer Engine (v1.1.0)
        shield_audit, fair_play_alerts = FairPlayGuardianEngine.run_startup_statutory_shield(
            tender_id=tender_id,
            tender_title=tender_title,
            bidder=bidder_profile,
            criteria=criteria,
            chunks=chunks,
            citations=clause_citations
        )
        tech_proof, qc_proforma_affidavit = FairPlayGuardianEngine.evaluate_zero_history_competency(
            tender_id=tender_id,
            tender_title=tender_title,
            bidder=bidder_profile,
            criteria=criteria
        )
        mse_match = FairPlayGuardianEngine.match_25pct_mse_subcontracting_quota(
            tender_id=tender_id,
            tender_title=tender_title,
            bidder=bidder_profile,
            criteria=criteria,
            shield_audit=shield_audit
        )

        if qc_proforma_affidavit and not any(a.doc_code == qc_proforma_affidavit.doc_code for a in compliance_binder.statutory_affidavits):
            compliance_binder.statutory_affidavits.append(qc_proforma_affidavit)

        return QualificationScorecard(
            tender_id=tender_id,
            tender_title=tender_title,
            source_portal=source_portal,
            recommendation=recommendation,
            score=score,
            deterministic_gates=gate_results,
            clause_citations=clause_citations,
            discovered_atc_urls=discovered_atc_urls or [],
            executive_summary=summary,
            prebid_legal_pack=prebid_pack,
            consortium_recommendation=consortium_rec,
            compliance_binder=compliance_binder,
            emd_capital_report=emd_report,
            competitor_forensics=forensics_report,
            startup_shield=startup_shield_report,
            startup_exemption_audit=shield_audit,
            technical_equivalence_proof=tech_proof,
            mse_subcontracting_match=mse_match,
            fair_play_violations=fair_play_alerts,
        )

    @classmethod
    async def evaluate_tender_async(
        cls,
        tender_id: str,
        tender_title: str,
        source_portal: str,
        bidder_profile: BidderProfile,
        chunks: List[ProcessedClauseChunk],
        explicit_criteria: Optional[TenderStatutoryCriteria] = None,
        discovered_atc_urls: Optional[List[str]] = None,
        enable_gemini_analysis: bool = True
    ) -> QualificationScorecard:
        """
        Asynchronous pipeline: Augments pure-Python deterministic gates and 5 Pillars with
        Gemini (gemini-3.8-flash) semantic clause and conflict auditing.
        """
        gemini_citations: List[ClauseCitation] = []
        if enable_gemini_analysis and chunks:
            try:
                gemini_citations = await cls.analyze_clauses_with_gemini(
                    chunks=chunks,
                    bidder=bidder_profile
                )
            except Exception as e:
                logger.warning(f"Async Gemini clause audit skipped due to error: {e}")

        return cls.evaluate_tender(
            tender_id=tender_id,
            tender_title=tender_title,
            source_portal=source_portal,
            bidder_profile=bidder_profile,
            chunks=chunks,
            explicit_criteria=explicit_criteria,
            discovered_atc_urls=discovered_atc_urls,
            gemini_citations=gemini_citations
        )