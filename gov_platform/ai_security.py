"""AI security and evaluation utilities for Phase 2."""
from __future__ import annotations

from dataclasses import dataclass

from .rag_engine import contains_prompt_injection


@dataclass(frozen=True)
class CitationEvaluation:
    citation_coverage: float
    unsupported_claim_rate: float
    retrieved_relevant: int
    retrieved_total: int


def sanitize_untrusted_document(text: str) -> str:
    """Mark document content as data; reject obvious instruction payloads."""
    if contains_prompt_injection(text):
        raise ValueError("document_prompt_injection_detected")
    return text


def evaluate_citations(answer: str, cited_document_ids: set[str], required_ids: set[str]) -> CitationEvaluation:
    del answer
    if not required_ids:
        return CitationEvaluation(1.0, 0.0, 0, 0)
    cited = sum(1 for doc_id in required_ids if doc_id in cited_document_ids)
    coverage = cited / len(required_ids)
    unsupported = 0.0 if cited == len(required_ids) else 1.0 - coverage
    return CitationEvaluation(coverage, unsupported, cited, len(required_ids))


def assert_no_cross_tenant_retrieval(request_tenant: str, citation_tenants: list[str]) -> None:
    if any(tenant != request_tenant for tenant in citation_tenants):
        raise PermissionError("cross_tenant_retrieval_blocked")
