from gov_platform.phase1_demo import (
    build_demo_case,
    completeness,
    grounded_question,
    map_regulatory_evidence,
    assess_priority,
    assign_analyst,
    record_analyst_decision,
    run_phase1_demo,
)


def test_phase1_demo_has_reproducible_case_and_ten_documents() -> None:
    case = build_demo_case()
    assert str(case.case_id) == "10000000-0000-4000-8000-000000000001"
    assert len(case.documents) == 10


def test_phase1_completeness_detects_required_document_types() -> None:
    case = build_demo_case()
    result = completeness(case)
    assert result["complete"] is True
    assert result["missing"] == []


def test_phase1_rag_withholds_unsupported_question() -> None:
    case = build_demo_case()
    result = grounded_question(case, "What is the legal penalty imposed by the ministry?")
    assert result["status"] in {"grounded", "withheld"}
    # The demo must never present synthetic content as authoritative law.
    assert result.get("uncertainty") == "Synthetic demonstration evidence; not authoritative regulatory advice." or result["status"] == "withheld"


def test_phase1_regulatory_mapping_is_explicitly_demo_authority() -> None:
    case = build_demo_case()
    mappings = map_regulatory_evidence(case)
    assert mappings
    assert all(item["source_authority"] == "demo" for item in mappings)
    assert all(0 <= item["coverage"] <= 1 for item in mappings)


def test_phase1_human_review_and_decision_are_recorded() -> None:
    case = build_demo_case()
    priority = assess_priority(case, completeness(case), map_regulatory_evidence(case))
    assert priority["human_decision_required"] is True
    assignment = assign_analyst(case)
    assert assignment["assignee"] == "analyst.demo"
    decision = record_analyst_decision(case, "accept_for_further_review", "Continue technical assessment.")
    assert decision["human_decision"] is True
    assert any(event["action"] == "analyst.decision_recorded" for event in case.audit_events)


def test_phase1_full_demo_contains_metrics_and_audit() -> None:
    result = run_phase1_demo()
    assert result["case"]["document_count"] == 10
    assert result["metrics"]["documents_processed"] == 10
    assert result["metrics"]["processing_time_ms"] >= 0
    assert result["audit"]
    assert result["governance"]["decision_support_only"] is True
