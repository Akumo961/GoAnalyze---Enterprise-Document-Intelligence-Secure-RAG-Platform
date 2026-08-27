from collections.abc import AsyncIterator
from uuid import UUID

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from gov_platform.api import app
from gov_platform.api_auth import ApiIdentity, require_identity
from gov_platform.db.cases import CaseORM
from gov_platform.db.models import Base
from gov_platform.db.session import get_session


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
async def test_http_case_workflow_is_tenant_scoped(session: AsyncSession) -> None:
    async def override_session() -> AsyncIterator[AsyncSession]:
        yield session

    async def override_identity() -> ApiIdentity:
        return ApiIdentity("analyst-1", "tenant-a", frozenset({"case_manager", "analyst"}))

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[require_identity] = override_identity
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/v1/cases",
                json={"external_reference": "APP-100", "title": "Synthetic environmental case"},
            )
            assert response.status_code == 201
            case_id = response.json()["id"]
            assert UUID(case_id)

            fetched = await client.get(f"/v1/cases/{case_id}")
            assert fetched.status_code == 200
            assert fetched.json()["external_reference"] == "APP-100"
    finally:
        app.dependency_overrides.clear()

    # Verify persistence exists only in the authenticated tenant.
    row = await session.get(CaseORM, UUID(case_id))
    assert row is not None and row.tenant_id == "tenant-a"


@pytest.mark.asyncio
async def test_http_auth_dependency_is_not_bypassed_without_identity() -> None:
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as error:
        await require_identity()
    assert error.value.status_code == 401
