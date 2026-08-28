"""Deterministic Phase 22 governance acceptance checks."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "PHASE22_HUMAN_ACCOUNTABILITY.md"


def main() -> None:
    text = DOC.read_text(encoding="utf-8").lower()
    required = [
        "human accountability",
        "must not autonomously",
        "explicitly authorized human action",
        "human actor identifier",
        "human override",
        "separation of authority",
        "consequential workflow APIs",
        "enforce authorization independently",
        "engineering evidence only",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(f"Missing Phase 22 controls: {missing}")

    print("Phase 22 acceptance: PASS")
    print("Human accountability boundary: PASS")
    print("Human override requirement: PASS")
    print("Independent authorization requirement: PASS")
    print("Decision-record requirements: PASS")
    print("Verification limitations explicitly documented: PASS")


if __name__ == "__main__":
    main()
