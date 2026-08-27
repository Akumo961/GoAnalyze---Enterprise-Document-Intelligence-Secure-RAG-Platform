from collections.abc import AsyncIterator
from hashlib import sha256
from uuid import uuid4

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from gov_platform.api import app
from gov_platform.api_auth import ApiIdentity, require_identity
from gov_platform.db.document_repository import DocumentRepository
from gov_platform.db.models import Base
from gov_platform.db.session import get_session
from gov_platform.document_processing import process_document
from gov_platform.document_processing_api import get_malware_scanner


class CleanScanner:
    def __init__(self) -> None:
        self.calls = 0

    def scan(self, data: bytes) -> None:
        self.calls += 1


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as db:
        yield db
    await engine.dispose()


def test_process_document_verifies_hash_before_extraction() -> None:
    data = b"environmental permit evidence"
    scanner = CleanScanner()
    result = process_document(
        data,
        content_type="text/plain",
        expected_sha256=sha256(data).hexdigest(),
        scanner=scanner,
    )
    assert result.sha256 == sha256(data).hexdigest()
    assert result.bytes_processed == len(data)
    assert result.extraction.text == data.decode()
    assert scanner.calls == 1


def test_process_document_rejects_hash_mismatch_before_scanning() -> None:
    scanner = CleanScanner()
    with pytest.raises(ValueError, match="content_hash_mismatch"):
        process_document(
            b"evidence",
            content_type="text/plain",
            expected_sha256="0" * 64,
            scanner=scanner,
        )
    assert scanner.calls == 0


@pytest.mark.asyncio
async def test_http_processing_is_tenant_scoped_and_scanned(session: AsyncSession) -> None:
    identity = ApiIdentity("analyst-1", "tenant-a", frozenset({"analyst"}))
    data = b"synthetic environmental evidence"
    document = await DocumentRepository(session).create(
        tenant_id="tenant-a",
        case_id=uuid4(),
        filename="evidence.txt",
        content_type="text/plain",
        classification="internal",
        sha256=sha256(data).hexdigest(),
        object_uri="s3://goanalyze-documents/tenant-a/evidence.txt",
        metadata={},
    )
    scanner = CleanScanner()

    async def override_session() -> AsyncIterator[AsyncSession]:
        yield session

    async def override_identity() -> ApiIdentity:
        return identity

    def override_scanner() -> CleanScanner:
        return scanner

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[require_identity] = override_identity
    app.dependency_overrides[get_malware_scanner] = override_scanner
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.put(
                f"/v1/documents/{document.id}/content",
                content=data,
                headers={"content-type": "text/plain"},
            )
        assert response.status_code == 200
        payload = response.json()
        assert payload["sha256"] == sha256(data).hexdigest()
        assert payload["text"] == data.decode()
        assert scanner.calls == 1
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_http_processing_cannot_cross_tenant(session: AsyncSession) -> None:
    data = b"secret evidence"
    document = await DocumentRepository(session).create(
        tenant_id="tenant-a",
        case_id=uuid4(),
        filename="secret.txt",
        content_type="text/plain",
        classification="internal",
        sha256=sha256(data).hexdigest(),
        object_uri="s3://goanalyze-documents/tenant-a/secret.txt",
        metadata={},
    )

    async def override_session() -> AsyncIterator[AsyncSession]:
        yield session

    async def override_identity() -> ApiIdentity:
        return ApiIdentity("analyst-b", "tenant-b", frozenset({"analyst"}))

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[require_identity] = override_identity
    app.dependency_overrides[get_malware_scanner] = lambda: CleanScanner()
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.put(f"/v1/documents/{document.id}/content", content=data)
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
