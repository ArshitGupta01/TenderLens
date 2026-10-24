"""
TenderLens - Pillar C: Automated Compliance Matrix, Deviation & Affidavit Engine
================================================================================
Eliminates manual bid-prep bottlenecks by auto-generating:
1. Structured Clause-by-Clause Technical & Commercial Compliance Matrix
2. Formal Deviation Statement (mapping any non-standard terms)
3. Portal-ready CSV export string
4. Ready-to-sign Statutory Affidavits:
   - GFR 2017 Rule 170(i) Bid Security Declaration (in lieu of EMD)
   - DPIIT Make in India Local Content Self-Certification
   - GFR 2017 Rule 144(xi) Land Border Sharing Undertaking
   - OEM Manufacturer Authorization Form (MAF) Draft
"""

import io
import csv
from datetime import datetime
from typing import List
from contracts.schema import (
    BidderProfile,
    ClauseCitation,
    GateResult,
    ComplianceMatrixRow,
    StatutoryAffidavitDraft,
    ComplianceAndBinderPackage
)
from backend.engine.deterministic_gatekeeper import TenderStatutoryCriteria


class ComplianceMatrixEngine:
    @classmethod
    def generate_package(
        cls,
        tender_id: str,
        tender_title: str,
        bidder: BidderProfile,
        criteria: TenderStatutoryCriteria,
        gates: List[GateResult],
        citations: List[ClauseCitation]
    ) -> ComplianceAndBinderPackage:
        rows: List[ComplianceMatrixRow] = []
        sl = 1

        # 1. Convert Deterministic Gates into Auditable Compliance Matrix Rows
        for gate in gates:
            status = "COMPLIED" if gate.passed else "DEVIATION"
            if gate.passed and "CONDITIONAL REQUIREMENT" in gate.reason:
                status = "CLARIFICATION_REQUIRED"

            deviation_note = (
                "Nil Deviation — Strictly Complied"
                if status == "COMPLIED"
                else f"Statutory Exemption / Pre-Bid Representation Invoked: {gate.reason}"
            )

            rows.append(ComplianceMatrixRow(
                sl_no=sl,
                document_name="Tender_Statutory_Schedule.pdf",
                page_number=1,
                clause_id=f"GATE-{sl:02d}",
                requirement_summary=f"{gate.rule_name} (Mandated: {gate.required_value})",
                compliance_status=status,
                bidder_proof_and_datasheet_mapping=f"Bidder Verified Credential: {gate.bidder_value} | Ref: {gate.statutory_citation}",
                deviation_statement=deviation_note
            ))
            sl += 1

        # 2. Convert Extracted Document Clause Citations into Compliance Rows
        for cit in citations:
            c_status = "COMPLIED"
            if cit.status == "NON_COMPLIANT":
                c_status = "DEVIATION"
            elif cit.status in ["AMBIGUOUS_MANUAL_REVIEW", "CONDITIONAL"]:
                c_status = "CLARIFICATION_REQUIRED"

            rows.append(ComplianceMatrixRow(
                sl_no=sl,
                document_name=cit.document_name,
                page_number=cit.page_number,
                clause_id=cit.clause_id,
                requirement_summary=cit.verbatim_text[:180],
                compliance_status=c_status,
                bidder_proof_and_datasheet_mapping=(
                    f"Anchored to {cit.document_name} (Pg {cit.page_number}, {cit.clause_id}). "
                    f"Supported by {bidder.company_name} Technical Datasheet & QA Certificates ({', '.join(bidder.held_certifications) or 'Standard'})."
                ),
                deviation_statement=(
                    "Nil Deviation — Strictly Complied"
                    if c_status == "COMPLIED"
                    else f"Subject to Pre-Bid Query / Statutory Precedence Review ({cit.risk_level})"
                )
            ))
            sl += 1

        has_deviations = any(r.compliance_status != "COMPLIED" for r in rows)
        csv_str = cls._build_csv_string(rows)
        affidavits = cls._generate_statutory_affidavits(tender_id, tender_title, bidder, criteria)

        return ComplianceAndBinderPackage(
            compliance_rows=rows,
            has_material_deviations=has_deviations,
            csv_export_string=csv_str,
            statutory_affidavits=affidavits
        )

    @staticmethod
    def _build_csv_string(rows: List[ComplianceMatrixRow]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Sl. No.",
            "Source Document",
            "Page No.",
            "Clause Reference",
            "Tender Specification / Requirement",
            "Compliance Status (COMPLIED / DEVIATION)",
            "Bidder Proof & Datasheet Reference",
            "Deviation Statement"
        ])
        for r in rows:
            writer.writerow([
                r.sl_no,
                r.document_name,
                r.page_number,
                r.clause_id,
                r.requirement_summary,
                r.compliance_status,
                r.bidder_proof_and_datasheet_mapping,
                r.deviation_statement
            ])
        return output.getvalue()

    @staticmethod
    def _generate_statutory_affidavits(
        tender_id: str,
        tender_title: str,
        bidder: BidderProfile,
        criteria: TenderStatutoryCriteria
    ) -> List[StatutoryAffidavitDraft]:
        date_str = datetime.now().strftime("%d %B %Y")
        mii_class = "Class-I Local Supplier" if bidder.local_content_percentage >= 50.0 else "Class-II Local Supplier"

        affidavits: List[StatutoryAffidavitDraft] = [
            # 1. GFR 2017 Rule 170(i) Bid Security Declaration
            StatutoryAffidavitDraft(
                doc_code="GFR_170_BID_SECURITY",
                title="Bid Security Declaration (In Lieu of Earnest Money Deposit)",
                governing_statute="Rule 170(i) of General Financial Rules (GFR), 2017",
                content_markdown=(
                    f"# BID SECURITY DECLARATION\n"
                    f"**Date**: {date_str} | **Tender Ref**: {tender_id} (*{tender_title}*)\n\n"
                    f"We, **{bidder.company_name}** (Entity Type: {bidder.entity_type}), hereby declare under **GFR 2017 Rule 170(i)** "
                    f"that we accept that if we withdraw or modify our bid during the period of validity, or if we are awarded the contract "
                    f"and fail to sign the contract or submit a performance security before the deadline defined in the RFP, we will be "
                    f"suspended for the period of time specified in the tender document from being eligible to submit bids for contracts "
                    f"with the procuring entity.\n\n"
                    f"**Authorized Signatory**: For **{bidder.company_name}**"
                )
            ),
            # 2. DPIIT Make in India Local Content Declaration
            StatutoryAffidavitDraft(
                doc_code="DPIIT_MII_LOCAL_CONTENT",
                title="Self-Certification for Local Content (Make in India)",
                governing_statute="DPIIT Public Procurement (Preference to Make in India) Order, 2017 (as amended)",
                content_markdown=(
                    f"# SELF-CERTIFICATION FOR LOCAL CONTENT\n"
                    f"**Date**: {date_str} | **Tender Ref**: {tender_id}\n\n"
                    f"In line with the **DPIIT Public Procurement (Preference to Make in India) Order, 2017**, we, **{bidder.company_name}**, "
                    f"hereby certify that the items/services offered against Tender No. **{tender_id}** meet the mandatory local content "
                    f"threshold with a verified domestic value addition of **{bidder.local_content_percentage:.1f}%**, qualifying us as a "
                    f"**{mii_class}**.\n\n"
                    f"- **Location of Local Value Addition in India**: Manufacturing / Integration Facility of {bidder.company_name}\n"
                    f"- **Note**: False declaration shall be a breach of the Code of Integrity under Rule 175(1)(i)(h) of the GFR 2017."
                )
            ),
            # 3. GFR Rule 144(xi) Land Border Undertaking
            StatutoryAffidavitDraft(
                doc_code="GFR_144_XI_LAND_BORDER",
                title="Undertaking on Compliance with GFR Rule 144(xi) (Land Border Clause & Non-Blacklisting)",
                governing_statute="Ministry of Finance OM No. F.No.6/18/2019-PPD dated 23.07.2020 & GFR Rule 144(xi)",
                content_markdown=(
                    f"# CERTIFICATE UNDER RULE 144(xi) OF GFR 2017 & NON-BLACKLISTING\n"
                    f"**Date**: {date_str} | **Tender Ref**: {tender_id}\n\n"
                    f"1. **Land Border Undertaking**: We, **{bidder.company_name}**, have read the clause regarding restrictions on "
                    f"procurement from a bidder of a country which shares a land border with India; we certify that **{bidder.company_name}** "
                    f"is not from such a country (or is registered with the Competent Authority under DPIIT) and is eligible to be considered.\n"
                    f"2. **Non-Blacklisting**: We further affirm that **{bidder.company_name}** is not currently debarred, blacklisted, or "
                    f"put on holiday list by GeM, CPPP, or any Central/State Government PSU."
                )
            )
        ]

        if criteria.oem_authorization_mandatory:
            affidavits.append(StatutoryAffidavitDraft(
                doc_code="OEM_MAF_FORMAT",
                title="Tender-Specific Manufacturer Authorization Form (MAF)",
                governing_statute="GeM Bid Specific OEM Authorization Guidelines",
                content_markdown=(
                    f"# MANUFACTURER AUTHORIZATION FORM (MAF)\n"
                    f"**Date**: {date_str} | **To**: The Tender Inviting Authority | **Ref Tender**: {tender_id}\n\n"
                    f"We, **[OEM Name / {bidder.company_name}]**, being the Original Equipment Manufacturer having factories in India, "
                    f"hereby authorize **{bidder.company_name}** to submit a bid, negotiate, and conclude the contract against Tender "
                    f"**{tender_id}**. We hereby extend our full comprehensive back-to-back OEM warranty, spares availability, and "
                    f"technical support for the entire contract duration."
                )
            ))

        return affidavits
