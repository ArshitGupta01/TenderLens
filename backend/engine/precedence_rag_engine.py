"""
TenderLens - Precedence DAG RAG Engine (v1.0.3)
================================================
Eliminates Naive Flat Vector RAG Hallucinations in Public Procurement:
1. Canonical Attribute Categorization (Turnover, Experience, EMD, MII, MAF, Certs, LD, etc.)
2. Versioned Directed Acyclic Graph (DAG) construction with legal precedence ordering:
   - Rank 1: Latest Corrigendum (Corr N)
   - Rank 2: Prior Corrigenda (Corr 1 ... N-1)
   - Rank 3: Buyer Uploaded ATC / RFP Document
   - Rank 4: Buyer Text-Based ATC Clauses
   - Rank 5: Main Tender / GeM Bid PDF
3. Precedence-Aware Retrieval: Strict override of baseline terms by higher-precedence Corrigenda.
4. Safe Uncertainty Detection: Flags conflicting terms at the same rank as AMBIGUOUS_MANUAL_REVIEW.
5. Exact Document Coordinate Provenance & Audit Trail linking back to native PDF bboxes.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
import httpx

from backend.config import settings
from backend.services.document_processor import ProcessedClauseChunk
from contracts.schema import (
    RAGPrecedenceCitation,
    RAGQueryResponse,
    PrecedenceDAGNode,
    PrecedenceDAGEdge,
    PrecedenceDAGGraph
)

logger = logging.getLogger("tenderlens.rag")

# Canonical Category Detection Patterns
CATEGORY_PATTERNS = {
    "TURNOVER": re.compile(r"\b(turnover|annual\s+turnover|financial\s+turnover|average\s+turnover)\b", re.IGNORECASE),
    "EXPERIENCE": re.compile(r"\b(experience|past\s+performance|similar\s+works?|completed\s+contracts?|years\s+in\s+business)\b", re.IGNORECASE),
    "EMD": re.compile(r"\b(emd|earnest\s+money|bid\s+security|surety\s+bond|bank\s+guarantee)\b", re.IGNORECASE),
    "MII_LOCAL_CONTENT": re.compile(r"\b(make\s+in\s+india|local\s+content|class-?[iI]+|dpiit|indigenous)\b", re.IGNORECASE),
    "OEM_MAF": re.compile(r"\b(manufacturer\s+authorization|maf|oem\s+authorization|authorization\s+form|oem\s+undertaking)\b", re.IGNORECASE),
    "CERTIFICATIONS": re.compile(r"\b(iso|bis|cmmi|ce\s+mark|rohs|accreditation|nabl|test\s+certificate)\b", re.IGNORECASE),
    "LIQUIDATED_DAMAGES": re.compile(r"\b(liquidated\s+damages|ld\s+clause|penalty|delayed\s+delivery|delay\s+damages)\b", re.IGNORECASE),
    "ARBITRATION": re.compile(r"\b(arbitration|jurisdiction|dispute\s+resolution|governing\s+law|court\s+of\s+law)\b", re.IGNORECASE),
    "PAYMENT_TERMS": re.compile(r"\b(payment\s+terms?|milestone|advance\s+payment|epbg|performance\s+security|bill\s+submission)\b", re.IGNORECASE),
}


class PrecedenceRAGEngine:
    """Precedence-Aware Directed Acyclic Graph (DAG) RAG Engine for Multi-Document Tenders."""

    @staticmethod
    def classify_clause_category(text: str) -> str:
        """Classifies a clause chunk into a canonical procurement category."""
        for cat, pattern in CATEGORY_PATTERNS.items():
            if pattern.search(text):
                return cat
        return "GENERAL"

    @classmethod
    def index_chunks(cls, chunks: List[ProcessedClauseChunk]) -> List[RAGPrecedenceCitation]:
        """
        Converts raw clause chunks into indexed RAG citations with canonical categories
        and default precedence states.
        """
        indexed: List[RAGPrecedenceCitation] = []
        for c in chunks:
            cat = cls.classify_clause_category(c.text_content)
            bbox_dict = None
            if c.bbox:
                bbox_dict = {
                    "x0": c.bbox.x0,
                    "y0": c.bbox.y0,
                    "x1": c.bbox.x1,
                    "y1": c.bbox.y1
                }
            indexed.append(RAGPrecedenceCitation(
                document_name=c.document_name,
                precedence_rank=c.precedence_rank,
                page_number=c.page_number,
                clause_id=c.clause_id,
                verbatim_text=c.text_content,
                category=cat,
                bbox=bbox_dict,
                is_superseded=False,
                superseded_by=None
            ))
        return indexed

    @classmethod
    def resolve_precedence_dag(
        cls,
        citations: List[RAGPrecedenceCitation]
    ) -> Tuple[List[RAGPrecedenceCitation], List[PrecedenceDAGEdge], int, int]:
        """
        Applies Precedence DAG mechanics across all indexed citations:
        - When chunks target the same category across documents:
          Lower rank number (e.g. Rank 1 Corrigendum) strictly supersedes higher rank number (Rank 5 Main PDF).
        - Identifies conflicts and marks superseded nodes.
        """
        # Group by category (ignoring general unless explicitly checked)
        category_map: Dict[str, List[RAGPrecedenceCitation]] = {}
        for cit in citations:
            if cit.category != "GENERAL":
                category_map.setdefault(cit.category, []).append(cit)

        edges: List[PrecedenceDAGEdge] = []
        total_overrides = 0
        detected_conflicts = 0

        for cat, group in category_map.items():
            if len(group) < 2:
                continue

            # Sort group by precedence rank ascending: Rank 1 first, Rank 5 last
            sorted_group = sorted(group, key=lambda x: x.precedence_rank)
            top_citation = sorted_group[0]

            for lower_citation in sorted_group[1:]:
                if lower_citation.precedence_rank > top_citation.precedence_rank:
                    # Valid legal supersession: Corrigendum overrides baseline
                    lower_citation.is_superseded = True
                    lower_citation.superseded_by = f"{top_citation.document_name} ({top_citation.clause_id})"
                    total_overrides += 1
                    edges.append(PrecedenceDAGEdge(
                        source_node_id=f"{top_citation.document_name}:{top_citation.clause_id}",
                        target_node_id=f"{lower_citation.document_name}:{lower_citation.clause_id}",
                        relation_type="SUPERSEDES",
                        explanation=f"{top_citation.document_name} (Rank {top_citation.precedence_rank}) supersedes {lower_citation.document_name} (Rank {lower_citation.precedence_rank}) for {cat} requirement."
                    ))
                elif lower_citation.precedence_rank == top_citation.precedence_rank:
                    # Same rank contradiction -> Safe Uncertainty Rule
                    detected_conflicts += 1
                    edges.append(PrecedenceDAGEdge(
                        source_node_id=f"{top_citation.document_name}:{top_citation.clause_id}",
                        target_node_id=f"{lower_citation.document_name}:{lower_citation.clause_id}",
                        relation_type="CONFLICTS_WITH",
                        explanation=f"Ambiguous conflict between two clauses at the same precedence rank ({top_citation.precedence_rank}) for {cat}."
                    ))

        return citations, edges, total_overrides, detected_conflicts

    @classmethod
    def build_dag_graph(
        cls,
        tender_id: str,
        chunks: List[ProcessedClauseChunk]
    ) -> PrecedenceDAGGraph:
        """Constructs the complete visual Precedence DAG topology for a tender corpus."""
        indexed = cls.index_chunks(chunks)
        resolved_citations, edges, overrides, conflicts = cls.resolve_precedence_dag(indexed)

        nodes: List[PrecedenceDAGNode] = []
        for cit in resolved_citations:
            nodes.append(PrecedenceDAGNode(
                node_id=f"{cit.document_name}:{cit.clause_id}",
                document_name=cit.document_name,
                precedence_rank=cit.precedence_rank,
                clause_id=cit.clause_id,
                category=cit.category,
                page_number=cit.page_number,
                text_snippet=cit.verbatim_text[:160] + "..." if len(cit.verbatim_text) > 160 else cit.verbatim_text,
                bbox=cit.bbox
            ))

        return PrecedenceDAGGraph(
            tender_id=tender_id,
            nodes=nodes,
            edges=edges,
            total_overrides=overrides,
            detected_conflicts=conflicts
        )

    @classmethod
    def query(
        cls,
        tender_id: str,
        query_str: str,
        chunks: List[ProcessedClauseChunk],
        canonical_category: Optional[str] = None
    ) -> RAGQueryResponse:
        """
        Executes Precedence-Aware RAG retrieval:
        1. Classifies query intent to canonical category.
        2. Retrieves candidate clauses and indexes into DAG.
        3. Identifies the winning precedent citation (highest precedence / lowest rank).
        4. Provides the full audit trail showing which baseline clauses were superseded.
        5. Synthesizes a legally defensible answer.
        """
        target_category = canonical_category or cls.classify_clause_category(query_str)
        indexed = cls.index_chunks(chunks)
        resolved_citations, edges, overrides, conflicts = cls.resolve_precedence_dag(indexed)

        # Keyword tokens from query for relevance scoring
        query_tokens = set(re.findall(r"\w+", query_str.lower()))

        def score_citation(cit: RAGPrecedenceCitation) -> float:
            score = 0.0
            if cit.category == target_category and target_category != "GENERAL":
                score += 50.0
            text_tokens = set(re.findall(r"\w+", cit.verbatim_text.lower()))
            overlap = len(query_tokens.intersection(text_tokens))
            score += overlap * 5.0
            # Precedence boost: Lower rank gets higher priority
            score += (6 - cit.precedence_rank) * 10.0
            return score

        scored = [(score_citation(c), c) for c in resolved_citations]
        scored.sort(key=lambda x: x[0], reverse=True)

        matching_citations = [c for score, c in scored if score > 10.0]

        if not matching_citations:
            # Fallback to general search
            matching_citations = resolved_citations

        winning_citation: Optional[RAGPrecedenceCitation] = None
        audit_trail: List[RAGPrecedenceCitation] = []
        conflict_detected = False
        precedence_applied = False

        if matching_citations:
            # Find the top un-superseded citation with highest precedence (lowest rank)
            un_superseded = [c for c in matching_citations if not c.is_superseded]
            un_superseded.sort(key=lambda x: x.precedence_rank)
            winning_citation = un_superseded[0] if un_superseded else matching_citations[0]

            # Audit trail consists of all related clauses ordered by rank to display supersession
            same_category = [c for c in resolved_citations if c.category == winning_citation.category]
            if len(same_category) <= 1 and len(resolved_citations) > 1:
                same_category = resolved_citations
            audit_trail = sorted(same_category, key=lambda x: x.precedence_rank)

            if len(audit_trail) > 1:
                precedence_applied = True
                ranks = [c.precedence_rank for c in audit_trail]
                if len(ranks) != len(set(ranks)):
                    conflict_detected = True

        # Synthesize Answer
        if not winning_citation:
            answer = (
                f"No specific clause regarding '{query_str}' was identified in the provided tender documents. "
                f"Please review the uploaded technical specifications and ATC annexures manually."
            )
        else:
            answer_parts = [
                f"**Operative Clause ({winning_citation.document_name}, Page {winning_citation.page_number}, Clause {winning_citation.clause_id})**:",
                f"> \"{winning_citation.verbatim_text.strip()}\"",
                f"\n**Legal Precedence**: Rank {winning_citation.precedence_rank} "
                f"({'Latest Corrigendum - Supersedes prior terms' if winning_citation.precedence_rank == 1 else 'Active Controlling Provision'})."
            ]

            if precedence_applied and len(audit_trail) > 1:
                superseded_citations = [c for c in audit_trail if c.is_superseded]
                if superseded_citations:
                    answer_parts.append("\n**Precedence Audit Trail (Superseded Baseline Terms)**:")
                    for s in superseded_citations:
                        answer_parts.append(
                            f"- *{s.document_name}* (Page {s.page_number}, Cl {s.clause_id}, Rank {s.precedence_rank}): "
                            f"\"{s.verbatim_text[:120]}...\" [SUPERSEDED by {winning_citation.document_name}]"
                        )

            if conflict_detected:
                answer_parts.append(
                    "\n⚠️ **Safe Uncertainty Warning**: Conflicting clauses detected at the same precedence level. "
                    "This ambiguity should be raised during the pre-bid clarification meeting."
                )

            answer = "\n".join(answer_parts)

        return RAGQueryResponse(
            tender_id=tender_id,
            query=query_str,
            answer=answer,
            winning_citation=winning_citation,
            audit_trail=audit_trail,
            conflict_detected=conflict_detected,
            precedence_applied=precedence_applied,
            confidence_score=0.95 if winning_citation and not conflict_detected else 0.70
        )

    @classmethod
    async def query_with_gemini(
        cls,
        tender_id: str,
        query_str: str,
        chunks: List[ProcessedClauseChunk],
        canonical_category: Optional[str] = None
    ) -> RAGQueryResponse:
        """
        Augments deterministic precedence retrieval with Google Gemini (gemini-3.8-flash)
        for nuanced natural-language synthesis.
        """
        # First obtain deterministic precedence answer
        base_resp = cls.query(
            tender_id=tender_id,
            query_str=query_str,
            chunks=chunks,
            canonical_category=canonical_category
        )

        if not settings.GEMINI_API_KEY or not base_resp.winning_citation:
            return base_resp

        try:
            prompt = (
                f"You are the TenderLens Precedence DAG RAG Legal Assistant (v1.0.3) for Indian Public Procurement.\n\n"
                f"User Question: {query_str}\n\n"
                f"Controlling Winning Precedent (Rank {base_resp.winning_citation.precedence_rank}):\n"
                f"Document: {base_resp.winning_citation.document_name} (Page {base_resp.winning_citation.page_number}, Clause {base_resp.winning_citation.clause_id})\n"
                f"Text: {base_resp.winning_citation.verbatim_text}\n\n"
                f"Superseded Prior Versions / Audit Trail:\n"
                + "\n".join([f"- {a.document_name} (Rank {a.precedence_rank}): {a.verbatim_text[:150]}" for a in base_resp.audit_trail if a.is_superseded])
                + f"\n\nPrecedence Override Applied: {base_resp.precedence_applied}\n"
                f"Conflict Detected: {base_resp.conflict_detected}\n\n"
                f"Provide a clear, legally precise answer (3-4 concise paragraphs) explaining the operative requirement, "
                f"how Corrigenda/ATC precedence resolved the rule, exact page citations, and any pre-bid action advice for the bidder."
            )

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": 600}
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        llm_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        if llm_text:
                            base_resp.answer = llm_text
        except Exception as e:
            logger.warning(f"Gemini RAG synthesis fallback to deterministic response: {e}")

        return base_resp
