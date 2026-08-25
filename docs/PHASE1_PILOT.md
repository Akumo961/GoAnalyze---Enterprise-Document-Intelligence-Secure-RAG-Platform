# Phase 1 — Synthetic Environmental Pilot

## Status

**Implemented as a deterministic synthetic evaluation workflow.** The workflow is designed to be runnable without external services and is intentionally separate from claims about production deployment.

## Acceptance workflow

1. Create a reproducible synthetic environmental application.
2. Load 10 synthetic documents.
3. Classify documents.
4. Check required evidence completeness.
5. Answer a question only from available synthetic evidence and return citations.
6. Map synthetic evidence to explicitly `demo` regulatory obligations.
7. Calculate a transparent synthetic priority score.
8. Route the case to a human analyst queue.
9. Record a human analyst decision and note.
10. Produce a complete in-memory audit trail.
11. Emit measurable pilot metrics.

## Run

From the repository root:

```bash
python scripts/run_phase1_demo.py
```

The command does not require PostgreSQL, OpenSearch, MinIO, Keycloak, Redis, an LLM provider, or internet access. It exercises the deterministic pilot implementation in `gov_platform/phase1_demo.py`.

## Test

```bash
pytest tests/test_phase1_demo.py
```

## Synthetic case

The case is deliberately fictional:

- Applicant: `Demo Industries Inc.`
- Project: `North River Synthetic Industrial Facility`
- Project type: synthetic industrial-discharge review
- Documents: 10
- Tenant: `demo-ministry`

No real applicant, permit, ministry decision, legal obligation, performance result, or government record is represented.

## Regulatory safety boundary

The regulatory source is explicitly marked `demo`. It is **not** an authoritative Québec legal source and must never be presented as one. The Phase 1 implementation demonstrates the architecture for provenance-bearing regulatory knowledge; authoritative sources must be loaded and approved by an authorized customer governance process later.

## Human accountability

The system produces decision-support artifacts only. The synthetic analyst decision is explicitly recorded as a human action. No legally binding environmental decision is made by GoAnalyze.

## Evidence produced

The JSON output contains:

- case identity
- document count
- completeness result
- grounded question result and citations
- regulatory mappings and coverage
- priority score and method
- analyst assignment
- human decision
- audit events
- processing-time/document-count/citation metrics
- regulatory authority and decision-support governance flags

## What Phase 1 does not prove

This pilot does not prove:

- production RAG quality
- OCR accuracy on arbitrary scans
- malware scanning
- production OpenSearch/MinIO behavior
- production Kubernetes resilience
- Québec legal compliance
- privacy compliance
- accessibility certification
- penetration-test results
- government deployment approval
- ROI
- production readiness
