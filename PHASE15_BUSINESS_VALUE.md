# Phase 15 — Business Value Instrumentation

## Purpose

Phase 15 adds measurable instrumentation so a pilot can establish real operational and business baselines without inventing ROI or performance claims.

The platform now exposes Prometheus metrics for document throughput and processing time, pipeline-stage latency, missing evidence, search latency/backend outcomes, grounded AI response latency/citation counts, case-review throughput, risk-score distribution, human-review requirement, and analyst routing.

## Metrics implemented

| Measurement | Metric family | Current source |
|---|---|---|
| Documents processed | `goanalyze_documents_processed_total` | Ingestion pipeline |
| End-to-end processing time | `goanalyze_document_processing_duration_seconds` | Ingestion pipeline |
| Per-stage processing time | `goanalyze_document_stage_duration_seconds` | Ingestion pipeline |
| Missing evidence | `goanalyze_missing_evidence_total` | Environmental review engine |
| Search requests/backend | `goanalyze_search_requests_total` | Search service |
| Search latency | `goanalyze_search_duration_seconds` | Search service |
| AI/RAG requests | `goanalyze_ai_requests_total` | Grounded RAG service |
| AI/RAG latency | `goanalyze_ai_response_duration_seconds` | Grounded RAG service |
| Citations per AI response | `goanalyze_ai_citations_per_response` | Grounded RAG service |
| Cases reviewed | `goanalyze_cases_reviewed_total` | Environmental review engine |
| Risk-score distribution | `goanalyze_case_risk_score` | Environmental review engine |
| Human review requirement | `goanalyze_human_review_required_total` | Environmental review engine |
| Analyst routing | `goanalyze_case_assignments_total` | Assignment engine |
| Queue backlog | `goanalyze_queue_backlog` | Integration adapter API; not inferred by the core application |
| Workflow SLA elapsed time | `goanalyze_workflow_sla_seconds` | Integration adapter API; requires lifecycle timestamps |
| Human decisions | `goanalyze_human_decisions_total` | Audit workflow when `case.human_decision_recorded` is emitted |
| Explicit AI overrides | `goanalyze_human_overrides_total` | Audit workflow when `ai_override=true` is recorded |

## Privacy and cardinality boundary

Prometheus labels intentionally do **not** contain tenant IDs, case IDs, document IDs, applicant names, filenames, prompts, excerpts, or other customer content. This avoids turning operational telemetry into a secondary customer-data store and prevents unbounded metric cardinality.

## How a pilot can measure value

The platform now provides the technical measurement points needed to establish a baseline before a pilot and compare the same measures during/after deployment:

- processing time per document/case
- documents processed per period
- search latency
- AI response latency
- citation coverage/counts
- missing-evidence detection frequency
- human-review requirement
- analyst routing volume
- queue backlog when connected to the authoritative workflow system
- workflow SLA elapsed time when lifecycle events are integrated
- human override rate when AI recommendations and human decisions are explicitly correlated
- case throughput

ROI, time savings, and productivity improvements remain **unverified until measured on real pilot data**.

## Verification

`demo/verify_phase15.py` runs the synthetic Phase 14 scenario, exercises the real search service, and asserts that the relevant metric families are present and receive non-zero observations.

`.github/workflows/phase15-observability.yml` executes that acceptance check in GitHub Actions.

The Phase 15 acceptance test is synthetic/offline evidence. It does not establish production-scale performance, an SLA, or a government business case.

## Important limitation

The core repository does not currently have an authoritative external workflow system providing real queue-backlog and end-to-end lifecycle timestamps. Those metrics are therefore exposed as integration surfaces rather than fabricated values.
