# abark-doc-intelligence

> **Document Intelligence Pipeline by AbArk**
> Upload PDF, DOCX, or TXT — get schema-validated structured JSON out.
> Zero-dependency OCR fallback, built-in schemas for invoices, contracts, RFPs, and resumes.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Features

- **Auto format detection** — PDF, DOCX, TXT
- **PDF parsing** — native text + table extraction via pdfplumber; OCR fallback via Tesseract
- **DOCX parsing** — full heading/section/table extraction via python-docx
- **LLM structuring** — converts raw text → schema-validated JSON with any OpenAI-compatible model
- **Built-in schemas** — Invoice, Contract, RFP, Resume (plug in your own schema too)
- **REST API** — multipart file upload endpoint via FastAPI
- **Docker ready**

---

## Quick Start

```bash
pip install -e .
export OPENAI_API_KEY=sk-...

python -c "
from abark_doc_intel.pipeline import DocIntelPipeline

pipeline = DocIntelPipeline()
result = pipeline.run('invoice.pdf', doc_type='invoice')
print(result.structured_json)
"
```

---

## REST API

```bash
uvicorn server:app --reload --port 8001

# Extract an invoice
curl -X POST http://localhost:8001/extract \
  -F 'file=@invoice.pdf' \
  -F 'doc_type=invoice'

# List available schemas
curl http://localhost:8001/schemas
```

---

## Built-in Schemas

| `doc_type` | Extracts |
|---|---|
| `invoice` | vendor, client, line items, totals, dates |
| `contract` | parties, dates, obligations, clauses |
| `rfp` | requirements, deadlines, evaluation criteria |
| `resume` | skills, experience, education, certifications |

### Custom Schema

```python
custom_schema = {
    "type": "object",
    "properties": {
        "patient_name": {"type": "string"},
        "diagnosis": {"type": "string"},
        "medications": {"type": "array", "items": {"type": "string"}},
    }
}
result = pipeline.run("medical_report.pdf", schema=custom_schema, doc_type="medical_report")
```

---

## Architecture

```
abark_doc_intel/
├── models.py                   # DocumentResult, DocFormat, ExtractedTable
├── pipeline.py                 # DocIntelPipeline — main orchestrator
├── extractors/
│   ├── pdf_extractor.py        # pdfplumber + OCR fallback
│   └── docx_extractor.py       # python-docx
├── parsers/
│   └── llm_structurer.py       # LLM → JSON structuring
└── schema/
    └── builtin_schemas.py      # Invoice, Contract, RFP, Resume schemas
server.py                       # FastAPI REST server
```

---

## References & Inspiration

- [IBM Docling](https://github.com/docling-project/docling) — advanced PDF parsing, TableFormer
- [NanoNets docext](https://github.com/NanoNets/docext) — VLM-powered OCR-free extraction

---

## License

MIT © [AbArk](https://github.com/AbArk)
