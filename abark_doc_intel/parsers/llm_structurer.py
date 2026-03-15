"""
LLM Structurer — converts raw extracted text into schema-validated JSON.
Works with any OpenAI-compatible endpoint.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class LLMStructurer:
    """
    Takes raw document text and a JSON schema, returns structured data.

    Usage:
        structurer = LLMStructurer()
        result = structurer.structure(
            raw_text="Invoice from Acme Corp...",
            schema={"type": "object", "properties": {"vendor": {"type": "string"}, ...}},
            doc_type="invoice"
        )
    """

    SYSTEM_PROMPT = """You are a precise document information extraction AI.
Given raw document text and a target JSON schema, extract all relevant fields
and return ONLY valid JSON matching the schema. If a field is not found, use null.
Do not include any explanation or markdown — only raw JSON."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
    ):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = base_url.rstrip("/")

    def structure(
        self,
        raw_text: str,
        schema: Dict[str, Any],
        doc_type: str = "document",
        extra_instructions: str = "",
    ) -> Optional[Dict[str, Any]]:
        """
        Sends raw text + schema to LLM, returns structured dict.
        Returns None on failure.
        """
        schema_str = json.dumps(schema, indent=2)
        user_prompt = f"""Document Type: {doc_type}

Target JSON Schema:
{schema_str}

Raw Document Text:
---
{raw_text[:6000]}
---

{extra_instructions}

Extract and return JSON matching the schema exactly."""

        payload = {
            "model": self.model,
            "temperature": 0.0,
            "max_tokens": 2048,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
        }

        try:
            with httpx.Client(timeout=45) as client:
                resp = client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                resp.raise_for_status()
                content = resp.json()["choices"][0]["message"]["content"]
                # Strip markdown fences if present
                content = content.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
                return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error from LLM response: {e}")
            return None
        except Exception as e:
            logger.error(f"LLMStructurer error: {e}")
            return None
