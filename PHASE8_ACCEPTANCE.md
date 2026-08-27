# Phase 8 — Secure document content processing

## Implemented scope

Phase 8 closes the Phase 7 gap between document registration and safe content processing.

Implemented:

- authenticated, tenant-scoped binary content processing for an already-registered document;
- SHA-256 verification against the registered document before scanning;
- fail-closed malware-scanner abstraction;
- ClamAV/`clamdscan` adapter with timeout and no user-controlled subprocess filename;
- explicit rejecting scanner when a deployment has not configured malware scanning;
- PDF, DOCX, TXT, and CSV extraction through the existing bounded extractor;
- extraction-size limit to reduce resource exhaustion risk;
- audit-chain event for successful document processing;
- cross-tenant isolation at the document lookup boundary;
- tests for hash mismatch, scanner invocation, extraction, tenant isolation, and HTTP processing.

## Deliberate boundaries

This phase does **not** claim:

- a production ClamAV deployment;
- antivirus efficacy or an independent malware-detection assessment;
- OCR as a universally available production service. The existing Tesseract integration remains an explicit executable integration and is not invoked automatically by this endpoint;
- durable binary-object storage. Phase 7 remains the object-storage registration boundary;
- legal/privacy compliance certification;
- autonomous environmental decisions.

The default API scanner intentionally rejects processing when no scanner is configured. A production deployment must wire a managed scanner through dependency configuration before accepting sensitive documents.

## Acceptance gates

The Phase 8 workflow must execute:

1. Phase 8 processing tests.
2. Full Python test suite.
3. Ruff.
4. mypy.

A green result is evidence for the exact commit tested by GitHub Actions only.
