"""Security validation for government document registration.

This module validates document metadata at the trust boundary. It deliberately
accepts only object-storage URIs (s3:// or minio://) and never dereferences a
caller-supplied HTTP URL, preventing SSRF through document ingestion.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from fastapi import HTTPException, status

ALLOWED_CONTENT_TYPES = frozenset(
    {
        "application/pdf",
        "text/plain",
        "text/csv",
        "application/json",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
)
MAX_FILENAME_LENGTH = 255
MAX_METADATA_KEYS = 64
MAX_METADATA_VALUE_LENGTH = 4096
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def sanitize_filename(filename: str) -> str:
    """Return a safe display name; never use it as a filesystem path."""
    value = filename.strip().replace("\\", "/").split("/")[-1]
    value = re.sub(r"[\x00-\x1f\x7f]", "", value)
    value = value.strip(" .")
    if not value or value in {".", ".."}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_filename")
    if len(value) > MAX_FILENAME_LENGTH:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="filename_too_long")
    return value


def validate_content_type(content_type: str) -> str:
    value = content_type.strip().lower()
    if value not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="unsupported_content_type")
    return value


def validate_sha256(sha256: str) -> str:
    value = sha256.strip().lower()
    if not _SHA256_RE.fullmatch(value):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_sha256")
    return value


def validate_object_uri(object_uri: str) -> str:
    """Allow storage references but reject network URLs and path traversal."""
    value = object_uri.strip()
    parsed = urlparse(value)
    if parsed.scheme not in {"s3", "minio"} or not parsed.netloc or parsed.query or parsed.fragment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_object_uri")
    if ".." in parsed.path.split("/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_object_uri")
    return value


def validate_metadata(metadata: dict[str, object]) -> dict[str, object]:
    if len(metadata) > MAX_METADATA_KEYS:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="metadata_too_large")
    for key, value in metadata.items():
        if not isinstance(key, str) or not key.strip() or len(key) > 128:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_metadata_key")
        if isinstance(value, str) and len(value) > MAX_METADATA_VALUE_LENGTH:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="metadata_value_too_large")
    return metadata
