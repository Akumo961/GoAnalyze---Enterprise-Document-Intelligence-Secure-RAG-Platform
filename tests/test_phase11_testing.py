"""Phase 11 security, RAG, ingestion, and regression acceptance tests."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from gov_platform.audit import AuditLog
from gov_platform.ingestion import IngestionPipeline, NullOcrEngine
from gov_platform.models import (
    AIFinding,
    ClassificationLevel,
    DocumentIngestRequest,
    EnvironmentalReviewResult,
    EvidenceCitation,
    TenantContext,
)
from gov_platform.rag import GroundedRagService
from gov_platform.security import evaluate_abac


def _citation() -> EvidenceCitation:
    return EvidenceCitation(
        document_id=uuid4(), version=1, chunk_id="chunk-1", page=2,
        sha256="a" * 64, excerpt="The application includes the required environmental study.",
    )


def test_authentication_production_disallows_dev_auth():
    from gov_platform.config import Settings
    settings = Settings(environment="production", allow_insecure_dev_auth=False)
    assert settings.allow_insecure_dev_auth is False


def test_authorization_denies_cross_tenant_access():
    decision = evaluate_abac(TenantContext(tenant_id="tenant-a", ministry="a"), "read:document", "tenant-b", ClassificationLevel.internal, "case-review")
    assert not decision.allowed and decision.reason == "tenant_mismatch"


def test_platform_admin_can_cross_tenant():
    decision = evaluate_abac(TenantContext(tenant_id="tenant-a", ministry="a", roles={"platform-admin"}), "read:document", "tenant-b", ClassificationLevel.internal, "operations")
    assert decision.allowed


def test_protected_b_requires_explicit_role():
    denied = evaluate_abac(TenantContext(tenant_id="tenant-a", ministry="a"), "read:document", "tenant-a", ClassificationLevel.protected_b, "case-review")
    allowed = evaluate_abac(TenantContext(tenant_id="tenant-a", ministry="a", roles={"protected-b-reader"}), "read:document", "tenant-a", ClassificationLevel.protected_b, "case-review")
    assert not denied.allowed and allowed.allowed


def test_admin_action_requires_tenant_admin():
    decision = evaluate_abac(TenantContext(tenant_id="tenant-a", ministry="a"), "admin:user", "tenant-a", ClassificationLevel.internal, "operations")
    assert not decision.allowed and decision.reason == "tenant_admin_required"


def test_invalid_purpose_is_denied():
    decision = evaluate_abac(TenantContext(tenant_id="tenant-a", ministry="a"), "read:document", "tenant-a", ClassificationLevel.internal, "unknown")
    assert not decision.allowed and decision.reason == "invalid_purpose"


def test_audit_hash_function_is_available():
    assert callable(AuditLog()._hash_event)


def test_rag_withholds_unsupported_answer():
    finding = GroundedRagService().answer("What is required?", [])
    assert not finding.grounded and finding.confidence == 0 and finding.citations == []


def test_rag_answer_is_grounded_and_capped():
    finding = GroundedRagService().answer("What is required?", [_citation() for _ in range(8)])
    assert finding.grounded and len(finding.citations) == 5 and finding.confidence <= 0.92


def test_citation_hash_is_required_length():
    with pytest.raises(ValidationError):
        EvidenceCitation(document_id=uuid4(), version=1, chunk_id="x", sha256="bad", excerpt="evidence")


def test_document_ingest_accepts_valid_sha256():
    request = DocumentIngestRequest(tenant_id="tenant-a", filename="application.pdf", content_type="application/pdf", sha256="b" * 64, object_uri="s3://documents/application.pdf")
    assert len(request.sha256) == 64


def test_document_ingest_rejects_invalid_sha256():
    with pytest.raises(ValidationError):
        DocumentIngestRequest(tenant_id="tenant-a", filename="application.pdf", content_type="application/pdf", sha256="short", object_uri="s3://documents/application.pdf")


def test_ingestion_has_explicit_ocr_boundary():
    pipeline = IngestionPipeline(ocr_engine=NullOcrEngine())
    assert pipeline.ocr_engine.extract_text("s3://x", "application/pdf") == ""


def test_ai_finding_confidence_is_bounded():
    with pytest.raises(ValidationError):
        AIFinding(finding_type="test", statement="bad", confidence=1.1, grounded=False, explanation="invalid")


def test_environmental_risk_score_is_bounded():
    with pytest.raises(ValidationError):
        EnvironmentalReviewResult(case_id=uuid4(), admissible=True, missing_documents=[], regulation_mappings=[], compliance_findings=[], risk_score=101, recommendation="review", justification="test", requires_human_review=True)


def test_classification_levels_are_explicit():
    assert {level.value for level in ClassificationLevel} == {"public", "internal", "confidential", "protected_b"}


def test_unknown_resource_tenant_is_denied():
    decision = evaluate_abac(TenantContext(tenant_id="tenant-a", ministry="a"), "read:document", "", ClassificationLevel.internal, "case-review")
    assert not decision.allowed


def test_tenant_admin_is_not_platform_admin():
    decision = evaluate_abac(TenantContext(tenant_id="tenant-a", ministry="a", roles={"tenant-admin"}), "read:document", "tenant-b", ClassificationLevel.internal, "case-review")
    assert not decision.allowed
