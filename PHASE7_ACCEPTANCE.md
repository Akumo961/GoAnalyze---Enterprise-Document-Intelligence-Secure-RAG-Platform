# Phase 7 — Secure document intake and tenant-scoped registration

## Implemented scope

Phase 7 establishes a secure document trust boundary on top of the Phase 6 HTTP service:

- tenant-scoped document registration and listing for an existing case;
- server-side case ownership check before document registration;
- safe filename normalization that strips path components and control characters;
- explicit document content-type allowlist;
- SHA-256 format validation and canonical lowercase storage;
- object-storage URI validation limited to `s3://` and `minio://` references;
- rejection of HTTP(S), query-bearing, fragment-bearing, and path-traversal object references to reduce SSRF/path-confusion risk;
- bounded metadata key/value validation;
- persistent document records using the existing PostgreSQL-compatible `documents` table;
- hash-chained audit event for successful document registration;
- HTTP integration tests covering tenant isolation and malicious metadata/URI inputs.

## Important boundary

This phase registers a document that has already been placed in controlled object storage. It does **not** claim to perform binary upload, antivirus scanning, malware detonation, OCR, or object-storage authorization itself. Those remain deployment/integration gates. A future upload service must calculate the SHA-256 digest from received bytes and scan the object before registration.

The platform also does not dereference caller-supplied URLs, which is an intentional SSRF defense.

## Acceptance gates

The Phase 7 workflow executes:

1. Phase 7 document-security and HTTP integration tests.
2. Full Python test suite.
3. Ruff.
4. mypy.

A green workflow proves only the exact commit tested by GitHub Actions. It does not prove production PostgreSQL, MinIO/S3, malware-scanning, OCR, or external security assessment.

## Governance

Document registration is decision-support infrastructure. No environmental authorization or legally binding decision is made by this phase.

Acceptance workflow trigger: Phase 7 secure document intake verification.
