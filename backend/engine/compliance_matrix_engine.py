"""Build a draft checklist and CSV from gate results and source citations."""

import csv
import io
from typing import List

from contracts.schema import (
    BidderProfile,
    ClauseCitation,
    ComplianceAndBinderPackage,
    ComplianceMatrixRow,
    GateResult,
)
from backend.engine.deterministic_gatekeeper import TenderStatutoryCriteria


def _spreadsheet_safe(value: object) -> str:
    text = str(value)
    if text.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + text
    return text


class ComplianceMatrixEngine:
    @classmethod
    def generate_package(
        cls,
        tender_id: str,
        tender_title: str,
        bidder: BidderProfile,
        criteria: TenderStatutoryCriteria,
        gates: List[GateResult],
        citations: List[ClauseCitation],
    ) -> ComplianceAndBinderPackage:
        rows: List[ComplianceMatrixRow] = []
        for index, gate in enumerate(gates, start=1):
            rows.append(ComplianceMatrixRow(
                sl_no=index,
                document_name="Entered bidder and tender values",
                page_number=None,
                clause_id=gate.rule_name,
                requirement_summary=f"{gate.rule_name}: {gate.required_value}",
                compliance_status=(
                    "REVIEW_REQUIRED"
                    if gate.review_required
                    else ("MET_FROM_ENTERED_VALUES" if gate.passed else "GAP_FROM_ENTERED_VALUES")
                ),
                bidder_proof_and_datasheet_mapping=(
                    f"Entered value: {gate.bidder_value}. Supporting evidence was not uploaded or verified."
                ),
                deviation_statement="Check the original tender and attach source evidence before treating this row as complete.",
            ))

        for citation in citations:
            rows.append(ComplianceMatrixRow(
                sl_no=len(rows) + 1,
                document_name=citation.document_name,
                page_number=citation.page_number,
                clause_id=citation.clause_id,
                requirement_summary=citation.verbatim_text[:240],
                compliance_status="SOURCE_REVIEW_REQUIRED",
                bidder_proof_and_datasheet_mapping="Source excerpt found; bidder proof was not supplied or matched to this clause.",
                deviation_statement="Open the original notice and verify the excerpt, page and operative version.",
            ))

        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow([
            "No.", "Source", "Page", "Clause", "Requirement", "Entered-value status",
            "Evidence mapping", "Review note",
        ])
        for row in rows:
            writer.writerow([
                row.sl_no,
                _spreadsheet_safe(row.document_name),
                row.page_number if row.page_number is not None else "",
                _spreadsheet_safe(row.clause_id),
                _spreadsheet_safe(row.requirement_summary),
                row.compliance_status,
                _spreadsheet_safe(row.bidder_proof_and_datasheet_mapping),
                _spreadsheet_safe(row.deviation_statement),
            ])

        has_gaps = any(row.compliance_status == "GAP_FROM_ENTERED_VALUES" for row in rows)
        note = (
            f"Draft checklist for {tender_title} ({tender_id}). Values are entered or extracted and are not evidence of compliance. "
            "No statutory declarations are generated. Review the original tender and supporting documents before submitting a bid."
        )
        return ComplianceAndBinderPackage(
            compliance_rows=rows,
            has_material_deviations=has_gaps,
            csv_export_string=output.getvalue(),
            statutory_affidavits=[],
            review_note=note,
        )
