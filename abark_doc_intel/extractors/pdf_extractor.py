"""
PDF Extractor — extracts text, tables, and sections from PDF files.
Uses pdfplumber for native PDFs and pytesseract for scanned/image PDFs.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from ..models import DocumentResult, DocFormat, ExtractedSection, ExtractedTable

logger = logging.getLogger(__name__)


class PDFExtractor:
    """
    Extracts structured content from PDF files.

    - Native PDFs: pdfplumber for high-accuracy text + table extraction.
    - Scanned PDFs: pytesseract OCR fallback.
    """

    def __init__(self, ocr_fallback: bool = True, min_text_length: int = 100):
        self.ocr_fallback = ocr_fallback
        self.min_text_length = min_text_length

    def extract(self, path: str) -> DocumentResult:
        path = str(path)
        logger.info(f"Extracting PDF: {path}")

        try:
            import pdfplumber
        except ImportError:
            raise ImportError("Install pdfplumber: pip install pdfplumber")

        raw_text = ""
        sections = []
        tables = []
        page_count = 0

        with pdfplumber.open(path) as pdf:
            page_count = len(pdf.pages)
            logger.debug(f"PDF has {page_count} pages")

            for page_num, page in enumerate(pdf.pages, start=1):
                # Extract text
                page_text = page.extract_text() or ""
                raw_text += page_text + "\n"

                # Extract tables
                for tbl in page.extract_tables():
                    if tbl and len(tbl) > 1:
                        headers = [str(h or "").strip() for h in tbl[0]]
                        rows = [[str(c or "").strip() for c in row] for row in tbl[1:]]
                        tables.append(ExtractedTable(headers=headers, rows=rows, page=page_num))
                        logger.debug(f"  Page {page_num}: extracted table with {len(rows)} rows")

                # Basic section detection via heuristics
                for line in page_text.splitlines():
                    stripped = line.strip()
                    if stripped and len(stripped) < 80 and stripped.isupper():
                        sections.append(ExtractedSection(title=stripped, content="", page=page_num, level=1))
                    elif stripped and len(stripped) < 120 and stripped.endswith(":"):
                        sections.append(ExtractedSection(title=stripped.rstrip(":"), content="", page=page_num, level=2))

        # OCR fallback for scanned PDFs
        if len(raw_text.strip()) < self.min_text_length and self.ocr_fallback:
            logger.warning("Low text content detected — attempting OCR fallback")
            raw_text = self._ocr_extract(path) or raw_text

        logger.info(f"PDF extraction complete: {len(raw_text)} chars, {len(tables)} tables, {page_count} pages")
        return DocumentResult(
            source=path,
            format=DocFormat.PDF,
            raw_text=raw_text.strip(),
            sections=sections,
            tables=tables,
            page_count=page_count,
            metadata={"filename": os.path.basename(path)},
        )

    def _ocr_extract(self, path: str) -> str:
        try:
            from pdf2image import convert_from_path
            import pytesseract
            pages = convert_from_path(path)
            texts = [pytesseract.image_to_string(p) for p in pages]
            return "\n".join(texts)
        except ImportError:
            logger.warning("OCR dependencies missing (pdf2image, pytesseract). Skipping.")
            return ""
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return ""
