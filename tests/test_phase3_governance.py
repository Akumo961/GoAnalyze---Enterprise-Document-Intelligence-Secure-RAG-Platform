from datetime import UTC, date, datetime, timedelta

import pytest

from gov_platform.audit_chain import seal_event, verify_chain
from gov_platform.models import AuditEvent
from gov_platform.regulatory_knowledge import (
    KnowledgeType,
    RegulatoryObligation,
    RegulatorySource,
    obligations_for,
)
from gov_platform.retention import RetentionPolicy, deletion_due
from gov_platform.workflow import CaseState, ReviewCase, WorkflowRole, validate_transition_history


def test_regulatory_matching_is_jurisdiction_and_date_scoped() -> None:
    obligations = [
        RegulatoryObligation("o1", "s1", "Demo obligation", "Synthetic only", ("study",), "QC", date(2026, 1, 1)),
        RegulatoryObligation("o2", "s2", "Expired", "Synthetic only", ("study",), "QC", date(2025, 1, 1), date(2025, 12, 31)),
        RegulatoryObligation("o3", "s3", "Other jurisdiction", "Synthetic only", ("study",), "ON", date(2026, 1, 1)),
    ]
    assert [x.obligation_id for x in obligations_for(obligations, jurisdiction="QC", when=date(2026, 8, 25))] == ["o1"]


def test_source_schema_supports_unverified_demo_content() -> None:
    source = RegulatorySource("demo", "Synthetic source", KnowledgeType.guidance, "QC", "Demo", False, "demo://source")
    assert source.authoritative is False


def test_workflow_preserves_human_approval_boundary() -> None:
    case = ReviewCase("case-1", "tenant-a")
    case.transition("analyst", CaseState.admissibility, "Initial screening")
    case.transition("analyst", CaseState.technical_review, "Complete intake")
    case.transition("analyst", CaseState.legal_review, "Technical review complete")
    case.transition("analyst", CaseState.recommendation, "Recommendation prepared")
    with pytest.raises(ValueError, match="decision_officer_role_required"):
        case.transition("system", CaseState.approved, "Automated approval")
    case.transition(
        "delegated_officer",
        CaseState.approved,
        "Human decision",
        role=WorkflowRole.decision_officer,
    )
    assert validate_transition_history(case.transitions)


def test_workflow_rejects_illegal_transition() -> None:
    case = ReviewCase("case-2", "tenant-a")
    with pytest.raises(ValueError, match="decision_officer_role_required"):
        case.transition("analyst", CaseState.approved, "skip review")


def test_audit_chain_is_tamper_evident() -> None:
    first = AuditEvent(tenant_id="t1", actor="a", action="create", resource_type="case", resource_id="1", purpose="review", trace_id="x")
    second = AuditEvent(tenant_id="t1", actor="a", action="review", resource_type="case", resource_id="1", purpose="review", trace_id="x")
    sealed_first = seal_event(first, None)
    sealed_second = seal_event(second, sealed_first.event_hash)
    assert verify_chain([sealed_first, sealed_second])
    tampered = sealed_second.model_copy(update={"details": {"changed": True}})
    assert not verify_chain([sealed_first, tampered])


def test_retention_due_is_timezone_aware() -> None:
    policy = RetentionPolicy("demo", 30)
    created = datetime.now(UTC) - timedelta(days=31)
    assert deletion_due(created, policy)
    with pytest.raises(ValueError):
        deletion_due(datetime.now(), policy)
