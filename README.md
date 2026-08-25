# GoAnalyze Government

Secure environmental document intelligence and AI-assisted decision support for government workflows.

> **Evidence-first positioning:** this repository contains a substantial enterprise application foundation, but it is not presented as government-certified, production-approved, or procurement-approved. Capabilities are classified by evidence in [`PRODUCTION_READINESS.md`](PRODUCTION_READINESS.md).

## Target use

GoAnalyze Government is designed to help public-sector analysts process environmental applications, permits, studies, inspection records, correspondence and compliance evidence while preserving human accountability.

Core workflow target:

**ingest → extract/OCR → classify → completeness → search → evidence/citations → regulatory mapping → risk/priority → analyst review → human decision → audit/export**

## Current engineering foundation

The repository currently includes:

- FastAPI backend and Next.js frontend
- PostgreSQL persistence and migrations
- Keycloak/OIDC JWT verification with issuer, audience, expiry and signature validation
- RBAC/ABAC authorization and tenant-scoped access controls
- Hash-chained audit records, including a concurrency fix verified against real PostgreSQL
- Document upload/download APIs with size limits, SHA-256 integrity checks and server-derived storage keys
- Search API with OpenSearch integration path and database fallback
- Redis-backed rate limiting
- OpenTelemetry instrumentation
- Docker, Kubernetes/Helm and Terraform deployment artifacts
- Automated Python/frontend quality checks and GitHub Actions CI configuration
- CycloneDX SBOM generation evidence
- Environmental review primitives for completeness, evidence mapping and risk/priority support

These capabilities are not equivalent to a completed government production deployment. See the readiness register for the exact evidence and limitations.

## Critical limitation: AI/RAG maturity

The current RAG service is citation-grounded application logic, not yet a complete production LLM/RAG stack with a validated model provider, retrieval benchmark, citation-accuracy benchmark and prompt-injection evaluation suite. This is intentionally stated plainly so the repository does not overclaim.

## Regulatory knowledge

GoAnalyze does **not** invent Québec legal requirements. Regulatory knowledge is modeled as versioned, provenance-bearing sources and obligations that must be authoritative or customer-approved before they can drive regulatory assertions. Demo/unverified material must remain clearly labeled.

## Security and AI governance

See [`docs/SECURITY_AI_GOVERNANCE.md`](docs/SECURITY_AI_GOVERNANCE.md). Uploaded documents are untrusted input. Tenant boundaries, authorization, citation provenance, prompt-injection resistance, model permissions, auditability and human review are treated as security controls rather than marketing claims.

## Government deployment model

The architecture is intended to support government-controlled cloud, private cloud, on-premises and isolated deployments, subject to validating the actual infrastructure configuration in the target environment. The architecture document contains both implemented components and target-state components; diagrams are not proof of production integration.

## Commercial model

The proposed commercial model separates:

1. Core platform
2. Government configuration
3. Environmental/customer integrations
4. Customer data
5. Customer-approved regulatory knowledge
6. Enterprise deployment and services

Potential commercial packaging is described in [`docs/GOVERNMENT_PRODUCT.md`](docs/GOVERNMENT_PRODUCT.md) and [`docs/PROCUREMENT_READINESS.md`](docs/PROCUREMENT_READINESS.md). No contract value is asserted.

## Decision-support boundary

GoAnalyze Government is decision-support software. It must not autonomously issue legally binding environmental decisions. AI findings, regulatory mappings and risk/priority assessments require appropriate evidence and human review.

## Evidence-first documentation

- [`PRODUCTION_READINESS.md`](PRODUCTION_READINESS.md) — authoritative current readiness register
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — target/logical architecture
- [`FINAL_SECURITY_REPORT.md`](FINAL_SECURITY_REPORT.md) — recorded security testing evidence
- [`FINAL_PRODUCTION_READINESS.md`](FINAL_PRODUCTION_READINESS.md) — historical readiness assessment
- [`FEATURE_COMPLETION_REPORT.md`](FEATURE_COMPLETION_REPORT.md) — documented feature implementation evidence
- [`docs/SECURITY_AI_GOVERNANCE.md`](docs/SECURITY_AI_GOVERNANCE.md) — AI/security control model
- [`docs/GOVERNMENT_PRODUCT.md`](docs/GOVERNMENT_PRODUCT.md) — product and commercial boundary
- [`docs/PROCUREMENT_READINESS.md`](docs/PROCUREMENT_READINESS.md) — buyer evaluation framework

## Disclaimer

This project is an evolving commercial/product engineering effort. No customer deployment, government endorsement, regulatory approval, certification, legal conclusion or security accreditation is claimed unless independently documented with evidence.
