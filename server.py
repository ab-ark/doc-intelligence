"""
AbArk Doc Intelligence — FastAPI server.
Upload a document file and receive structured JSON output.
"""

import logging
import os
import tempfile
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from abark_doc_intel.pipeline import DocIntelPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AbArk Doc Intelligence API",
    description="Upload PDF/DOCX/TXT documents, receive structured JSON",
    version="0.1.0",
)

pipeline = DocIntelPipeline(
    model=os.environ.get("LLM_MODEL", "gpt-4o-mini"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "abark-doc-intelligence"}


@app.get("/schemas")
def list_schemas():
    from abark_doc_intel.schema.builtin_schemas import SCHEMAS
    return {"available_schemas": list(SCHEMAS.keys())}


@app.post("/extract")
async def extract_document(
    file: UploadFile = File(...),
    doc_type: Optional[str] = Form(None),
    extra_instructions: Optional[str] = Form(""),
):
    """
    Upload a document file. Returns raw text, section count, table count,
    and structured JSON if a doc_type is specified.
    """
    allowed_types = {
        "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    }
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=415, detail=f"Unsupported content type: {file.content_type}")

    suffix_map = {
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "text/plain": ".txt",
    }
    suffix = suffix_map.get(file.content_type, ".tmp")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = pipeline.run(
            path=tmp_path,
            doc_type=doc_type,
            extra_instructions=extra_instructions or "",
        )
        return JSONResponse(content=result.to_dict())
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)
