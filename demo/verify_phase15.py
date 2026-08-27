"""Acceptance check for Phase 15 observability.

Runs the synthetic Phase 14 workflow in-process, then verifies that the
Prometheus registry contains non-zero measurements for the business outcomes
that can currently be measured by the core platform.
"""

from __future__ import annotations

import asyncio

from prometheus_client import REGISTRY

from run_demo import main


REQUIRED_METRICS = {
    "goanalyze_documents_processed_total",
    "goanalyze_document_processing_duration_seconds_count",
    "goanalyze_document_stage_duration_seconds_count",
    "goanalyze_missing_evidence_total",
    "goanalyze_search_requests_total",
    "goanalyze_ai_requests_total",
    "goanalyze_ai_response_duration_seconds_count",
    "goanalyze_ai_citations_per_response_count",
    "goanalyze_cases_reviewed_total",
    "goanalyze_case_risk_score_count",
    "goanalyze_human_review_required_total",
}


def metric_values() -> dict[str, float]:
    values: dict[str, float] = {}
    for family in REGISTRY.collect():
        for sample in family.samples:
            values[sample.name] = float(sample.value)
    return values


async def run() -> None:
    await main()
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
        "goanalyze_ai_requests_total": values["goanalyze_ai_requests_total"],
        "goanalyze_ai_response_duration_seconds_count": values[
            "goanalyze_ai_response_duration_seconds_count"
        ],
        "goanalyze_ai_citations_per_response_count": values["goanalyze_ai_citations_per_response_count"],
        "goanalyze_cases_reviewed_total": values["goanalyze_cases_reviewed_total"],
        "goanalyze_case_risk_score_count": values["goanalyze_case_risk_score_count"],
        "goanalyze_human_review_required_total": values["goanalyze_human_review_required_total"],
    }
    zero = [name for name, value in positive.items() if value <= 0]
    if zero:
        raise AssertionError(f"Expected non-zero Phase 15 measurements: {zero}")

    print("Phase 15 observability acceptance passed.")
    for name, value in positive.items():
        print(f"{name}={value}")
    print("Search and queue backlog are exposed as measurement/integration surfaces; this offline demo does not invent external-service measurements.")


if __name__ == "__main__":
    asyncio.run(run())
