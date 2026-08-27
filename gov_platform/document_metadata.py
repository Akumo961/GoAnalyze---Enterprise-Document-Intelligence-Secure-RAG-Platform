"""Deterministic, reviewable metadata extraction for government documents.

This module deliberately avoids an LLM. Metadata is derived from trusted
processing inputs and document text, so the result is reproducible and easy to
audit. It is decision-support metadata, not an authoritative legal record.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .document_extract import ExtractedDocument

MAX_TITLE_LENGTH = 500


@dataclass(frozen=True)
class DocumentMetadata:
    title: str | None
    language: str
    page_count: int | None
    character_count: int
    word_count: int
    extraction_method: str
    metadata_version: str = "1"


def _detect_language(text: str) -> str:
    """Return a conservative language label from common stop-word evidence."""
    lowered = f" {text.lower()} "
    french = len(re.findall(r"\b(le|la|les|des|une|pour|dans|avec|est|sur)\b", lowered))
    english = len(re.findall(r"\b(the|and|for|with|from|this|that|is|are)\b", lowered))
    if french == 0 and english == 0:
        return "und"
    if french > english:
        return "fr"
    if english > french:
        return "en"
    return "und"


def _extract_title(text: str) -> str | None:
    for line in text.splitlines():
        candidate = " ".join(line.split()).strip()
        if candidate and len(candidate) <= MAX_TITLE_LENGTH:
            return candidate
    return None


def extract_metadata(document: ExtractedDocument) -> DocumentMetadata:
    text = document.text
    return DocumentMetadata(
        title=_extract_title(text),
        language=_detect_language(text),
        page_count=document.page_count,
        character_count=len(text),
        word_count=len(text.split()),
        extraction_method=document.method,
    )
