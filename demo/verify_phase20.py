"""Acceptance checks for the Phase 20 synthetic commercial demonstration.

This verifier deliberately validates the existing offline demo rather than
claiming a live government deployment. All inputs are synthetic and
non-authoritative. The checks prove that the demo exercises the intended
analyst workflow and that its evidence boundary is explicit.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo" / "run_demo.py"
DATASET = ROOT / "demo" / "synthetic_case.json"
REPORT = ROOT / "demo" / "last_run.json"


def main() -> int:
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    assert dataset["authoritativeness"] == "synthetic_non_authoritative"
    assert dataset["notice"]
    assert len(dataset["documents"]) >= 10
    assert dataset["intentionally_missing_document_types"]
    assert dataset["human_decision"]["decision"] == "request_additional_information"

    completed = subprocess.run(
        [sys.executable, str(DEMO)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        print(completed.stdout)
        print(completed.stderr, file=sys.stderr)
        return completed.returncode

    report = json.loads(REPORT.read_text(encoding="utf-8"))
    steps = report["steps"]
    required = {
        "documents_processed": lambda v: v >= 10,
        "missing_documents": lambda v: "public_consultation_record" in v,
        "rag_grounded": lambda v: v is True,
        "rag_citation_count": lambda v: v >= 1,
        "regulatory_knowledge_status": lambda v: v == "demo_only",
        "risk_score": lambda v: isinstance(v, (int, float)),
        "human_review_required": lambda v: v is True,
        "assigned_queue": lambda v: bool(v),
        "human_decision": lambda v: v == "request_additional_information",
        "audit_event_count": lambda v: v >= 1,
        "human_decision_audit_event_hash": lambda v: bool(v),
    }
    for key, predicate in required.items():
        if key not in steps or not predicate(steps[key]):
            raise AssertionError(f"Phase 20 acceptance failed: {key}={steps.get(key)!r}")

    assert report["verification_boundary"] == "synthetic offline execution; not production validation"
    print("Phase 20 commercial demo acceptance: PASS")
    print(f"Synthetic documents processed: {steps['documents_processed']}")
    print(f"Missing evidence detected: {steps['missing_documents']}")
    print(f"Grounded citations: {steps['rag_citation_count']}")
    print(f"Human review required: {steps['human_review_required']}")
    print(f"Analyst queue: {steps['assigned_queue']}")
    print(f"Audit events: {steps['audit_event_count']}")
    print("Boundary: synthetic/non-authoritative; not production or legal validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
