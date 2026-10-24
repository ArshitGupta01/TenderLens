"""
TenderLens - Qualification Engine: Hybrid Scorecard Synthesizer
==============================================================
Synthesizes:
1. Precedence DAG conflict resolution (Rank 1 Corr -> Rank 5 Main PDF)
2. Deterministic mathematical gates (zero math hallucination)
3. Safe Uncertainty triage (ambiguous/conflicting clauses -> AMBIGUOUS_MANUAL_REVIEW)
4. Evidence-backed ClauseCitation generation with exact document coordinates.
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

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

logger = logging.getLogger("tenderlens.engine")


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
            f"Identify if any buyer clauses revoke statutory MSME turnover/experience exemptions or introduce conflicting requirements.\n\n"
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
        # Sort chunks by precedence rank ascending: Rank 1 (Corrigendum) first, Rank 5 last
        sorted_chunks = sorted(chunks, key=lambda c: c.precedence_rank)

        criteria = TenderStatutoryCriteria()
        citations: List[ClauseCitation] = []

        # Robust regexes handling intermediate phrases like 'last 3 years', 'financial years', etc.
        turnover_regex = re.compile(
            r"(?:turnover|annual\s+turnover)(?:[\s\w,()/-]*?(?:last\s*\d+\s*years?|past\s*\d+\s*years?|3\s*financial\s*years?))?[\s\w,()/-]*?(?:rs\.?|inr|₹)?\s*([\d,.]+)\s*(crore|cr|lakh|lac)?",
            re.IGNORECASE
        )
        # Handles both '3 years experience' and 'experience of 3 years'
        experience_regex = re.compile(
            r"(?:(\d+)\s*(?:years?|yrs?)[^\n.]*?(?:experience|past\s+performance)|(?:experience|past\s+performance)[^\n.]*?(\d+)\s*(?:years?|yrs?))",
            re.IGNORECASE
        )
        emd_regex = re.compile(r"(?:emd|earnest\s+money)[^\d]*?(?:rs\.?|inr|₹)?\s*([\d,.]+)", re.IGNORECASE)
        no_exemption_regex = re.compile(r"(?:no\s+exemption|not\s+exempted|exemption\s+not\s+allowed|msme\s+relaxation\s+not\s+allowed|no\s+relaxation)", re.IGNORECASE)
        oem_maf_regex = re.compile(r"(?:manufacturer\s+authorization|maf|oem\s+authorization|oem\s+certificate)", re.IGNORECASE)

        # Track attributes resolved by higher precedence ranks
        turnover_resolved = False
        experience_resolved = False
        exemption_override_resolved = False

        for chunk in sorted_chunks:
            text = chunk.text_content

            # 1. Turnover Extraction
            if not turnover_resolved:
                t_match = turnover_regex.search(text)
                if t_match:
                    raw_val = t_match.group(1).replace(",", "")
                    unit = (t_match.group(2) or "").lower()
                    try:
                        val = float(raw_val)
                        if "cr" in unit or "crore" in unit:
                            val *= 100.0  # Convert Crore to Lakhs
                        criteria.min_annual_turnover_lakhs = val
                        turnover_resolved = True
                        citations.append(ClauseCitation(
                            document_name=chunk.document_name,
                            page_number=chunk.page_number,
                            clause_id=chunk.clause_id,
                            verbatim_text=text[:300],
                            risk_level="MEDIUM",
                            status="COMPLIANT"
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
                    status="NON_COMPLIANT"
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
                            status="COMPLIANT"
                        ))
                    except (ValueError, TypeError):
                        pass

            # 4. OEM MAF Detection
            if oem_maf_regex.search(text):
                criteria.oem_authorization_mandatory = True

            # 5. EMD Extraction
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
        Executes end-to-end qualification audit:
        1. Extracts criteria (or uses explicit)
        2. Evaluates deterministic gates
        3. Integrates Gemini semantic citations (if provided)
        4. Computes recommendation score & executive summary
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
        soft_failures = [g for g in gate_results if not g.is_hard_disqualifier and not g.passed]
        ambiguities = [c for c in clause_citations if c.status == "AMBIGUOUS_MANUAL_REVIEW"]

        # Calculate Score (0.0 to 5.0 scale)
        if len(hard_failures) > 0:
            recommendation = "RED_FLAG_NO_BID"
            score = max(0.5, 2.0 - (len(hard_failures) * 0.5))
            summary = (
                f"RED FLAG: Bidder is legally or technically disqualified due to {len(hard_failures)} "
                f"unmet mandatory criteria: {', '.join([h.rule_name for h in hard_failures])}. "
                f"Bidding will risk EMD forfeiture and rejection during technical evaluation."
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

        return QualificationScorecard(
            tender_id=tender_id,
            tender_title=tender_title,
            source_portal=source_portal,
            recommendation=recommendation,
            score=score,
            deterministic_gates=gate_results,
            clause_citations=clause_citations,
            discovered_atc_urls=discovered_atc_urls or [],
            executive_summary=summary
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
        Asynchronous pipeline: Augments pure-Python deterministic gates with
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

