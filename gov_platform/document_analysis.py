"""Deterministic document analysis orchestration.

Combines metadata extraction and explainable classification without granting
the classifier authority over a case decision.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

from .document_classification import ClassificationResult, classify_document
from .document_extract import ExtractedDocument
from .document_metadata import DocumentMetadata, extract_metadata


@dataclass(frozen=True)
class DocumentAnalysisResult:
    metadata: DocumentMetadata
    classification: ClassificationResult

    def to_metadata(self) -> dict[str, object]:
        return {
            "analysis_version": "1",
            "metadata": asdict(self.metadata),
            "classification": asdict(self.classification),
        }


def analyze_document(document: ExtractedDocument) -> DocumentAnalysisResult:
    metadata = extract_metadata(document)
    classification = classify_document(document.text)
    return DocumentAnalysisResult(metadata=metadata, classification=classification)
