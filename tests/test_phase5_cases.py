from collections.abc import AsyncIterator
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from gov_platform.db.cases import CaseORM, validate_decision, validate_transition
from gov_platform.db.case_repository import CasePersistenceRepository
from gov_platform.db.models import Base


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
async def test_case_repository_is_tenant_scoped(session: AsyncSession) -> None:
    repo = CasePersistenceRepository(session)
    case = await repo.create(tenant_id="ministry-a", external_reference="APP-001", title="Synthetic application")
    assert await repo.get(tenant_id="ministry-b", case_id=case.id) is None
    assert (await repo.get(tenant_id="ministry-a", case_id=case.id)).id == case.id


@pytest.mark.asyncio
async def test_case_transition_requires_human_decision_officer_and_reason(session: AsyncSession) -> None:
    repo = CasePersistenceRepository(session)
    case = await repo.create(tenant_id="t1", external_reference="APP-002", title="Review case")
    await repo.transition(tenant_id="t1", case_id=case.id, target="analysis", actor="analyst-1")
    await repo.transition(tenant_id="t1", case_id=case.id, target="review", actor="analyst-1")
    with pytest.raises(ValueError, match="decision_reason_required"):
        await repo.transition(tenant_id="t1", case_id=case.id, target="approved", actor="officer-1")
    approved = await repo.transition(
        tenant_id="t1", case_id=case.id, target="approved", actor="officer-1", decision_reason="Human review completed."
    )
    assert approved.decision_officer == "officer-1"
    assert approved.decision_reason == "Human review completed."


@pytest.mark.asyncio
async def test_queue_listing_is_tenant_and_state_scoped(session: AsyncSession) -> None:
    repo = CasePersistenceRepository(session)
    first = await repo.create(tenant_id="t1", external_reference="APP-003", title="Queue A")
    await repo.assign(tenant_id="t1", case_id=first.id, queue="environmental-review", assignee="analyst-1")
    second = await repo.create(tenant_id="t2", external_reference="APP-004", title="Other tenant")
    await repo.assign(tenant_id="t2", case_id=second.id, queue="environmental-review", assignee="analyst-2")
    rows = await repo.list_queue(tenant_id="t1", queue="environmental-review", states={"intake"})
    assert [row.id for row in rows] == [first.id]


def test_transition_rules_are_explicit() -> None:
    validate_transition("intake", "analysis")
    with pytest.raises(ValueError):
        validate_transition("intake", "approved")
    with pytest.raises(ValueError, match="decision_officer_required"):
        validate_decision("approved", None, "reason")
    with pytest.raises(ValueError, match="decision_reason_required"):
        validate_decision("rejected", "officer", " ")


def test_case_model_has_tenant_and_workflow_fields() -> None:
    assert CaseORM.__tablename__ == "government_cases"
    assert CaseORM.tenant_id is not None
