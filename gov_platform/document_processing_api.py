"""HTTP endpoint for secure processing of registered document bytes."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from .api_auth import ApiIdentity, require_role
from .db.document_repository import DocumentRepository
from .db.session import get_session
from .document_processing import MalwareScanner, RejectingScanner, process_document

router = APIRouter(prefix="/v1/documents", tags=["document-processing"])


class DocumentProcessingResponse(BaseModel):
    document_id: UUID
    sha256: str
    bytes_processed: int
    extraction_method: str
    page_count: int | None
    text: str
    scanner: str


def get_malware_scanner() -> MalwareScanner:
    """Return the deployment scanner adapter.

    Production deployments must override this dependency with a configured
    scanner such as ClamAV. The rejecting default intentionally fails closed.
    """
    return RejectingScanner()


@router.put("/{document_id}/content", response_model=DocumentProcessingResponse)
async def process_registered_document(
    document_id: UUID,
    request: Request,
    identity: ApiIdentity = Depends(require_role("case_manager", "analyst", "administrator")),
    session: AsyncSession = Depends(get_session),
    scanner: MalwareScanner = Depends(get_malware_scanner),
) -> DocumentProcessingResponse:
    document = await DocumentRepository(session).get(
        tenant_id=identity.tenant_id, document_id=document_id
    )
    if document is None:
        raise HTTPException(status_code=404, detail="document_not_found")

    data = await request.body()
    try:
        result = process_document(
            data,
            content_type=document.content_type,
            expected_sha256=document.sha256,
            scanner=scanner,
        )
    except ValueError as exc:
        detail = str(exc)
        code = status.HTTP_422_UNPROCESSABLE_ENTITY
        if detail == "malware_detected_or_scan_failed":
            code = status.HTTP_422_UNPROCESSABLE_ENTITY
        raise HTTPException(status_code=code, detail=detail) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc

    return DocumentProcessingResponse(
        document_id=document.id,
        sha256=result.sha256,
        bytes_processed=result.bytes_processed,
        extraction_method=result.extraction.method,
        page_count=result.extraction.page_count,
        text=result.extraction.text,
        scanner=scanner.__class__.__name__,
    )
