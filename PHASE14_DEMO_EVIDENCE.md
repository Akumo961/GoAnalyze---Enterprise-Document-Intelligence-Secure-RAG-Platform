# Phase 14 — Demonstration Evidence

## Status

**Implementation: GREEN for the demo assets and acceptance workflow.**

**Runtime evidence: CI verification pending at the time this document was authored.**

## Implemented

- `demo/synthetic_case.json` provides a reproducible fictional environmental authorization case.
- The dataset is explicitly marked `synthetic_non_authoritative`.
- One expected evidence category (`public_consultation_record`) is intentionally withheld from the case so missing-evidence detection has a deterministic expected result.
- `demo/run_demo.py` exercises the real GoAnalyze persistence models, ingestion pipeline, grounded RAG service, environmental review engine, analyst assignment engine, and hash-chained audit log.
- The runner uses an ephemeral SQLite database and deterministic text input, avoiding dependency on external services or authoritative data.
- `demo/run_demo.ps1` provides a one-command launcher for Windows PowerShell.
- `.github/workflows/phase14-demo.yml` executes the demo and asserts its machine-readable outputs.

## Expected evidence

The acceptance workflow requires:

- at least 10 processed synthetic documents
- `public_consultation_record` in the missing-evidence result
- grounded RAG with at least one citation
- regulatory knowledge status `demo_only`
- human review required
- routing to the technical review queue
- human decision `request_additional_information`
- at least one audit event
- a non-empty audit event hash

## Explicit non-claims

This phase does not establish:

- authoritative Québec regulatory content
- legal interpretation
- privacy or security-law compliance
- government approval or accreditation
- production OCR capability
- production malware scanning
- production infrastructure readiness
- production-scale performance
- HA/DR validation
- LLM quality beyond the deterministic grounded service used by the current repository

The demonstration is decision-support only. A human analyst remains responsible for the decision.
