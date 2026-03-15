"""
Core data models for AbArk Doc Intelligence.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class DocFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    IMAGE = "image"
    UNKNOWN = "unknown"


@dataclass
class ExtractedTable:
    headers: List[str]
    rows: List[List[str]]
    page: Optional[int] = None

    def to_dict(self) -> Dict:
        return {"headers": self.headers, "rows": self.rows, "page": self.page}


@dataclass
class ExtractedSection:
    title: Optional[str]
    content: str
    page: Optional[int] = None
    level: int = 1  # heading level


@dataclass
class DocumentResult:
    """Final output from the extraction pipeline."""
    source: str
    format: DocFormat
    raw_text: str
    sections: List[ExtractedSection] = field(default_factory=list)
    tables: List[ExtractedTable] = field(default_factory=list)
    structured_json: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    page_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "format": self.format.value,
            "page_count": self.page_count,
            "sections_count": len(self.sections),
            "tables_count": len(self.tables),
            "structured_json": self.structured_json,
            "metadata": self.metadata,
            "raw_text_length": len(self.raw_text),
        }
