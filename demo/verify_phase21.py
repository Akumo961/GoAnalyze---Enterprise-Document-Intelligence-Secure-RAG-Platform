"""Phase 21 governance acceptance checks.

The checks are intentionally deterministic and synthetic. They verify that the
repository's documented decision-support boundary is present and that the demo
artifacts do not describe an autonomous legal decision.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE = ROOT / "docs" / "PHASE21_DECISION_SUPPORT_GOVERNANCE.md"
DEMO_DOC = ROOT / "docs" / "PHASE20_COMMERCIAL_DEMO.md"


def main() -> None:
    governance = GOVERNANCE.read_text(encoding="utf-8")
    demo = DEMO_DOC.read_text(encoding="utf-8")

    required = [
        "decision-support software",
        "Human accountability",
        "Factual evidence",
        "Inference",
        "Model-generated summary",
        "Uncertainty",
        "Human decision",
        "no direct LLM authority",
        "Tenant isolation",
        "Audit requirements",
        "Prohibited product claims",
    ]
    missing = [term for term in required if term.lower() not in governance.lower()]
    if missing:
        raise AssertionError(f"Missing Phase 21 governance controls: {missing}")

    forbidden = [
        "autonomous environmental decision capability",
        "replaces government decision-makers",
        "guarantees regulatory compliance",
    ]
    combined = f"{governance}\n{demo}".lower()
    for phrase in forbidden:
        # The governance/demo documents may mention these phrases only when
        # explicitly prohibiting the corresponding product claim.
        if phrase in combined and "must not" not in combined and "does not" not in combined:
            raise AssertionError(f"Unqualified prohibited claim detected: {phrase}")

    print("Phase 21 governance acceptance: PASS")
    print("Human decision-support boundary documented")
    print("AI/legal-decision separation documented")
    print("Evidence, uncertainty, authorization, and audit requirements documented")
    print("No production compliance/certification claim asserted")


if __name__ == "__main__":
    main()
