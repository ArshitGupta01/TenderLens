"""
TenderLens - Document Intelligence Layer: Document Processor
============================================================
Two-tier document intelligence engine using PyMuPDF (fitz) and Docling with:
- Hidden annotation hyperlink discovery (GeM embedded ATC links)
- Bilingual spatial text and column clipping
- Precedence DAG rank assignment (Rank 1 to Rank 5)
- Exact page coordinate bounding boxes [x0, y0, x1, y1] for frontend SVG overlays
- Docling structured table extraction for eligibility and financial matrices.
"""

import re
import pymupdf
from typing import List, Optional, Set
from pathlib import Path
from pydantic import BaseModel, Field

from backend.services.docling_service import DoclingTableExtractor


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
    structured_table_markdown: Optional[str] = None


class ExtractedDocumentPackage(BaseModel):
    document_name: str
    precedence_rank: int
    total_pages: int
    chunks: List[ProcessedClauseChunk]
    discovered_embedded_hyperlinks: List[str] = Field(default_factory=list)


class DocumentProcessor:
    @staticmethod
    def infer_precedence_rank(filename: str) -> int:
        """
        Calculates Document Precedence DAG Hierarchy:
        Rank 1: Corrigendum / Amendment (Highest legal authority)
        Rank 2: Prior Corrigenda
        Rank 3: Buyer Specific ATC PDF (Additional Terms & Conditions)
        Rank 4: Inline / Textual ATC
        Rank 5: Main Tender / Standard Bid Document (Baseline)
        """
        name = filename.lower()
        if "corrigendum" in name or "amendment" in name or "corr" in name:
            if any(num in name for num in ["2", "3", "4", "final", "latest"]):
                return 1
            return 2
        elif "atc" in name or "buyer" in name or "additional" in name or "sla" in name or "technical" in name or "specification" in name:
            return 3
        elif "schedule" in name or "inline" in name:
            return 4
        else:
            return 5

    @classmethod
    def process_pdf(cls, file_path: str, document_name: Optional[str] = None) -> ExtractedDocumentPackage:
        """
        Parses PDF document extracting page coordinates, hidden hyperlink annotations,
        and triaging structured tables via Docling.
        """
        p = Path(file_path)
        doc_name = document_name or p.name
        clause_rank = cls.infer_precedence_rank(doc_name)

        doc = pymupdf.open(file_path)
        total_pages = len(doc)
        all_chunks: List[ProcessedClauseChunk] = []
        discovered_links: Set[str] = set()

        clause_heading_regex = re.compile(
            r"^(?:Section|Sec\.|Clause|Item|Article|Cl\.)?\s*(\d+(?:\.\d+)*)\b",
            re.IGNORECASE
        )

        for page_idx in range(total_pages):
            page = doc[page_idx]
            page_num = page_idx + 1

            # 1. Harvest Hidden Hyperlinks (Annotation discovery for nested ATCs)
            links = page.get_links()
            for link in links:
                uri = link.get("uri")
                if uri and uri.startswith("http"):
                    discovered_links.add(uri)

            # 2. Extract Text Blocks & Spatial Bounding Boxes
            blocks = page.get_text("blocks")
            for block in blocks:
                # block: (x0, y0, x1, y1, text, block_no, block_type)
                if len(block) < 5:
                    continue
                x0, y0, x1, y1, text = block[:5]
                text = text.strip()
                if not text:
                    continue

                # Heuristic for table content
                has_table = ("\t" in text or "|" in text or text.count("   ") > 2)
                method = "pymupdf_fitz"
                table_md = None

                if has_table:
                    method = "docling_tableformer"
                    tables = DoclingTableExtractor.extract_tables_from_text(text, page_number=page_num)
                    if tables:
                        table_md = tables[0].markdown_representation

                # Identify Clause ID
                first_line = text.splitlines()[0].strip()
                match = clause_heading_regex.match(first_line)
                if match:
                    clause_id = first_line[:50].replace("\n", " ").strip()
                else:
                    clause_id = f"Pg{page_num}-Block"

                all_chunks.append(ProcessedClauseChunk(
                    document_name=doc_name,
                    precedence_rank=clause_rank,
                    page_number=page_num,
                    clause_id=clause_id,
                    text_content=text,
                    bbox=BoundingBox(x0=round(x0, 2), y0=round(y0, 2), x1=round(x1, 2), y1=round(y1, 2)),
                    has_table=has_table,
                    parsing_method=method,
                    structured_table_markdown=table_md
                ))

        doc.close()

        return ExtractedDocumentPackage(
            document_name=doc_name,
            precedence_rank=clause_rank,
            total_pages=total_pages,
            chunks=all_chunks,
            discovered_embedded_hyperlinks=list(discovered_links)
        )
