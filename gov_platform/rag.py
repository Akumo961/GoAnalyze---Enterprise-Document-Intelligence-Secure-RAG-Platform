from __future__ import annotations

import time

from .models import AIFinding, EvidenceCitation
from .observability import AI_CITATIONS, AI_REQUESTS, AI_RESPONSE_DURATION


class GroundedRagService:
    def answer(self, question: str, citations: list[EvidenceCitation]) -> AIFinding:
        started = time.perf_counter()
        try:
            grounded = bool(citations)
            if not grounded:
                finding = AIFinding(
                    finding_type="rag_answer",
                    statement="The repository evidence supplied to the RAG service does not support an answer.",
                    confidence=0.0,
                    citations=[],
                    grounded=False,
                    explanation="No citations were available, so the response is withheld.",
                )
            else:
                joined = " ".join(citation.excerpt for citation in citations[:3])
                finding = AIFinding(
                    finding_type="rag_answer",
                    statement=f"Based on cited evidence: {joined[:600]}",
                    confidence=min(0.92, 0.55 + len(citations) * 0.08),
                    citations=citations[:5],
                    grounded=True,
                    explanation="Answer generated only from retrieved citation excerpts.",
                )
            AI_REQUESTS.labels(grounded=str(finding.grounded).lower(), status="success").inc()
            AI_CITATIONS.observe(len(finding.citations))
            return finding
        except Exception:
            AI_REQUESTS.labels(grounded="unknown", status="error").inc()
            raise
        finally:
            AI_RESPONSE_DURATION.observe(time.perf_counter() - started)


rag_service = GroundedRagService()
