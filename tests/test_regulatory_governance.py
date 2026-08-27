from datetime import date
from uuid import uuid4

from gov_platform.environmental_engine import EnvironmentalAuthorizationEngine
from gov_platform.models import EnvironmentalReviewRequest
from gov_platform.regulatory import (
    KnowledgeStatus,
    RegulatoryKnowledgeBase,
    RegulatoryObligation,
    RegulatorySource,
)


def _request(jurisdiction: str) -> EnvironmentalReviewRequest:
    return EnvironmentalReviewRequest(
        tenant_id="tenant-a",
        case_id=uuid4(),
        project_type="industrial_discharge",
        location="synthetic",
        applicant="Synthetic Applicant",
        documents=[],
        attributes={"jurisdiction": jurisdiction},
    )


def test_regulatory_mapping_is_not_invented_without_verified_pack() -> None:
    result = EnvironmentalAuthorizationEngine().review(_request("QC"), set(), [])
    assert result.regulation_mappings[0].finding_type == "regulatory_knowledge_unavailable"
    assert result.regulation_mappings[0].grounded is False


def test_demo_knowledge_is_not_treated_as_authoritative() -> None:
    kb = RegulatoryKnowledgeBase(
        sources=[
            RegulatorySource(
                source_id="demo",
                title="Synthetic",
                publisher="GoAnalyze",
                jurisdiction="QC-DEMO",
                canonical_uri="https://example.invalid/demo",
                retrieved_on=date(2026, 8, 27),
                status=KnowledgeStatus.demo,
            )
        ],
        obligations=[
            RegulatoryObligation(
                obligation_id="DEMO-1",
                title="Synthetic obligation",
                description="Demo only",
                source_id="demo",
                applicable_jurisdictions=("QC-DEMO",),
                evidence_types=("application_form",),
                status=KnowledgeStatus.demo,
            )
        ],
    )
    result = EnvironmentalAuthorizationEngine(kb).review(_request("QC-DEMO"), set(), [])
    assert result.regulation_mappings[0].finding_type == "regulatory_knowledge_unavailable"


def test_verified_knowledge_can_be_mapped_with_provenance() -> None:
    kb = RegulatoryKnowledgeBase(
        sources=[
            RegulatorySource(
                source_id="verified-1",
                title="Authoritative source",
                publisher="Authorized source owner",
                jurisdiction="QC",
                canonical_uri="https://authority.example/record/1",
                retrieved_on=date(2026, 8, 27),
                status=KnowledgeStatus.verified,
                checksum="abc123",
            )
        ],
        obligations=[
            RegulatoryObligation(
                obligation_id="REQ-1",
                title="Verified evidence requirement",
                description="Only a synthetic test of provenance handling.",
                source_id="verified-1",
                applicable_jurisdictions=("QC",),
                evidence_types=("application_form",),
                status=KnowledgeStatus.verified,
            )
        ],
    )
    result = EnvironmentalAuthorizationEngine(kb).review(_request("QC"), {"application_form"}, [])
    assert result.regulation_mappings[0].finding_type == "regulatory_obligation"
    assert result.regulation_mappings[0].confidence == 1.0
