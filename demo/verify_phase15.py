"""Acceptance check for Phase 15 observability.

Runs the synthetic Phase 14 workflow in-process, exercises document search,
then verifies that the Prometheus registry contains non-zero measurements for
the business outcomes that the core platform can currently measure.
"""

from __future__ import annotations

import asyncio

from prometheus_client import REGISTRY

from gov_platform.db.session import get_sessionmaker
from gov_platform.observability import HUMAN_DECISIONS
from gov_platform.search import search
from run_demo import main


REQUIRED_METRICS = {
    "goanalyze_documents_processed_total",
    "goanalyze_document_processing_duration_seconds_count",
    "goanalyze_document_stage_duration_seconds_count",
    "goanalyze_missing_evidence_total",
    "goanalyze_search_requests_total",
    "goanalyze_search_duration_seconds_count",
    "goanalyze_ai_requests_total",
    "goanalyze_ai_response_duration_seconds_count",
    "goanalyze_ai_citations_per_response_count",
    "goanalyze_cases_reviewed_total",
    "goanalyze_case_risk_score_count",
    "goanalyze_human_review_required_total",
    "goanalyze_case_assignments_total",
}


def metric_values() -> dict[str, float]:
    values: dict[str, float] = {}
    for family in REGISTRY.collect():
        for sample in family.samples:
            values[sample.name] = float(sample.value)
    return values


async def run() -> None:
    await main()

    # The Phase 14 demo DB is intentionally ephemeral. Exercise the real
    # search service against it so search latency/backend selection is measured.
    async with get_sessionmaker()() as session:
        result = await search(
            session,
            tenant_id="demo-melccfp-01",
            query="industrial discharge",
            page=1,
            page_size=20,
        )
        assert result.backend in {"opensearch", "database_fallback"}

    values = metric_values()
    missing = sorted(name for name in REQUIRED_METRICS if name not in values)
    if missing:
        raise AssertionError(f"Missing Phase 15 metrics: {missing}")

    positive = {
        "goanalyze_documents_processed_total": values["goanalyze_documents_processed_total"],
        "goanalyze_document_processing_duration_seconds_count": values[
            "goanalyze_document_processing_duration_seconds_count"
        ],
        "goanalyze_document_stage_duration_seconds_count": values[
            "goanalyze_document_stage_duration_seconds_count"
        ],
        "goanalyze_missing_evidence_total": values["goanalyze_missing_evidence_total"],
        "goanalyze_search_requests_total": values["goanalyze_search_requests_total"],
        "goanalyze_search_duration_seconds_count": values["goanalyze_search_duration_seconds_count"],
        "goanalyze_ai_requests_total": values["goanalyze_ai_requests_total"],
        "goanalyze_ai_response_duration_seconds_count": values[
            "goanalyze_ai_response_duration_seconds_count"
        ],
        "goanalyze_ai_citations_per_response_count": values["goanalyze_ai_citations_per_response_count"],
        "goanalyze_cases_reviewed_total": values["goanalyze_cases_reviewed_total"],
        "goanalyze_case_risk_score_count": values["goanalyze_case_risk_score_count"],
        "goanalyze_human_review_required_total": values["goanalyze_human_review_required_total"],
        "goanalyze_case_assignments_total": values["goanalyze_case_assignments_total"],
    }
    zero = [name for name, value in positive.items() if value <= 0]
    if zero:
        raise AssertionError(f"Expected non-zero Phase 15 measurements: {zero}")

    assert HUMAN_DECISIONS.labels(decision="request_additional_information")._value.get() >= 1

    print("Phase 15 observability acceptance passed.")
    for name, value in positive.items():
        print(f"{name}={value}")
    print("Queue backlog and workflow-SLA metrics are integration surfaces; this offline demo does not invent external-service measurements.")


if __name__ == "__main__":
    asyncio.run(run())
