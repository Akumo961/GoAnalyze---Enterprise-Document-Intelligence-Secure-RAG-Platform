# GoAnalyze Government — Phase 14 Demonstration Environment

This directory contains a reproducible stakeholder demonstration built on the real GoAnalyze domain components.

## What it demonstrates

The scenario is a fictional Québec environmental authorization case. It uses **synthetic, non-authoritative data only**.

1. Register a multi-document application case.
2. Process supplied documents through the real ingestion pipeline (with deterministic text supplied to the pipeline so the demo remains offline).
3. Extract metadata and classify documents.
4. Detect missing evidence: the synthetic public-consultation record is intentionally withheld from the case.
5. Build evidence citations from persisted document records.
6. Generate a grounded RAG answer using only those citations.
7. Run environmental completeness, regulatory-mapping and risk-screening logic.
8. Route the case to a human review queue.
9. Record the analyst's `request_additional_information` decision in the hash-chained audit log.
10. Emit machine-readable execution evidence.

## Run

From the repository root:

```bash
python demo/run_demo.py
```

The runner requires the same Python dependencies as the application. It does **not** require Docker, PostgreSQL, OpenSearch, MinIO, Kafka, Temporal, Keycloak, an LLM provider, or Internet access. It uses an ephemeral SQLite database and real application components.

On Windows PowerShell:

```powershell
python .\demo\run_demo.py
```

## Output

The command prints a JSON execution report and writes `demo/last_run.json` locally. The report includes:

- number of documents processed
- missing document types
- RAG grounded status and citation count
- regulatory knowledge status (`demo_only`)
- risk score
- human-review requirement
- assigned queue
- human decision
- audit-event count and event hash
- per-document processing results

`last_run.json` is intentionally generated locally and should not be treated as a repository claim or production evidence artifact.

## Evidence boundary

This demo proves that the selected workflow can execute deterministically in an offline development environment. It does **not** prove:

- Québec legal or regulatory correctness
- production OCR quality
- production malware-scanning efficacy
- government security accreditation
- production-scale performance
- high availability or disaster recovery
- production deployment on government infrastructure
- LLM factual accuracy beyond the deterministic grounded RAG implementation
- legal compliance or certification

The human analyst remains responsible for any decision. No legally binding environmental decision is automated.
