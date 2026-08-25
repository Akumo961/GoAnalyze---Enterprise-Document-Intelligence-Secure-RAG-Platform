"""Deterministic synthetic pilot workflow for Phase 1.

This is a demo/evaluation harness, not an authoritative regulatory engine.
It uses synthetic evidence and explicitly labels all regulatory knowledge as
DEMO. The workflow preserves human accountability: no legal decision is made
by the system.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
from uuid import UUID, uuid5

from .regulatory_knowledge import RegulatoryObligation, RegulatorySource, SourceAuthority

DEMO_NAMESPACE = UUID("10000000-0000-4000-8000-000000000010")


@dataclass(frozen=True)
class DemoDocument:
    document_id: UUID
    filename: str
    document_type: str
    text: str
    page_count: int = 1

    @property
    def checksum(self) -> str:
        return sha256(self.text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class DemoCitation:
    document_id: UUID
    filename: str
    page: int
    excerpt: str
    checksum: str


@dataclass(frozen=True)
class DemoFinding:
    category: str
    statement: str
    evidence: tuple[DemoCitation, ...]
    confidence: float
    uncertainty: str


@dataclass
class DemoCase:
    case_id: UUID
    tenant_id: str
    project_name: str
    applicant: str
    project_type: str
    documents: list[DemoDocument]
    findings: list[DemoFinding] = field(default_factory=list)
    assigned_to: str | None = None
    analyst_decision: str | None = None
    analyst_note: str | None = None
    audit_events: list[dict[str, object]] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def audit(self, action: str, actor: str, details: dict[str, object] | None = None) -> None:
        self.audit_events.append({
            "timestamp": datetime.now(UTC).isoformat(),
            "actor": actor,
            "action": action,
            "details": details or {},
        })


DEMO_SOURCE = RegulatorySource(
    source_id="demo-qc-environmental-source-v1",
    title="Synthetic Québec environmental review source",
    authority=SourceAuthority.demo,
    jurisdiction="Québec",
    publisher="GoAnalyze synthetic demonstration dataset",
    version="1.0",
)

DEMO_OBLIGATIONS = (
    RegulatoryObligation(
        obligation_id="DEMO-ENV-001",
        source_id=DEMO_SOURCE.source_id,
        title="Synthetic submission evidence requirement",
        description="Demo-only obligation used to demonstrate evidence mapping.",
        evidence_requirements=("application_form", "site_plan", "impact_assessment"),
        jurisdiction="Québec",
        verified=True,
    ),
    RegulatoryObligation(
        obligation_id="DEMO-ENV-002",
        source_id=DEMO_SOURCE.source_id,
        title="Synthetic mitigation evidence requirement",
        description="Demo-only mitigation evidence requirement.",
        evidence_requirements=("mitigation_plan",),
        jurisdiction="Québec",
        verified=True,
    ),
)


def _doc(filename: str, document_type: str, text: str, pages: int = 1) -> DemoDocument:
    return DemoDocument(uuid5(DEMO_NAMESPACE, filename), filename, document_type, text, pages)


def build_demo_case() -> DemoCase:
    """Return the reproducible synthetic case used by the Phase 1 demo."""
    docs = [
        _doc("01_application_form.pdf", "application_form", "Synthetic application for North River Industrial Facility. Applicant: Demo Industries. Project: industrial discharge. Location: Synthetic Region.", 3),
        _doc("02_site_plan.pdf", "site_plan", "Synthetic site plan. Discharge point D-01 and monitoring location M-01 are shown.", 2),
        _doc("03_effluent_characterization.pdf", "effluent_characterization", "Synthetic effluent characterization. Flow 120 m3/day. Parameters are demonstration values only.", 8),
        _doc("04_mitigation_plan.pdf", "mitigation_plan", "Synthetic mitigation plan describing containment, monitoring and response procedures.", 12),
        _doc("05_public_consultation_record.pdf", "public_consultation_record", "Synthetic public consultation record containing demonstration questions and responses.", 5),
        _doc("06_impact_assessment.pdf", "impact_assessment", "Synthetic impact assessment. Potential effects and proposed mitigation are demonstration content only.", 24),
        _doc("07_monitoring_plan.pdf", "monitoring_plan", "Synthetic monitoring plan with sampling frequency and reporting fields.", 6),
        _doc("08_technical_memo.pdf", "technical_memo", "Synthetic technical memorandum. Cross-reference to D-01 and M-01.", 4),
        _doc("09_communications.pdf", "correspondence", "Synthetic correspondence regarding requested application information.", 3),
        _doc("10_appendix.pdf", "appendix", "Synthetic supporting appendix with demonstration calculations.", 7),
    ]
    case = DemoCase(
        case_id=UUID("10000000-0000-4000-8000-000000000001"),
        tenant_id="demo-ministry",
        project_name="North River Synthetic Industrial Facility",
        applicant="Demo Industries Inc.",
        project_type="industrial_discharge",
        documents=docs,
    )
    case.audit("case.created", "demo-system", {"document_count": len(docs)})
    return case


def classify_documents(case: DemoCase) -> None:
    case.audit("documents.classified", "demo-system", {"count": len(case.documents)})


def completeness(case: DemoCase) -> dict[str, object]:
    required = {"application_form", "site_plan", "effluent_characterization", "mitigation_plan", "public_consultation_record"}
    present = {d.document_type for d in case.documents}
    missing = sorted(required - present)
    result: dict[str, object] = {"required": sorted(required), "present": sorted(present), "missing": missing, "complete": not missing}
    case.audit("case.completeness_checked", "demo-system", result)
    return result


def _citation(document: DemoDocument, excerpt: str) -> DemoCitation:
    return DemoCitation(document.document_id, document.filename, 1, excerpt[:600], document.checksum)


def grounded_question(case: DemoCase, question: str) -> dict[str, object]:
    """Answer only from synthetic document text; unsupported questions are withheld."""
    terms = question.lower().split()
    hits: list[DemoCitation] = []
    for document in case.documents:
        lowered = document.text.lower()
        if any(term in lowered for term in terms if len(term) > 3):
            hits.append(_citation(document, document.text))
    hits = hits[:5]
    if not hits:
        result: dict[str, object] = {"status": "withheld", "answer": None, "citations": [], "reason": "no_supporting_evidence"}
    else:
        result = {
            "status": "grounded",
            "answer": f"The synthetic case contains evidence related to: {question}.",
            "citations": [c.__dict__ for c in hits],
            "evidence_type": "FACTUAL_EVIDENCE",
            "uncertainty": "Synthetic demonstration evidence; not authoritative regulatory advice.",
        }
    case.audit("ai.question_answered", "demo-system", {"status": result["status"], "citation_count": len(hits)})
    return result


def map_regulatory_evidence(case: DemoCase) -> list[dict[str, object]]:
    by_type = {d.document_type: d for d in case.documents}
    mappings: list[dict[str, object]] = []
    for obligation in DEMO_OBLIGATIONS:
        evidence: list[DemoCitation] = []
        for required_type in obligation.evidence_requirements:
            document = by_type.get(required_type)
            if document:
                evidence.append(_citation(document, document.text))
        mappings.append({
            "obligation_id": obligation.obligation_id,
            "title": obligation.title,
            "source_authority": DEMO_SOURCE.authority.value,
            "evidence": [e.__dict__ for e in evidence],
            "coverage": len(evidence) / max(1, len(obligation.evidence_requirements)),
        })
    case.audit("regulatory.evidence_mapped", "demo-system", {"mapping_count": len(mappings)})
    return mappings


def assess_priority(case: DemoCase, completeness_result: dict[str, object], mappings: list[dict[str, object]]) -> dict[str, object]:
    missing = len(completeness_result["missing"]) if isinstance(completeness_result["missing"], list) else 0
    coverage = sum(float(m["coverage"]) for m in mappings) / max(1, len(mappings))
    score = round(min(100.0, 25.0 + missing * 15.0 + (1.0 - coverage) * 30.0), 2)
    level = "high" if score >= 70 else "medium" if score >= 40 else "low"
    result: dict[str, object] = {"score": score, "priority": level, "method": "synthetic demonstration heuristic", "human_decision_required": True}
    case.audit("case.priority_assessed", "demo-system", result)
    return result


def assign_analyst(case: DemoCase, analyst: str = "analyst.demo") -> dict[str, object]:
    case.assigned_to = analyst
    result: dict[str, object] = {"assignee": analyst, "queue": "environmental-technical-review", "status": "technical_review"}
    case.audit("case.assigned", analyst, result)
    return result


def record_analyst_decision(case: DemoCase, decision: str, note: str, analyst: str = "analyst.demo") -> dict[str, object]:
    allowed = {"accept_for_further_review", "request_information", "escalate"}
    if decision not in allowed:
        raise ValueError("invalid_demo_decision")
    if not note.strip():
        raise ValueError("analyst_note_required")
    case.analyst_decision = decision
    case.analyst_note = note.strip()
    result: dict[str, object] = {"decision": decision, "note": case.analyst_note, "human_decision": True, "actor": analyst}
    case.audit("analyst.decision_recorded", analyst, result)
    return result


def run_phase1_demo() -> dict[str, object]:
    case = build_demo_case()
    classify_documents(case)
    complete = completeness(case)
    answer = grounded_question(case, "What monitoring locations are described?")
    mappings = map_regulatory_evidence(case)
    priority = assess_priority(case, complete, mappings)
    assignment = assign_analyst(case)
    decision = record_analyst_decision(case, "accept_for_further_review", "Synthetic analyst review completed; continue technical assessment.")
    elapsed_ms = round((datetime.now(UTC) - case.started_at).total_seconds() * 1000, 2)
    case.audit("demo.completed", "demo-system", {"elapsed_ms": elapsed_ms})
    return {
        "case": {"case_id": str(case.case_id), "project_name": case.project_name, "applicant": case.applicant, "document_count": len(case.documents)},
        "completeness": complete,
        "ai": answer,
        "regulatory_mappings": mappings,
        "priority": priority,
        "assignment": assignment,
        "decision": decision,
        "audit": case.audit_events,
        "metrics": {"documents_processed": len(case.documents), "processing_time_ms": elapsed_ms, "citation_coverage": len(answer["citations"]) / 5.0 if isinstance(answer["citations"], list) else 0.0},
        "governance": {"regulatory_source": DEMO_SOURCE.source_id, "authority": DEMO_SOURCE.authority.value, "decision_support_only": True},
    }
