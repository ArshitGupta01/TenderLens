"""
TenderLens - Test Suite: Document Processor
============================================
Tests PDF parsing, hidden hyperlink extraction, and Precedence Rank tagging.
"""

import pytest
import pymupdf
from pathlib import Path
from backend.services.document_processor import DocumentProcessor


def test_precedence_rank_inference():
    """Verify Indian public procurement precedence hierarchy rank assignments."""
    assert DocumentProcessor.infer_precedence_rank("GeM-Bidding-Corr-2.pdf") == 1
    assert DocumentProcessor.infer_precedence_rank("Corrigendum_1.pdf") == 2
    assert DocumentProcessor.infer_precedence_rank("Buyer_Uploaded_ATC_RFP.pdf") == 3
    assert DocumentProcessor.infer_precedence_rank("Technical_Specifications.pdf") == 3
    assert DocumentProcessor.infer_precedence_rank("GeM-Bid-7182910.pdf") == 5


def test_pdf_processing_with_embedded_hyperlink(tmp_path: Path):
    """Verify that embedded PDF URI annotations (hidden GeM links) are extracted."""
    pdf_file = tmp_path / "GeM_Sample_Tender.pdf"

    # Create synthetic PDF using PyMuPDF
    doc = pymupdf.open()
    page = doc.new_page()

    # Add text
    page.insert_text((50, 100), "Clause 1.1: Minimum annual turnover required is Rs 50 Lakhs.")
    page.insert_text((50, 150), "Buyer uploaded ATC document: Click here to view the file")

    # Add hidden hyperlink annotation targeting an external ATC PDF
    rect = pymupdf.Rect(50, 140, 300, 160)
    page.insert_link({
        "kind": pymupdf.LINK_URI,
        "from": rect,
        "uri": "https://gem.gov.in/atc/Buyer_Added_ATC_7182910.pdf"
    })

    doc.save(str(pdf_file))
    doc.close()

    # Process via DocumentProcessor
    result = DocumentProcessor.process_pdf(str(pdf_file), "GeM_Sample_Tender.pdf")

    assert result.total_pages == 1
    assert result.precedence_rank == 5
    assert len(result.chunks) >= 1
    assert "https://gem.gov.in/atc/Buyer_Added_ATC_7182910.pdf" in result.discovered_embedded_hyperlinks
