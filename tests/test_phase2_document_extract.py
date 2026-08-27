import pytest

from gov_platform.document_extract import extract_text, validate_upload


def test_text_extraction_preserves_sha256():
    data = b"Environmental application\nDischarge monitoring results"
    result = extract_text(data, "text/plain")
    assert result.method == "text"
    assert "Discharge monitoring" in result.text
    assert len(result.sha256) == 64


def test_upload_size_and_type_limits():
    with pytest.raises(ValueError, match="unsupported_content_type"):
        validate_upload(b"data", "application/x-executable")


def test_empty_upload_rejected():
    with pytest.raises(ValueError, match="empty_document"):
        validate_upload(b"", "text/plain")
