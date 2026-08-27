"""HTTP boundary for deterministic document metadata/classification analysis."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from .api_auth import ApiIdentity, require_role
from .db.document_repository import DocumentRepository
from .db.session import get_session
from .document_analysis import analyze_document
from .document_extract import ExtractedDocument

MAX_ANALYSIS_TEXT = 5_000_000

router = APIRouter(prefix="/v1/documents", tags=["document-analysis"])


class DocumentAnalysisRequest(BaseModel):
    extracted_text: str = Field(min_length=1, max_length=MAX_ANALYSIS_TEXT)
    extraction_method: str = Field(min_length=1, max_length=64)
    page_count: int | None = Field(default=None, ge=1, le=100_000)


class DocumentAnalysisResponse(BaseModel):
    document_id: UUID
    classification: str
    confidence: float
    matched_terms: tuple[str, ...]
    metadata: dict[str, object]
    review_required: bool


@router.post("/{document_id}/analysis", response_model=DocumentAnalysisResponse)
async def analyze_document_endpoint(
    document_id: UUID,
    request: DocumentAnalysisRequest,
    identity: ApiIdentity = Depends(require_role("analyst", "case_manager", "administrator")),
    session: AsyncSession = Depends(get_session),
) -> DocumentAnalysisResponse:
    repository = DocumentRepository(session)
    document = await repository.get(tenant_id=identity.tenant_id, document_id=document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="document_not_found")
    extracted = ExtractedDocument(
        sha256=document.sha256,
        text=request.extracted_text,
        method=request.extraction_method,
        page_count=request.page_count,
    )
    result = analyze_document(extracted)
    saved = await repository.save_analysis(
        tenant_id=identity.tenant_id,
        document_id=document_id,
        classification=result.classification.label,
        metadata=result.to_metadata(),
    )
    if saved is None:
        raise HTTPException(status_code=404, detail="document_not_found")
    return DocumentAnalysisResponse(
        document_id=document_id,
        classification=result.classification.label,
        confidence=result.classification.confidence,
        matched_terms=result.classification.matched_terms,
        metadata=result.to_metadata(),
        review_required=result.classification.review_required,
    )
