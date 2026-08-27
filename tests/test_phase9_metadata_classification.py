from gov_platform.document_classification import classify_document
from gov_platform.document_extract import ExtractedDocument
from gov_platform.document_metadata import extract_metadata


def test_metadata_extraction_is_deterministic_and_bounded() -> None:
    document = ExtractedDocument(
        sha256="a" * 64,
        text="Environmental Impact Assessment\nThe project is submitted for authorization.",
        method="pdf-text",
        page_count=4,
    )
    result = extract_metadata(document)
    assert result.title == "Environmental Impact Assessment"
    assert result.page_count == 4
    assert result.language == "en"
    assert result.word_count == 10
    assert result.extraction_method == "pdf-text"


def test_unknown_language_is_not_guessed() -> None:
    document = ExtractedDocument("b" * 64, "12345 !!!", "text", None)
    assert extract_metadata(document).language == "und"


def test_classification_is_explainable_and_requires_review() -> None:
    result = classify_document("Inspection record: inspector finding and violation.")
    assert result.label == "inspection_record"
    assert result.matched_terms == ("inspection", "inspector", "finding", "violation")
    assert result.confidence <= 0.95
    assert result.review_required is True


def test_classification_does_not_invent_a_label() -> None:
    result = classify_document("A document containing unrelated material only.")
    assert result.label == "unclassified"
    assert result.confidence == 0.0
    assert result.matched_terms == ()
