from gov_platform.phase1_demo import (
    assign_analyst,
    assess_priority,
    build_demo_case,
    completeness,
    grounded_question,
    map_regulatory_evidence,
    record_analyst_decision,
    run_phase1_demo,
)


def test_phase1_demo_is_reproducible_and_has_ten_documents() -> None:
    first = build_demo_case()
    second = build_demo_case()
    assert str(first.case_id) == "10000000-0000-4000-8000-000000000001"
    assert len(first.documents) == 10
    assert [(d.document_id, d.filename, d.checksum) for d in first.documents] == [
        (d.document_id, d.filename, d.checksum) for d in second.documents
    ]


def test_phase1_completeness_detects_missing_documents() -> None:
    case = build_demo_case()
    complete = completeness(case)
    assert complete["complete"] is True
    assert complete["missing"] == []

    case.documents = [d for d in case.documents if d.document_type != "site_plan"]
    incomplete = completeness(case)
    assert incomplete["complete"] is False
    assert incomplete["missing"] == ["site_plan"]


def test_phase1_grounded_question_carries_citations() -> None:
    case = build_demo_case()
    result = grounded_question(case, "What monitoring locations are described?")
    assert result["status"] == "grounded"
    assert result["evidence_type"] == "FACTUAL_EVIDENCE"
    assert result["citations"]
    assert any(citation["filename"] == "02_site_plan.pdf" for citation in result["citations"])
    assert all(citation["checksum"] for citation in result["citations"])


def test_phase1_rag_withholds_unsupported_question() -> None:
    case = build_demo_case()
    result = grounded_question(case, "What statutory penalty applies to this application?")
    assert result["status"] == "withheld"
    assert result["citations"] == []
    assert result["reason"] == "no_supporting_evidence"


def test_phase1_regulatory_mapping_is_explicitly_demo_authority() -> None:
    case = build_demo_case()
    mappings = map_regulatory_evidence(case)
    assert len(mappings) == 2
    assert all(item["source_authority"] == "demo" for item in mappings)
    assert all(0 <= item["coverage"] <= 1 for item in mappings)
    assert all(item["evidence"] for item in mappings)


def test_phase1_priority_and_human_review_boundary() -> None:
    case = build_demo_case()
    priority = assess_priority(case, completeness(case), map_regulatory_evidence(case))
    assert priority["human_decision_required"] is True
    assert priority["method"] == "synthetic demonstration heuristic"

    assignment = assign_analyst(case)
    assert assignment["assignee"] == "analyst.demo"
    assert assignment["status"] == "technical_review"

    decision = record_analyst_decision(case, "accept_for_further_review", "Continue technical assessment.")
    assert decision["human_decision"] is True
    assert any(event["action"] == "analyst.decision_recorded" for event in case.audit_events)


def test_phase1_full_demo_contains_metrics_governance_and_audit() -> None:
    result = run_phase1_demo()
    assert result["case"]["document_count"] == 10
    assert result["metrics"]["documents_processed"] == 10
    assert result["metrics"]["processing_time_ms"] >= 0
    assert 0 <= result["metrics"]["citation_coverage"] <= 1
    assert result["audit"]
    assert result["audit"][-1]["action"] == "demo.completed"
    assert result["governance"]["authority"] == "demo"
    assert result["governance"]["decision_support_only"] is True
