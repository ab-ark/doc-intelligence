"""
Tests for AbArk Doc Intelligence.
Run with: pytest tests/ -v
"""

import json
import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch

from abark_doc_intel.models import DocumentResult, DocFormat, ExtractedTable, ExtractedSection
from abark_doc_intel.pipeline import DocIntelPipeline
from abark_doc_intel.parsers.llm_structurer import LLMStructurer
from abark_doc_intel.schema.builtin_schemas import SCHEMAS


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_txt_file(tmp_path):
    content = """INVOICE #INV-001
Vendor: Acme Corp
Client: Beta Ltd
Date: 2025-01-15
Due: 2025-02-15

Item: Software License  Qty: 1  Price: $5000  Total: $5000
Item: Support Plan     Qty: 12  Price: $200   Total: $2400

Subtotal: $7400
Tax (10%): $740
Total: $8140
"""
    f = tmp_path / "invoice.txt"
    f.write_text(content)
    return str(f)


# ── Unit Tests ─────────────────────────────────────────────────────────────────

class TestDocumentResult:
    def test_to_dict_fields(self):
        result = DocumentResult(
            source="test.pdf",
            format=DocFormat.PDF,
            raw_text="Hello world",
            page_count=2,
        )
        d = result.to_dict()
        assert d["source"] == "test.pdf"
        assert d["format"] == "pdf"
        assert d["page_count"] == 2
        assert d["raw_text_length"] == len("Hello world")


class TestExtractedTable:
    def test_to_dict(self):
        tbl = ExtractedTable(
            headers=["Name", "Price"],
            rows=[["Widget", "10"], ["Gadget", "20"]],
            page=1,
        )
        d = tbl.to_dict()
        assert d["headers"] == ["Name", "Price"]
        assert len(d["rows"]) == 2


class TestBuiltinSchemas:
    def test_all_schemas_present(self):
        for key in ["invoice", "contract", "rfp", "resume"]:
            assert key in SCHEMAS

    def test_invoice_schema_fields(self):
        schema = SCHEMAS["invoice"]
        assert "invoice_number" in schema["properties"]
        assert "total_amount" in schema["properties"]
        assert "line_items" in schema["properties"]


class TestLLMStructurer:
    @patch("abark_doc_intel.parsers.llm_structurer.httpx.Client")
    def test_structure_returns_dict(self, MockClient):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"invoice_number": "INV-001", "total_amount": 8140}'}}]
        }
        mock_response.raise_for_status = MagicMock()
        MockClient.return_value.__enter__.return_value.post.return_value = mock_response

        structurer = LLMStructurer(api_key="test-key")
        result = structurer.structure(
            raw_text="Invoice INV-001 total $8140",
            schema=SCHEMAS["invoice"],
            doc_type="invoice",
        )
        assert result is not None
        assert result["invoice_number"] == "INV-001"

    @patch("abark_doc_intel.parsers.llm_structurer.httpx.Client")
    def test_structure_handles_bad_json(self, MockClient):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "NOT JSON AT ALL"}}]
        }
        mock_response.raise_for_status = MagicMock()
        MockClient.return_value.__enter__.return_value.post.return_value = mock_response

        structurer = LLMStructurer(api_key="test-key")
        result = structurer.structure("some text", SCHEMAS["invoice"], "invoice")
        assert result is None


class TestDocIntelPipeline:
    def test_detect_format_pdf(self):
        pipeline = DocIntelPipeline.__new__(DocIntelPipeline)
        from abark_doc_intel.models import DocFormat
        fmt = pipeline._detect_format("report.pdf")
        assert fmt == DocFormat.PDF

    def test_detect_format_docx(self):
        pipeline = DocIntelPipeline.__new__(DocIntelPipeline)
        from abark_doc_intel.models import DocFormat
        fmt = pipeline._detect_format("doc.docx")
        assert fmt == DocFormat.DOCX

    def test_detect_format_unknown(self):
        pipeline = DocIntelPipeline.__new__(DocIntelPipeline)
        from abark_doc_intel.models import DocFormat
        fmt = pipeline._detect_format("file.xyz")
        assert fmt == DocFormat.UNKNOWN

    def test_run_txt_no_schema(self, sample_txt_file):
        pipeline = DocIntelPipeline.__new__(DocIntelPipeline)
        pipeline.pdf_extractor = MagicMock()
        pipeline.docx_extractor = MagicMock()
        pipeline.structurer = MagicMock()

        result = pipeline._extract_txt(sample_txt_file)
        assert "INVOICE" in result.raw_text
        assert result.format == DocFormat.TXT

    def test_export_json(self, tmp_path):
        pipeline = DocIntelPipeline.__new__(DocIntelPipeline)
        result = DocumentResult(
            source="test.txt",
            format=DocFormat.TXT,
            raw_text="hello",
        )
        out = str(tmp_path / "out.json")
        pipeline.export_json(result, out)
        with open(out) as f:
            data = json.load(f)
        assert data["format"] == "txt"
