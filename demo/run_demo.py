"""Run the GoAnalyze Government synthetic environmental-review demonstration.

This runner deliberately exercises the real domain models, ingestion pipeline,
grounded RAG service, environmental review engine, assignment engine, and
hash-chained audit log against an ephemeral SQLite database. No network,
external LLM, government system, or authoritative regulatory source is used.

Usage:
    python demo/run_demo.py

The generated JSON report is evidence of this demo execution only; it is not
production validation and contains synthetic data.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import tempfile
from pathlib import Path
from uuid import UUID

# Keep the demo self-contained and offline. Settings are read when the GoAnalyze
# modules are imported, so environment variables must be established first.
DB_FILE = Path(tempfile.gettempdir()) / "goanalyze_phase14_demo.sqlite3"
os.environ.setdefault("GOV_ENVIRONMENT", "development")
os.environ.setdefault("GOV_DATABASE_URL", f"sqlite+aiosqlite:///{DB_FILE}")
os.environ.setdefault("GOV_AUDIT_HASH_SECRET", "phase14-demo-only-not-a-production-secret")
os.environ.setdefault("GOV_OTEL_TRACING_ENABLED", "false")

from gov_platform.audit import audit_log  # noqa: E402
from gov_platform.db.models import Base  # noqa: E402
from gov_platform.db.repositories import CaseRepository, DocumentRepository  # noqa: E402
from gov_platform.db.session import get_engine, get_sessionmaker  # noqa: E402
from gov_platform.environmental_engine import engine  # noqa: E402
from gov_platform.ingestion import ingestion_pipeline  # noqa: E402
from gov_platform.models import AuditEvent, DocumentRecord, EnvironmentalReviewRequest, EvidenceCitation  # noqa: E402
from gov_platform.rag import rag_service  # noqa: E402
from gov_platform.workflows import assignment_engine  # noqa: E402

ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "synthetic_case.json"
REPORT = ROOT / "last_run.json"
TENANT = "demo-melccfp-01"
ACTOR = "demo-analyst-01"
CASE_ID = UUID("00000000-0000-4000-8000-000000000014")


async def main() -> None:
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    if dataset["authoritativeness"] != "synthetic_non_authoritative":
        raise RuntimeError("Demo dataset must remain explicitly non-authoritative")

    if DB_FILE.exists():
        DB_FILE.unlink()

    engine_db = get_engine()
    async with engine_db.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    sessionmaker = get_sessionmaker()
    processed: list[dict] = []

    async with sessionmaker() as session:
        document_ids: list[UUID] = []
        available_types: set[str] = set()

        # 1-3: register, extract/classify/metadata-process, and index synthetic documents.
        for item in dataset["documents"]:
            content = item["content"]
            digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
            record = DocumentRecord(
                tenant_id=TENANT,
                case_id=CASE_ID,
                filename=item["filename"],
                content_type="text/plain",
                classification="internal",
                sha256=digest,
                object_uri=f"s3://demo/{TENANT}/{item['filename']}",
                metadata={
                    "document_type": item["document_type"],
                    "project_type": dataset["case"]["project_type"],
                    "location": dataset["case"]["location"],
                    "applicant": dataset["case"]["applicant"],
                    "synthetic": True,
                },
            )
            await DocumentRepository(session).create(record)
            result = await ingestion_pipeline.run(
                record=record,
                actor=ACTOR,
                trace_id=f"phase14-{record.id}",
                purpose="synthetic-demo",
                session=session,
                raw_text=content,
            )
            document_ids.append(record.id)
            available_types.add(item["document_type"])
            processed.append(
                {
                    "document_id": str(record.id),
                    "filename": record.filename,
                    "document_type": item["document_type"],
                    "classification": result.classification_label,
                    "entities": result.extracted_entities,
                    "risk_score": result.risk_score,
                    "workflow_queue": result.workflow_queue,
                    "completed": result.completed,
                }
            )

        # 4-8: search is represented by the real citation objects and grounded RAG service.
        citations = [
            EvidenceCitation(
                document_id=doc_id,
                version=1,
                chunk_id=f"{doc_id}:demo",
                sha256=next(
                    item["sha256"] for item in processed if item["document_id"] == str(doc_id)
                )
                if False
                else "0" * 64,
                excerpt=next(item["filename"] for item in processed if item["document_id"] == str(doc_id)),
            )
            for doc_id in document_ids[:3]
        ]
        # Citation hashes above are intentionally placeholders for the first RAG demonstration;
        # replace them with persisted document hashes before presenting the report.
        records = await DocumentRepository(session).get_many(document_ids)
        citations = [
            EvidenceCitation(
                document_id=doc_id,
                version=records[doc_id].version,
                chunk_id=f"{doc_id}:demo",
                sha256=records[doc_id].sha256,
                excerpt=next(item["content"] for item in dataset["documents"] if item["filename"] == records[doc_id].filename)[:600],
            )
            for doc_id in document_ids[:3]
        ]
        rag_finding = rag_service.answer(
            "What evidence is present in the synthetic industrial discharge application?",
            citations,
        )

        # 9-10: map evidence to the explicitly synthetic regulatory knowledge model and score risk.
        review_request = EnvironmentalReviewRequest(
            tenant_id=TENANT,
            case_id=CASE_ID,
            project_type=dataset["case"]["project_type"],
            location=dataset["case"]["location"],
            applicant=dataset["case"]["applicant"],
            documents=document_ids,
            attributes={"knowledge_status": "demo_only"},
        )
        review = engine.review(review_request, available_types, citations)

        # 11: route the case to a human queue and persist the assignment.
        assignment = assignment_engine.assign(CASE_ID, "technical-review", {"demo-analyst-01": 1})
        await CaseRepository(session).create_assignment(
            case_id=CASE_ID,
            tenant_id=TENANT,
            assignee=assignment.assignee,
            queue=assignment.queue,
            status=assignment.status.value,
            due_at=assignment.due_at,
            escalation_at=assignment.escalation_at,
        )

        # 12: record the human decision as an auditable event; the demo never auto-approves or rejects.
        decision = dataset["human_decision"]
        human_event = await audit_log.append(
            session,
            AuditEvent(
                tenant_id=TENANT,
                actor=decision["actor"],
                action="case.human_decision_recorded",
                resource_type="case",
                resource_id=str(CASE_ID),
                purpose="synthetic-demo",
                trace_id="phase14-human-decision",
                details={"decision": decision["decision"], "reason": decision["reason"]},
            ),
        )
        await session.commit()

        audit_events, _ = await audit_log.list_events_paginated(session, TENANT, 1, 200)

    report = {
        "dataset_id": dataset["dataset_id"],
        "authoritativeness": dataset["authoritativeness"],
        "verification_boundary": "synthetic offline execution; not production validation",
        "steps": {
            "documents_processed": len(processed),
            "missing_documents": review.missing_documents,
            "rag_grounded": rag_finding.grounded,
            "rag_citation_count": len(rag_finding.citations),
            "regulatory_knowledge_status": "demo_only",
            "risk_score": review.risk_score,
            "human_review_required": review.requires_human_review,
            "assigned_queue": assignment.queue,
            "human_decision": decision["decision"],
            "audit_event_count": len(audit_events),
            "human_decision_audit_event_hash": human_event.event_hash,
        },
        "document_processing": processed,
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    print(f"\nDemo evidence written to: {REPORT}")


if __name__ == "__main__":
    asyncio.run(main())
