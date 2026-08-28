# Phase 20 — Commercial Demonstration

## Purpose

Phase 20 provides a reproducible, stakeholder-facing demonstration scenario for GoAnalyze Government. It uses **synthetic, non-authoritative data only** and demonstrates decision-support capabilities without making or simulating a legally binding government decision.

## Scenario

A fictional industrial applicant submits an environmental authorization package. The case contains a synthetic document set with one intentionally withheld evidence category. GoAnalyze processes the package, identifies missing evidence, retrieves grounded evidence, presents demo-only regulatory knowledge, scores review priority, routes the case to a human analyst, and records the analyst's decision in the audit trail.

The repository's current deterministic demo uses a compact synthetic package rather than an artificial claim of an 80-document production workload. An expanded 80-document pilot dataset can be added later when a realistic benchmark is defined.

## Demonstrated workflow

| Step | Demonstrated | Evidence |
|---|---|---|
| 1. Upload/register application documents | Yes, synthetic offline registration | `demo/run_demo.py` |
| 2. Extract/process document content | Yes, deterministic text ingestion path | `demo/run_demo.py` |
| 3. Detect missing documents | Yes | `missing_documents` in `last_run.json` |
| 4. Search/retrieve case evidence | Yes, grounded citation objects | RAG finding in `run_demo.py` |
| 5. Ask an AI question | Yes, grounded RAG service invocation | `rag_service.answer()` |
| 6. Show source citations | Yes | `EvidenceCitation` records |
| 7. Map evidence to regulatory requirements | Yes, explicitly marked `demo_only` | `EnvironmentalReviewRequest` / review engine |
| 8. Generate risk/priority assessment | Yes | `risk_score` and `human_review_required` |
| 9. Route to human analyst | Yes | assignment engine and persisted assignment |
| 10. Record analyst decision and audit trail | Yes | human decision audit event and hash |

## What is intentionally NOT claimed

This demonstration does **not** prove:

- production OCR for arbitrary scanned documents;
- production-scale performance;
- authoritative Québec regulatory content;
- legal or regulatory correctness;
- government approval or accreditation;
- a production security assessment;
- an autonomous environmental decision capability;
- an 80-document production workload benchmark.

Regulatory knowledge in the dataset is explicitly fictional and non-authoritative. Human accountability is preserved: the demonstration records a human request for additional information rather than allowing the model to issue a legal decision.

## Reproduce

From the repository root:

```bash
python demo/run_demo.py
python demo/verify_phase20.py
```

On Windows PowerShell:

```powershell
python demo\run_demo.py
python demo\verify_phase20.py
```

The runner creates an ephemeral SQLite database and writes execution evidence to `demo/last_run.json`. The generated evidence is local execution evidence only and must not be represented as production validation.

## Commercial demonstration boundary

For a buyer-facing pilot, the synthetic scenario should be replaced by customer-approved test data under the customer's security, privacy, retention, and regulatory-governance controls. Authoritative regulatory sources should be loaded through an approved knowledge-ingestion process and versioned so that every answer can identify its source and effective version.
