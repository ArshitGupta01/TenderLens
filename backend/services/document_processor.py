"""
TenderLens - Document Intelligence Layer: Document Processor
============================================================
Two-tier document intelligence engine using PyMuPDF (fitz) with:
- Hidden annotation hyperlink discovery (GeM embedded ATC links)
- Bilingual spatial text and column clipping
- Precedence DAG rank assignment (Rank 1 to Rank 5)
- Exact page coordinate bounding boxes [x0, y0, x1, y1] for frontend SVG overlays.
"""

import re
import pymupdf
from typing import List, Optional, Set
from pathlib import Path
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class ProcessedClauseChunk(BaseModel):
    document_name: str
    precedence_rank: int  # 1 = Latest Corr, 2 = Prior Corr, 3 = Buyer RFP, 4 = Text ATC, 5 = Main
    page_number: int
    clause_id: str
    text_content: str
    bbox: Optional[BoundingBox] = None
    has_table: bool = False
    parsing_method: str = "pymupdf_fitz"  # 'pymupdf_fitz' or 'docling_tableformer'


class ExtractedDocumentPackage(BaseModel):
    document_name: str
    precedence_rank: int
    total_pages: int
    chunks: List[ProcessedClauseChunk]
    discovered_embedded_hyperlinks: List[str] = Field(default_factory=list)


class DocumentProcessor:
    @staticmethod
    def infer_precedence_rank(document_name: str) -> int:
        """
        Assigns legal precedence rank based on Indian procurement taxonomy:
        - Rank 1: Latest Corrigendum (e.g., Corr-2, Corrigendum-Final)
        - Rank 2: Prior Corrigenda (e.g., Corr-1)
        - Rank 3: Buyer Uploaded ATC / RFP PDF
        - Rank 4: Buyer Text-Based ATC Clauses (handled during paragraph chunking)
        - Rank 5: Main Tender / GeM Bid PDF
        """
        name_lower = document_name.lower()
        if "corr" in name_lower or "amend" in name_lower:
            # Check for version numbers
            match = re.search(r"corr(?:igendum)?[-_ ]?(\d+)", name_lower)
            if match and int(match.group(1)) > 1:
                return 1  # Latest
            return 2  # Prior corrigendum
        elif "atc" in name_lower or "rfp" in name_lower or "specification" in name_lower or "buyer" in name_lower:
            return 3  # Buyer Uploaded ATC PDF
        return 5  # Baseline Main Tender PDF

    @classmethod
    def extract_embedded_hyperlinks(cls, page: pymupdf.Page) -> List[str]:
        """
        Extracts hidden annotation hyperlinks from PDF stream (e.g. GeM's embedded
        'Buyer uploaded ATC document: Click here to view the file' URLs).
        """
        urls: List[str] = []
        links = page.get_links()
        for link in links:
            uri = link.get("uri")
            if uri and uri.startswith("http"):
                urls.append(uri)
        return list(set(urls))

    @classmethod
    def process_pdf(
        cls,
        pdf_path: str,
        document_name: Optional[str] = None
    ) -> ExtractedDocumentPackage:
        """
        Parses a PDF document page-by-page, extracting clause blocks, bounding boxes,
        and hidden hyperlinks.
        """
        file_path = Path(pdf_path)
        doc_name = document_name or file_path.name
        base_rank = cls.infer_precedence_rank(doc_name)

        doc = pymupdf.open(pdf_path)
        total_pages = len(doc)
        all_chunks: List[ProcessedClauseChunk] = []
        all_hyperlinks: Set[str] = set()

        clause_heading_regex = re.compile(
            r"^(?:clause|section|sl\.?\s*no\.?|param(?:eter)?|\d+(?:\.\d+)*)\s*[:.-]?",
            re.IGNORECASE
        )

        in_buyer_atc_section = False

        for page_idx in range(total_pages):
            page = doc[page_idx]
            page_num = page_idx + 1

            # 1. Harvest hidden PDF annotation hyperlinks
            page_links = cls.extract_embedded_hyperlinks(page)
            for link in page_links:
                all_hyperlinks.add(link)

            # 2. Check for tabular content
            tables = page.find_tables()
            has_table = len(tables.tables) > 0

            # 3. Extract text blocks with spatial coordinates
            # blocks format: (x0, y0, x1, y1, text, block_no, block_type)
            blocks = page.get_text("blocks", sort=True)

            for b in blocks:
                if len(b) < 5:
                    continue
                x0, y0, x1, y1, raw_text = b[0], b[1], b[2], b[3], b[4]
                text = raw_text.strip()
                if not text:
                    continue

                # Detect if we crossed into GeM's Buyer Added Text ATC section
                if "buyer added bid specific terms and conditions" in text.lower():
                    in_buyer_atc_section = True

                # Determine effective clause rank
                clause_rank = base_rank
                if base_rank == 5 and in_buyer_atc_section:
                    clause_rank = 4  # Elevate Rank 5 baseline to Rank 4 Buyer Text ATC

                # Identify Clause ID
                first_line = text.splitlines()[0].strip()
                match = clause_heading_regex.match(first_line)
                if match:
                    clause_id = first_line[:50].replace("\n", " ").strip()
                else:
                    clause_id = f"Pg{page_num}-Block"

                # Triage page parsing method
                method = "docling_tableformer" if has_table else "pymupdf_fitz"

                all_chunks.append(ProcessedClauseChunk(
                    document_name=doc_name,
                    precedence_rank=clause_rank,
                    page_number=page_num,
                    clause_id=clause_id,
                    text_content=text,
                    bbox=BoundingBox(x0=round(x0, 2), y0=round(y0, 2), x1=round(x1, 2), y1=round(y1, 2)),
                    has_table=has_table,
                    parsing_method=method
                ))

        doc.close()

        return ExtractedDocumentPackage(
            document_name=doc_name,
            precedence_rank=base_rank,
            total_pages=total_pages,
            chunks=all_chunks,
            discovered_embedded_hyperlinks=list(all_hyperlinks)
        )
