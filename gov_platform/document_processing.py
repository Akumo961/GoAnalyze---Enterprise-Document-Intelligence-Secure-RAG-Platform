"""Secure document-content processing boundary for registered documents.

The service accepts bytes only from an authenticated API request, verifies the
content digest against the registered document, performs malware scanning
through an explicit scanner adapter, and extracts text using the existing
safe extractors. Extracted text is returned to the caller and is not silently
persisted in the relational database.
"""
from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from typing import Protocol

from .document_extract import ExtractedDocument, extract_text, validate_upload

MAX_EXTRACTED_TEXT = 5_000_000


class MalwareScanner(Protocol):
    def scan(self, data: bytes) -> None: ...


class ClamAVScanner:
    """Scan bytes with an isolated clamdscan/ClamAV executable.

    The deployment must provide the scanner executable. A non-zero scanner
    result or timeout fails closed. No user-controlled filename is passed to
    the subprocess.
    """

    def __init__(self, command: str = "clamdscan", timeout_seconds: int = 30) -> None:
        self.command = command
        self.timeout_seconds = timeout_seconds

    def scan(self, data: bytes) -> None:
        try:
            completed = subprocess.run(
                [self.command, "--no-summary", "--stdin"],
                input=data,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise RuntimeError("malware_scanner_unavailable_or_timeout") from exc
        if completed.returncode != 0:
            raise ValueError("malware_detected_or_scan_failed")


class RejectingScanner:
    """Safe default when no malware scanner is configured."""

    def scan(self, data: bytes) -> None:
        raise RuntimeError("malware_scanner_not_configured")


@dataclass(frozen=True)
class DocumentProcessingResult:
    sha256: str
    bytes_processed: int
    extraction: ExtractedDocument


def process_document(
    data: bytes,
    *,
    content_type: str,
    expected_sha256: str,
    scanner: MalwareScanner,
) -> DocumentProcessingResult:
    digest = validate_upload(data, content_type)
    expected = expected_sha256.strip().lower()
    if digest != expected:
        raise ValueError("content_hash_mismatch")
    scanner.scan(data)
    extraction = extract_text(data, content_type)
    if len(extraction.text) > MAX_EXTRACTED_TEXT:
        raise ValueError("extracted_text_too_large")
    return DocumentProcessingResult(
        sha256=hashlib.sha256(data).hexdigest(),
        bytes_processed=len(data),
        extraction=extraction,
    )
