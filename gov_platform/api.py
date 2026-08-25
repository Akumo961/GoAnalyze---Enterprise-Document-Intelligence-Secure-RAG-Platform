"""HTTP API boundary for the government case and document workflow."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from .api_auth import ApiIdentity, require_identity, require_role
from .audit import audit_log
from .config import get_settings
from .db.case_repository import CasePersistenceRepository
from .db.cases import CASE_STATES
from .db.document_repository import DocumentRepository
from .db.session import get_session
from .document_security import sanitize_filename, validate_content_type, validate_metadata, validate_object_uri, validate_sha256
from .models import AuditEvent, ClassificationLevel


class CaseCreateRequest(BaseModel):
    external_reference: str = Field(min_length=1, max_length=255)
    title: str = Field(min_length=1, max_length=1024)
    priority: str = Field(default="normal", min_length=1, max_length=32)
    attributes: dict = Field(default_factory=dict)


class CaseAssignmentRequest(BaseModel):
    queue: str = Field(min_length=1, max_length=255)
    assignee: str | None = Field(default=None, max_length=255)


class CaseTransitionRequest(BaseModel):
    target: str
    decision_reason: str | None = Field(default=None, max_length=8192)


class DocumentRegisterRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=1024)
    content_type: str = Field(min_length=1, max_length=255)
    classification: ClassificationLevel = ClassificationLevel.internal
    sha256: str = Field(min_length=64, max_length=64)
    object_uri: str = Field(min_length=1, max_length=2048)
    metadata: dict[str, object] = Field(default_factory=dict)


class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    external_reference: str
    title: str
    state: str
    priority: str
    assigned_queue: str | None
    assigned_to: str | None
    decision_officer: str | None
    decision_reason: str | None


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    case_id: UUID | None
    filename: str
    content_type: str
    classification: str
    sha256: str
    object_uri: str
    version: int
    lineage_id: UUID


def _response(case) -> CaseResponse:
    return CaseResponse.model_validate(case)


def _document_response(document) -> DocumentResponse:
    return DocumentResponse.model_validate(document)


router = APIRouter(prefix="/v1/cases", tags=["cases"])


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(request: CaseCreateRequest, identity: ApiIdentity = Depends(require_role("case_manager", "analyst", "administrator")), session: AsyncSession = Depends(get_session)) -> CaseResponse:
    case = await CasePersistenceRepository(session).create(tenant_id=identity.tenant_id, external_reference=request.external_reference, title=request.title, priority=request.priority, attributes=request.attributes)
    return _response(case)


@router.get("", response_model=list[CaseResponse])
async def list_cases(queue: str | None = None, state: str | None = None, identity: ApiIdentity = Depends(require_identity), session: AsyncSession = Depends(get_session)) -> list[CaseResponse]:
    states = {state} if state else None
    if state is not None and state not in CASE_STATES:
        raise HTTPException(status_code=400, detail="invalid_case_state")
    cases = await CasePersistenceRepository(session).list_queue(tenant_id=identity.tenant_id, queue=queue, states=states)
    return [_response(case) for case in cases]


@router.get("/{case_id}/documents", response_model=list[DocumentResponse])
async def list_case_documents(case_id: UUID, identity: ApiIdentity = Depends(require_identity), session: AsyncSession = Depends(get_session)) -> list[DocumentResponse]:
    case = await CasePersistenceRepository(session).get(tenant_id=identity.tenant_id, case_id=case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="case_not_found")
    documents = await DocumentRepository(session).list_for_case(tenant_id=identity.tenant_id, case_id=case_id)
    return [_document_response(document) for document in documents]


@router.post("/{case_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def register_document(case_id: UUID, request: DocumentRegisterRequest, identity: ApiIdentity = Depends(require_role("case_manager", "analyst", "administrator")), session: AsyncSession = Depends(get_session)) -> DocumentResponse:
    case = await CasePersistenceRepository(session).get(tenant_id=identity.tenant_id, case_id=case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="case_not_found")
    filename = sanitize_filename(request.filename)
    content_type = validate_content_type(request.content_type)
    sha256 = validate_sha256(request.sha256)
    object_uri = validate_object_uri(request.object_uri)
    metadata = validate_metadata(request.metadata)
    document = await DocumentRepository(session).create(tenant_id=identity.tenant_id, case_id=case_id, filename=filename, content_type=content_type, classification=request.classification.value, sha256=sha256, object_uri=object_uri, metadata=metadata)
    await audit_log.append(session, AuditEvent(tenant_id=identity.tenant_id, actor=identity.subject, action="document.registered", resource_type="document", resource_id=str(document.id), purpose="case_document_intake", trace_id=f"document-{document.id}", details={"case_id": str(case_id), "filename": filename, "content_type": content_type, "classification": request.classification.value, "sha256": sha256}))
    return _document_response(document)


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(case_id: UUID, identity: ApiIdentity = Depends(require_identity), session: AsyncSession = Depends(get_session)) -> CaseResponse:
    case = await CasePersistenceRepository(session).get(tenant_id=identity.tenant_id, case_id=case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="case_not_found")
    return _response(case)


@router.post("/{case_id}/assignment", response_model=CaseResponse)
async def assign_case(case_id: UUID, request: CaseAssignmentRequest, identity: ApiIdentity = Depends(require_role("case_manager", "administrator")), session: AsyncSession = Depends(get_session)) -> CaseResponse:
    try:
        case = await CasePersistenceRepository(session).assign(tenant_id=identity.tenant_id, case_id=case_id, queue=request.queue, assignee=request.assignee)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="case_not_found") from exc
    return _response(case)


@router.post("/{case_id}/transition", response_model=CaseResponse)
async def transition_case(case_id: UUID, request: CaseTransitionRequest, identity: ApiIdentity = Depends(require_role("decision_officer", "case_manager", "administrator")), session: AsyncSession = Depends(get_session)) -> CaseResponse:
    if request.target not in CASE_STATES:
        raise HTTPException(status_code=400, detail="invalid_case_state")
    try:
        case = await CasePersistenceRepository(session).transition(tenant_id=identity.tenant_id, case_id=case_id, target=request.target, actor=identity.subject, decision_reason=request.decision_reason)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="case_not_found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _response(case)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="GoAnalyze Government API", version="2.2.0", description="Decision-support API for secure environmental case and document workflows.", docs_url="/docs" if settings.environment != "production" else None, redoc_url=None if settings.environment == "production" else "/redoc")
    app.include_router(router)

    @app.get("/health/live", tags=["health"])
    async def liveness() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
