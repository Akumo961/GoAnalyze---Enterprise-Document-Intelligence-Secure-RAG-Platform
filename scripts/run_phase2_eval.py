"""Run the offline Phase 2 RAG/security evaluation without external services."""
from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from gov_platform.ai_security import evaluate_citations, sanitize_untrusted_document
from gov_platform.models import EvidenceCitation
from gov_platform.rag_engine import ProductionRAG, retrieve


def main() -> None:
    cases = json.loads(Path("evals/phase2_benchmark.json").read_text(encoding="utf-8"))
    passed = 0
    results = []
    for case in cases:
        citations = [EvidenceCitation(document_id=uuid4(), version=1, chunk_id=str(i), sha256="a" * 64, excerpt=text) for i, text in enumerate(case["evidence"])]
        for text in case.get("untrusted_documents", []):
            try:
                sanitize_untrusted_document(text)
                safe = True
            except ValueError:
                safe = False
            assert safe is (not case.get("expects_injection", False))
        retrieved = retrieve(case["question"], citations)
        answer = ProductionRAG().answer(case["question"], citations)
        expected = case["expected_relevant"]
        relevant = sum(1 for item in retrieved if expected.lower() in item.citation.excerpt.lower())
        metric = evaluate_citations(answer.statement, {str(c.document_id) for c in answer.citations}, {str(c.document_id) for c in answer.citations})
        ok = (relevant >= case["min_relevant"]) and (answer.grounded == case["grounded"])
        passed += int(ok)
        results.append({"id": case["id"], "passed": ok, "retrieved": len(retrieved), "relevant": relevant, "citation_coverage": metric.citation_coverage})
    output = {"benchmark": "phase2-offline-v1", "passed": passed, "total": len(cases), "results": results}
    print(json.dumps(output, indent=2, sort_keys=True))
    if passed != len(cases):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
