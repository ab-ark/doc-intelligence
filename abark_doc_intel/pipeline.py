"""
DocIntelPipeline — end-to-end document intelligence pipeline.
Auto-detects format → extracts → structures into JSON.
"""

import logging
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

from .extractors.pdf_extractor import PDFExtractor
from .extractors.docx_extractor import DOCXExtractor
from .parsers.llm_structurer import LLMStructurer
from .schema.builtin_schemas import SCHEMAS
from .models import DocumentResult, DocFormat

logger = logging.getLogger(__name__)


class DocIntelPipeline:
    """
    Full document intelligence pipeline.

    Usage:
        pipeline = DocIntelPipeline()
        result = pipeline.run("contract.pdf", doc_type="contract")
        print(result.structured_json)
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        ocr_fallback: bool = True,
    ):
        self.pdf_extractor = PDFExtractor(ocr_fallback=ocr_fallback)
        self.docx_extractor = DOCXExtractor()
        self.structurer = LLMStructurer(model=model, api_key=api_key)

    def _detect_format(self, path: str) -> DocFormat:
        ext = Path(path).suffix.lower()
        return {
            ".pdf": DocFormat.PDF,
            ".docx": DocFormat.DOCX,
            ".doc": DocFormat.DOCX,
            ".txt": DocFormat.TXT,
            ".png": DocFormat.IMAGE,
            ".jpg": DocFormat.IMAGE,
            ".jpeg": DocFormat.IMAGE,
        }.get(ext, DocFormat.UNKNOWN)

    def run(
        self,
        path: str,
        doc_type: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        extra_instructions: str = "",
    ) -> DocumentResult:
        """
        Run the full extraction + structuring pipeline.

        Args:
            path: Path to document file.
            doc_type: One of 'invoice', 'contract', 'rfp', 'resume', or custom.
            schema: Custom JSON schema dict. If None, uses built-in schema for doc_type.
            extra_instructions: Additional instructions for the LLM structurer.

        Returns:
            DocumentResult with raw_text, sections, tables, and structured_json.
        """
        fmt = self._detect_format(path)
        logger.info(f"Running DocIntelPipeline: {path} (format={fmt.value}, doc_type={doc_type})")

        # Step 1: Extract
        if fmt == DocFormat.PDF:
            result = self.pdf_extractor.extract(path)
        elif fmt == DocFormat.DOCX:
            result = self.docx_extractor.extract(path)
        elif fmt == DocFormat.TXT:
            result = self._extract_txt(path)
        else:
            raise ValueError(f"Unsupported format: {fmt.value}. Supported: pdf, docx, txt")

        # Step 2: Structure with LLM (if schema or doc_type provided)
        active_schema = schema or SCHEMAS.get(doc_type or "")
        if active_schema:
            logger.info(f"Running LLM structuring with schema for doc_type='{doc_type}'")
            result.structured_json = self.structurer.structure(
                raw_text=result.raw_text,
                schema=active_schema,
                doc_type=doc_type or "document",
                extra_instructions=extra_instructions,
            )
        else:
            logger.info("No schema provided — skipping LLM structuring step.")

        return result

    def _extract_txt(self, path: str) -> DocumentResult:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return DocumentResult(
            source=path,
            format=DocFormat.TXT,
            raw_text=content,
            metadata={"filename": Path(path).name},
        )

    def export_json(self, result: DocumentResult, out_path: str) -> None:
        with open(out_path, "w") as f:
            json.dump(result.to_dict(), f, indent=2)
        logger.info(f"Result exported to {out_path}")
