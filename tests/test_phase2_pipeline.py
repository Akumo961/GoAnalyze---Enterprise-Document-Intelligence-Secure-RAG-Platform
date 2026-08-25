from uuid import uuid4

from gov_platform.phase2_pipeline import Phase2Pipeline


def test_ingest_extracts_and_indexes_for_tenant():
    pipeline = Phase2Pipeline()
    result = pipeline.ingest("tenant-a", uuid4(), b"Effluent monitoring results\nMonthly discharge data", "text/plain")
    assert result.extraction.text.startswith("Effluent monitoring")
    assert result.indexed_chunks == 1
    answer = pipeline.answer("tenant-a", "What are the discharge results?")
    assert answer.grounded is True
    assert answer.citations


def test_tenant_isolation_is_enforced_by_index():
    pipeline = Phase2Pipeline()
    pipeline.ingest("tenant-a", uuid4(), b"Secret tenant A discharge information", "text/plain")
    answer = pipeline.answer("tenant-b", "What is the discharge information?")
    assert answer.grounded is False
    assert not answer.citations
