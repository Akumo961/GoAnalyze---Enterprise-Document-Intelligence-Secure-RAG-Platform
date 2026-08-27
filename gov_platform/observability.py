"""Business and operational telemetry for measurable GoAnalyze outcomes.

Metrics are deliberately aggregate and low-cardinality. Tenant identifiers,
document IDs, filenames, prompts, applicant names, and other customer data
must never become Prometheus labels.

The metrics expose *measurements*, not claimed business outcomes. A pilot or
production deployment must establish its own baseline and targets.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter

from prometheus_client import Counter, Gauge, Histogram


DOCUMENTS_PROCESSED = Counter(
    "goanalyze_documents_processed_total",
    "Documents successfully processed by the ingestion pipeline.",
    ["status"],
)
DOCUMENT_PROCESSING_DURATION = Histogram(
    "goanalyze_document_processing_duration_seconds",
    "End-to-end document processing duration in seconds.",
    buckets=(0.1, 0.5, 1, 2, 5, 10, 30, 60, 120, 300, 600),
)
DOCUMENT_STAGE_DURATION = Histogram(
    "goanalyze_document_stage_duration_seconds",
    "Document pipeline stage duration in seconds.",
    ["stage"],
    buckets=(0.001, 0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10, 30, 60),
)
DOCUMENTS_MISSING = Counter(
    "goanalyze_missing_evidence_total",
    "Missing evidence/document categories detected by environmental review.",
)
SEARCH_REQUESTS = Counter(
    "goanalyze_search_requests_total",
    "Document search requests completed.",
    ["backend", "status"],
)
SEARCH_DURATION = Histogram(
    "goanalyze_search_duration_seconds",
    "Document search latency in seconds.",
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)
AI_REQUESTS = Counter(
    "goanalyze_ai_requests_total",
    "Grounded AI/RAG requests completed.",
    ["grounded", "status"],
)
AI_RESPONSE_DURATION = Histogram(
    "goanalyze_ai_response_duration_seconds",
    "Grounded AI/RAG response latency in seconds.",
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30),
)
AI_CITATIONS = Histogram(
    "goanalyze_ai_citations_per_response",
    "Number of source citations attached to a grounded AI response.",
    buckets=(0, 1, 2, 3, 5, 10, 20),
)
CASES_REVIEWED = Counter(
    "goanalyze_cases_reviewed_total",
    "Environmental case reviews completed.",
)
RISK_SCORE = Histogram(
    "goanalyze_case_risk_score",
    "Risk score distribution produced by the review engine (0-100).",
    buckets=(0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100),
)
HUMAN_REVIEW_REQUIRED = Counter(
    "goanalyze_human_review_required_total",
    "Environmental review results requiring human review.",
    ["required"],
)
CASE_ASSIGNMENTS = Counter(
    "goanalyze_case_assignments_total",
    "Cases routed to analyst queues.",
    ["queue"],
)
QUEUE_BACKLOG = Gauge(
    "goanalyze_queue_backlog",
    "Current queue backlog when an authoritative workflow adapter reports it.",
    ["queue"],
)
HUMAN_DECISIONS = Counter(
    "goanalyze_human_decisions_total",
    "Human case decisions recorded through the audit workflow.",
    ["decision"],
)
HUMAN_OVERRIDES = Counter(
    "goanalyze_human_overrides_total",
    "Human decisions explicitly recorded as overrides of an AI/system recommendation.",
)
WORKFLOW_SLA_SECONDS = Histogram(
    "goanalyze_workflow_sla_seconds",
    "Elapsed workflow time measured by an integration adapter when a case reaches a terminal or review milestone.",
    buckets=(60, 300, 900, 1800, 3600, 14400, 28800, 86400, 259200, 604800),
)


def record_human_decision(decision: str, *, override: bool = False) -> None:
    """Record an aggregate human decision without storing case/customer data."""
    HUMAN_DECISIONS.labels(decision=decision).inc()
    if override:
        HUMAN_OVERRIDES.inc()


@contextmanager
def observe_seconds(histogram: Histogram, *labels: str) -> Iterator[None]:
    """Observe a synchronous operation without retaining customer data."""
    start = perf_counter()
    try:
        yield
    finally:
        histogram.labels(*labels).observe(perf_counter() - start)
