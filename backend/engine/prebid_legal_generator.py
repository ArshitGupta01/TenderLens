"""
TenderLens - Pillar A: Automated Pre-Bid Query & Legal Pushback Generator
=========================================================================
Detects restrictive, anti-competitive, or contradictory tender clauses and
auto-drafts formal legal pre-bid representations citing:
1. Ministry of Finance OM No. F.20/2/2014-PPD & GFR 2017 Rule 173(i) (MSME/Startup Exemption)
2. GFR 2017 Rule 144(i) & CVC Guidelines (Prohibition of proprietary brand names)
3. DPIIT Public Procurement (Preference to Make in India) Order, 2017
4. GeM General Terms and Conditions (GTC) Clause 4 (Precedence & Illegal Overrides)
"""

import logging
from datetime import datetime
from typing import List
from contracts.schema import (
    BidderProfile,
    ClauseCitation,
    GateResult,
    PreBidRepresentationItem,
    PreBidLegalRepresentationPack
)
from backend.engine.deterministic_gatekeeper import TenderStatutoryCriteria

logger = logging.getLogger("tenderlens.prebid_legal")


class PreBidLegalGenerator:
    @classmethod
    def generate_representation_pack(
        cls,
        tender_id: str,
        tender_title: str,
        bidder: BidderProfile,
        criteria: TenderStatutoryCriteria,
        gates: List[GateResult],
        citations: List[ClauseCitation]
    ) -> PreBidLegalRepresentationPack:
        """
        Synthesizes all detected statutory violations, unfair restrictions, and
        ATC-vs-Corrigendum ambiguities into a formal Pre-Bid Representation Pack.
        """
        items: List[PreBidRepresentationItem] = []
        counter = 1

        # 1. Check for Illegal Revocation of MSME / Startup Turnover or Experience Relaxation
        if (bidder.is_msme_registered or bidder.is_startup_recognized) and (
            criteria.is_turnover_exemption_revoked_by_atc or criteria.is_experience_exemption_revoked_by_atc
        ):
            atc_citation = next(
                (c for c in citations if c.risk_level == "HIGH_DISQUALIFIER" or "exemption" in c.verbatim_text.lower()),
                None
            )
            doc_name = atc_citation.document_name if atc_citation else "Buyer_Added_ATC.pdf"
            page_num = atc_citation.page_number if atc_citation else 1
            clause_ref = atc_citation.clause_id if atc_citation else "ATC-Exemption-Override"
            excerpt = atc_citation.verbatim_text if atc_citation else "No exemption to MSME / Startup for turnover and prior experience."

            items.append(PreBidRepresentationItem(
                query_id=f"REP-{counter:02d}",
                document_name=doc_name,
                page_number=page_num,
                clause_reference=clause_ref,
                impugned_clause_excerpt=excerpt,
                violation_category="ILLEGAL_MSME_EXEMPTION_REVOCATION",
                statutory_authority_cited=(
                    "Ministry of Finance (Dept. of Expenditure) OM No. F.20/2/2014-PPD(Pt.) dated 25.07.2016, "
                    "GFR 2017 Rule 173(i), and Public Procurement Policy for MSEs Order, 2012"
                ),
                formal_argument=(
                    f"The Buyer ATC unilaterally revokes prior turnover and experience relaxations for registered "
                    f"Micro and Small Enterprises (MSEs) / DPIIT Startups. Under GFR Rule 173(i) and MoF OM "
                    f"No. F.20/2/2014-PPD, procuring entities may only waive MSE relaxations in tenders involving "
                    f"critical public safety, health, or national security with recorded prior approval of the "
                    f"competent authority. Routine commercial procurement cannot override mandatory statutory policy."
                ),
                requested_corrigendum_amendment=(
                    "Issue a Corrigendum deleting the restrictive ATC clause and restoring statutory exemption "
                    "from prior turnover and prior experience for Udyam-registered MSEs and DPIIT Startups."
                )
            ))
            counter += 1

        # 2. Check for Disproportionate Turnover Requirement (> 200% of estimated bid value, violating CVC norms)
        if criteria.estimated_bid_value_lakhs and criteria.estimated_bid_value_lakhs > 0:
            if criteria.min_annual_turnover_lakhs > (criteria.estimated_bid_value_lakhs * 2.0):
                items.append(PreBidRepresentationItem(
                    query_id=f"REP-{counter:02d}",
                    document_name="Buyer_ATC_Financial_Criteria.pdf",
                    page_number=1,
                    clause_reference="Financial-Eligibility-Turnover",
                    impugned_clause_excerpt=(
                        f"Minimum Average Annual Turnover mandated at ₹{criteria.min_annual_turnover_lakhs:.2f} Lakhs "
                        f"against an estimated bid value of ₹{criteria.estimated_bid_value_lakhs:.2f} Lakhs."
                    ),
                    violation_category="DISPROPORTIONATE_TURNOVER_THRESHOLD",
                    statutory_authority_cited=(
                        "Central Vigilance Commission (CVC) Office Memorandum No. 12-02-1-CTE-6 dated 17.12.2002 "
                        "& GFR 2017 Rule 144 (Fundamental Principles of Public Buying)"
                    ),
                    formal_argument=(
                        f"The stipulated average annual turnover of ₹{criteria.min_annual_turnover_lakhs:.2f} Lakhs is "
                        f"{criteria.min_annual_turnover_lakhs / criteria.estimated_bid_value_lakhs:.1f}x the estimated "
                        f"contract value. CVC guidelines explicitly mandate that minimum average annual financial turnover "
                        f"should be approximately 30% of the estimated cost (and not exceed 100%) to prevent artificial "
                        f"cartelization and exclusion of capable MSMEs."
                    ),
                    requested_corrigendum_amendment=(
                        f"Revise the Minimum Average Annual Turnover requirement down to 30% of the estimated bid value "
                        f"(₹{criteria.estimated_bid_value_lakhs * 0.30:.2f} Lakhs) in accordance with CVC norms."
                    )
                ))
                counter += 1

        # 3. Check for Proprietary Brand / Model Lock violating GFR Rule 144(i)
        if criteria.proprietary_brand_lock_detected:
            items.append(PreBidRepresentationItem(
                query_id=f"REP-{counter:02d}",
                document_name="Technical_Specifications_ATC.pdf",
                page_number=1,
                clause_reference="Tech-Spec-Brand-Restriction",
                impugned_clause_excerpt=criteria.proprietary_brand_details or "Specification mandates specific proprietary brand/make without 'or equivalent'.",
                violation_category="PROPRIETARY_BRAND_LOCK",
                statutory_authority_cited="GFR 2017 Rule 144(i) & DPIIT Public Procurement (Preference to Make in India) Order 2017 Para 10(d)",
                formal_argument=(
                    "GFR 2017 Rule 144(i) strictly stipulates that technical specifications shall be framed in terms "
                    "of functional performance and generic parameters, and shall not refer to a particular trade mark, "
                    "brand name, or catalog number unless unavoidable (in which case 'or equivalent' must be added). "
                    "Furthermore, DPIIT MII Order 2017 prohibits restrictive foreign brand specifications that exclude "
                    "Class-I and Class-II Indian Local Suppliers."
                ),
                requested_corrigendum_amendment=(
                    "Amend the technical specification to remove specific brand/make references and permit "
                    "'any OEM meeting generic BIS/ISO functional parameters or equivalent'."
                )
            ))
            counter += 1

        # 4. Check for Ambiguous / Contradictory Clauses flagged by Precedence DAG or Gemini Auditor
        for cit in citations:
            if cit.status == "AMBIGUOUS_MANUAL_REVIEW":
                items.append(PreBidRepresentationItem(
                    query_id=f"REP-{counter:02d}",
                    document_name=cit.document_name,
                    page_number=cit.page_number,
                    clause_reference=cit.clause_id,
                    impugned_clause_excerpt=cit.verbatim_text,
                    violation_category="CORRIGENDUM_OR_ATC_CONTRADICTION",
                    statutory_authority_cited="GeM General Terms & Conditions (GTC) Clause 4 (Order of Precedence) & GFR Rule 173",
                    formal_argument=(
                        "There is a material ambiguity / contradiction between the baseline tender terms and the "
                        "Buyer Added ATC / Corrigendum provisions noted above. Without an explicit supersession clarification, "
                        "bidders face arbitrary technical rejection during evaluation."
                    ),
                    requested_corrigendum_amendment=(
                        f"Clarify the exact operative threshold for {cit.clause_id} via an official Corrigendum "
                        f"and confirm order of precedence prior to the bid closing date."
                    )
                ))
                counter += 1

        letter_md = cls._render_formal_letter(
            tender_id=tender_id,
            tender_title=tender_title,
            bidder=bidder,
            items=items
        )

        return PreBidLegalRepresentationPack(
            tender_id=tender_id,
            tender_title=tender_title,
            bidder_company=bidder.company_name,
            total_challenges=len(items),
            representations=items,
            formal_letter_markdown=letter_md
        )

    @staticmethod
    def _render_formal_letter(
        tender_id: str,
        tender_title: str,
        bidder: BidderProfile,
        items: List[PreBidRepresentationItem]
    ) -> str:
        date_str = datetime.now().strftime("%d %B %Y")
        if not items:
            return (
                f"# PRE-BID COMPLIANCE VERIFICATION NOTE\n"
                f"**Date**: {date_str} | **Tender ID**: {tender_id}\n\n"
                f"No predatory, anti-competitive, or statutorily ultra-vires clauses were detected requiring "
                f"offensive pre-bid legal representation."
            )

        lines = [
            f"# FORMAL PRE-BID REPRESENTATION & REQUEST FOR CORRIGENDUM",
            f"**Date**: {date_str}",
            f"**To**: The Procuring Authority / Tender Inviting Authority (TIA)",
            f"**Copy To**: Chief Vigilance Officer (CVO) / GeM Marketplace Compliance Desk",
            f"**From**: {bidder.company_name} ({bidder.entity_type}"
            + (f" — Udyam Registered MSME [{bidder.msme_category}]" if bidder.is_msme_registered else "")
            + ")",
            f"**Subject**: Pre-Bid Representation regarding restrictive / conflicting clauses in Tender No. **{tender_id}** (*{tender_title}*)",
            "\n---\n",
            "Respected Sir/Madam,\n",
            f"We, **{bidder.company_name}**, intend to participate in the subject public procurement. Upon detailed legal and "
            "statutory audit of the tender documents, Buyer Added Bid Specific Terms (ATC), and associated Corrigenda, we "
            "respectfully bring to your notice the following clauses that require immediate clarification/amendment to align "
            "with mandatory Government of India procurement statutes:\n"
        ]

        for item in items:
            lines.extend([
                f"### {item.query_id}: {item.violation_category.replace('_', ' ')}",
                f"- **Document & Location**: `{item.document_name}` | Page {item.page_number} | Clause `{item.clause_reference}`",
                f"- **Impugned Provision**: *\"{item.impugned_clause_excerpt}\"*",
                f"- **Governing Statutory Authority**: **{item.statutory_authority_cited}**",
                f"- **Submission & Legal Rationale**: {item.formal_argument}",
                f"- **Requested Modification / Corrigendum**: **{item.requested_corrigendum_amendment}**\n"
            ])

        lines.extend([
            "---\n",
            "**Prayer**: We request the Procuring Authority to kindly publish a suitable Corrigendum addressing the above "
            "points and extend the bid submission deadline by at least 7 working days in accordance with GFR 2017 principles "
            "of transparency, fair competition, and broader participation.\n",
            f"Yours faithfully,\n\n**Authorized Signatory**\n**{bidder.company_name}**"
        ])
        return "\n".join(lines)
