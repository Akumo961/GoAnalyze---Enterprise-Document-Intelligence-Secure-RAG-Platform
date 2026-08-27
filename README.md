# GoAnalyze Government

**Secure environmental document intelligence and AI-assisted decision support for Québec public-sector organizations.**

GoAnalyze is being engineered as a government-oriented platform for analysts who work with environmental applications, permits, technical studies, inspection records, correspondence, evidence packages and regulatory material.

> **Important:** This repository does not claim government approval, certification, regulatory compliance, production deployment, customers, security certification or independent audit. Capabilities are described conservatively and are tracked in `PRODUCTION_READINESS.md`.

## Product workflow

```text
Secure ingestion
  -> extraction / OCR
  -> metadata + classification
  -> completeness screening
  -> search / retrieval
  -> evidence-grounded AI assistance
  -> citation + provenance checks
  -> regulatory knowledge mapping
  -> missing-evidence detection
  -> risk / priority support
  -> analyst queue
  -> human review and disposition
  -> audit trail + reporting
```

GoAnalyze is **decision-support software**. It must not autonomously issue legally binding environmental decisions. Human accountability remains part of the workflow.

## Architecture

- FastAPI application services
- PostgreSQL persistence
- OpenSearch integration for search/retrieval
- MinIO/S3-compatible object storage integration
- Redis-backed rate limiting and operational controls
- Keycloak/OIDC-compatible identity architecture
- OpenTelemetry instrumentation
- Prometheus-compatible metrics
- Kubernetes / Helm / Terraform deployment artifacts
- Docker production images

The intended deployment model supports government-controlled cloud, private cloud and on-premises environments, subject to environment-specific validation.

## Security model

The application includes or is being hardened around:

- signed OIDC/JWT authentication
- RBAC and tenant-aware authorization
- ABAC policy checks for tenant, classification and purpose
- hash-chained audit records
- secure headers and rate limiting
- upload-size and filename protections
- fail-closed production configuration
- AI evidence and citation controls
- explicit separation between demo/unverified and authoritative regulatory knowledge

See `PRODUCTION_READINESS.md` for the evidence boundary.

## Regulatory knowledge

GoAnalyze does **not** embed fictional Québec legal requirements. Regulatory obligations are represented through a versioned knowledge model containing source provenance, jurisdiction, status, evidence requirements, deadlines, exceptions and lifecycle metadata.

The repository's demonstration knowledge pack is synthetic and explicitly marked **DEMO ONLY — NOT AUTHORITATIVE**. An actual government deployment would require an authorized process to load, validate, approve, version and retire authoritative sources.

## Demonstration boundary

The repository contains a government-oriented engineering foundation and deployment artifacts. Some capabilities remain partially implemented or unverified, including live OCR, production vector retrieval, complete LLM integration, full workflow persistence, real infrastructure validation, penetration testing and privacy/legal assessment.

Do not interpret architecture diagrams or configuration files as proof that an external service has been deployed or validated.

## Evidence and documentation

Key documents:

- `ARCHITECTURE.md` — target architecture and data flows
- `PRODUCTION_READINESS.md` — authoritative evidence-based readiness baseline
- `PROCUREMENT_READINESS.md` — proposed procurement and commercial packaging model
- `EXECUTION_EVIDENCE.md` — historical execution evidence with limitations
- `FINAL_PRODUCTION_READINESS.md` — historical cumulative report; superseded for current status by `PRODUCTION_READINESS.md`
- `BUSINESS_CASE.md` — measurable business outcomes and instrumentation concepts
- `SECURITY.md` / `AI_SAFETY.md` — security and AI safety design material

## Engineering principle

The objective is not to make GoAnalyze look like a large government platform. The objective is to build evidence that a serious public-sector buyer could evaluate: secure implementation, reproducible tests, transparent limitations, governed regulatory knowledge, measurable workflow outcomes, and human accountability.
