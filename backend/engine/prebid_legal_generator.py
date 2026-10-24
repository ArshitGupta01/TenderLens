"""Create review questions from parsed tender signals without legal conclusions."""

from typing import List, Optional

from contracts.schema import (
    BidderProfile,
    ClauseCitation,
    PreBidLegalRepresentationPack,
    PreBidRepresentationItem,
)
from backend.engine.deterministic_gatekeeper import TenderStatutoryCriteria


class PreBidLegalGenerator:
    @classmethod
    def generate_representation_pack(
        cls,
        tender_id: str,
        tender_title: str,
        bidder: BidderProfile,
        criteria: TenderStatutoryCriteria,
        citations: List[ClauseCitation],
    ) -> PreBidLegalRepresentationPack:
        items: List[PreBidRepresentationItem] = []

        if (bidder.is_msme_registered or bidder.is_startup_recognized) and (
            criteria.is_turnover_exemption_revoked_by_atc
            or criteria.is_experience_exemption_revoked_by_atc
        ):
            citation = next(
                (item for item in citations if "exemption" in item.verbatim_text.lower()),
                None,
            )
            items.append(cls._review_item(
                query_id=f"REVIEW-{len(items) + 1:02d}",
                category="EXEMPTION_SCOPE_REVIEW",
                question="Please clarify whether the stated exemption applies to this bidder and identify the tender clause and current official policy used to determine its scope.",
                citation=citation,
            ))

        if criteria.proprietary_brand_lock_detected:
            citation = next(
                (
                    item for item in citations
                    if criteria.proprietary_brand_details
                    and criteria.proprietary_brand_details[:60].lower() in item.verbatim_text.lower()
                ),
                None,
            )
            items.append(cls._review_item(
                query_id=f"REVIEW-{len(items) + 1:02d}",
                category="SPECIFICATION_CLARIFICATION",
                question="Please clarify the functional basis for the named product or brand and whether equivalent products may be offered under the tender conditions.",
                citation=citation,
                excerpt=criteria.proprietary_brand_details,
            ))

        for citation in citations:
            if citation.status == "AMBIGUOUS_MANUAL_REVIEW":
                items.append(cls._review_item(
                    query_id=f"REVIEW-{len(items) + 1:02d}",
                    category="CONFLICT_CLARIFICATION",
                    question=f"Please clarify which wording controls for clause {citation.clause_id} and publish the answer through the official tender channel.",
                    citation=citation,
                ))

        note = (
            "These are automated prompts for human review, not legal findings. Check the original tender and current official rules; have procurement counsel review any correspondence before sending."
        )
        if items:
            lines = [
                "# Draft request for clarification",
                "",
                f"Tender: {tender_title} ({tender_id})",
                f"Bidder: {bidder.company_name}",
                "",
                f"> {note}",
                "",
            ]
            for item in items:
                location = item.document_name
                if item.page_number is not None:
                    location += f", page {item.page_number}"
                lines.extend([
                    f"## {item.query_id}: {item.violation_category.replace('_', ' ').title()}",
                    f"Source to verify: {location}, clause {item.clause_reference}",
                    f"Excerpt: {item.impugned_clause_excerpt or 'No excerpt was supplied.'}",
                    item.requested_corrigendum_amendment,
                    "",
                ])
        else:
            lines = [
                "# Draft review note",
                "",
                "No pre-bid clarification prompts were generated from the supplied values and source excerpts.",
                "This does not mean the tender has been fully reviewed or that its terms are legally compliant.",
                "",
                f"> {note}",
            ]

        return PreBidLegalRepresentationPack(
            tender_id=tender_id,
            tender_title=tender_title,
            bidder_company=bidder.company_name,
            total_challenges=len(items),
            representations=items,
            formal_letter_markdown="\n".join(lines),
        )

    @staticmethod
    def _review_item(
        query_id: str,
        category: str,
        question: str,
        citation: Optional[ClauseCitation] = None,
        excerpt: Optional[str] = None,
    ) -> PreBidRepresentationItem:
        return PreBidRepresentationItem(
            query_id=query_id,
            document_name=citation.document_name if citation else "User-entered tender criteria",
            page_number=citation.page_number if citation else None,
            clause_reference=citation.clause_id if citation else "Needs source reference",
            impugned_clause_excerpt=(
                citation.verbatim_text if citation else (excerpt or "No exact source excerpt was supplied.")
            ),
            violation_category=category,
            statutory_authority_cited="Verify any legal reference against current official rules and the complete tender before use.",
            formal_argument="This is a review prompt based on entered data, not a conclusion that a tender clause is unlawful or inapplicable.",
            requested_corrigendum_amendment=question,
        )
