from collections.abc import AsyncIterator
from uuid import UUID

import httpx
import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from gov_platform.api import app
from gov_platform.api_auth import ApiIdentity, require_identity
from gov_platform.db.case_repository import CasePersistenceRepository
from gov_platform.db.models import Base, DocumentORM
from gov_platform.db.session import get_session
from gov_platform.document_security import (
    sanitize_filename,
    validate_content_type,
    validate_object_uri,
    validate_sha256,
)


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as db:
        yield db
    await engine.dispose()


@pytest.mark.asyncio
async def test_document_registration_is_tenant_scoped_and_audited(session: AsyncSession) -> None:
    async def override_session() -> AsyncIterator[AsyncSession]:
        yield session

    async def override_identity() -> ApiIdentity:
        return ApiIdentity("analyst-1", "tenant-a", frozenset({"analyst"}))

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[require_identity] = override_identity
    try:
        case = await CasePersistenceRepository(session).create(
            tenant_id="tenant-a", external_reference="APP-7", title="Synthetic case"
        )
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/v1/cases/{case.id}/documents",
                json={
                    "filename": "../application.pdf",
                    "content_type": "application/pdf",
                    "sha256": "a" * 64,
                    "object_uri": "s3://gov-bucket/tenant-a/application.pdf",
                    "metadata": {"source": "synthetic"},
                },
            )
            assert response.status_code == 201
            body = response.json()
            assert body["filename"] == "application.pdf"
            document_id = UUID(body["id"])

            listed = await client.get(f"/v1/cases/{case.id}/documents")
            assert listed.status_code == 200
            assert listed.json()[0]["id"] == str(document_id)
    finally:
        app.dependency_overrides.clear()

    row = await session.get(DocumentORM, document_id)
    assert row is not None and row.tenant_id == "tenant-a"


@pytest.mark.asyncio
async def test_document_endpoint_cannot_cross_tenant_case(session: AsyncSession) -> None:
    async def override_session() -> AsyncIterator[AsyncSession]:
        yield session

    async def override_identity() -> ApiIdentity:
        return ApiIdentity("analyst-2", "tenant-b", frozenset({"analyst"}))

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[require_identity] = override_identity
    try:
        case = await CasePersistenceRepository(session).create(
            tenant_id="tenant-a", external_reference="APP-8", title="Private case"
        )
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/v1/cases/{case.id}/documents")
            assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_document_security_rejects_network_urls_and_unsafe_types() -> None:
    assert sanitize_filename(r"C:\uploads\permit.pdf") == "permit.pdf"
    assert validate_content_type("Application/PDF") == "application/pdf"
    assert validate_sha256("A" * 64) == "a" * 64
    with pytest.raises(HTTPException, match="invalid_object_uri"):
        validate_object_uri("https://example.com/private.pdf")
    with pytest.raises(HTTPException, match="invalid_object_uri"):
        validate_object_uri("s3://bucket/../secret.pdf")
    with pytest.raises(HTTPException, match="unsupported_content_type"):
        validate_content_type("application/x-msdownload")
