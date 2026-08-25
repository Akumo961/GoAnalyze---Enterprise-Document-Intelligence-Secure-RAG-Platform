from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from gov_platform.db.models import Base
from gov_platform.db.regulatory import RegulatoryObligationORM, RegulatorySourceORM
from gov_platform.db.regulatory_repository import RegulatoryKnowledgeRepository
from gov_platform.regulatory_knowledge import KnowledgeType, RegulatoryObligation, RegulatorySource, SourceAuthority
from gov_platform.retention import RetentionPolicy
from gov_platform.retention_executor import RetentionCandidate, execute_deletions, plan_retention


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as db:
        yield db
    await engine.dispose()


@pytest.mark.asyncio
async def test_regulatory_source_versions_are_persistent(session) -> None:
    repo = RegulatoryKnowledgeRepository(session)
    source_v1 = RegulatorySource("demo-source", "Synthetic source", KnowledgeType.guidance, "Québec", "Demo", False, "demo://1", version="1", authority=SourceAuthority.demo)
    source_v2 = RegulatorySource("demo-source", "Synthetic source", KnowledgeType.guidance, "Québec", "Demo", False, "demo://2", version="2", authority=SourceAuthority.customer)
    await repo.upsert_source(source_v1)
    await repo.upsert_source(source_v2)
    assert (await repo.source("demo-source", "1")).source_uri == "demo://1"
    assert (await repo.source("demo-source", "2")).source_uri == "demo://2"
    assert await session.scalar(__import__("sqlalchemy").select(__import__("sqlalchemy").func.count()).select_from(RegulatorySourceORM)) == 2


@pytest.mark.asyncio
async def test_active_obligations_are_date_and_jurisdiction_scoped(session) -> None:
    repo = RegulatoryKnowledgeRepository(session)
    source = RegulatorySource("s", "Synthetic", KnowledgeType.guidance, "Québec", "Demo", False, "demo://s", authority=SourceAuthority.demo)
    await repo.upsert_source(source)
    await repo.add_obligation(RegulatoryObligation("o1", "s", "Active", "Synthetic", jurisdiction="Québec", effective_from=date(2026, 1, 1), evidence_requirements=("study",)))
    await repo.add_obligation(RegulatoryObligation("o2", "s", "Expired", "Synthetic", jurisdiction="Québec", effective_from=date(2025, 1, 1), effective_to=date(2025, 12, 31), evidence_requirements=("study",)))
    await repo.add_obligation(RegulatoryObligation("o3", "s", "Other", "Synthetic", jurisdiction="Ontario", effective_from=date(2026, 1, 1), evidence_requirements=("study",)))
    active = await repo.active_obligations(jurisdiction="Québec", when=date(2026, 8, 25))
    assert [item.obligation_id for item in active] == ["o1"]


def test_retention_execution_requires_explicit_eligibility_and_respects_hold() -> None:
    policy = RetentionPolicy("demo", 30)
    old = datetime.now(UTC) - timedelta(days=31)
    actions = plan_retention([
        RetentionCandidate("old", old),
        RetentionCandidate("held", old, legal_hold=True),
    ], policy)
    deleted: list[str] = []
    assert execute_deletions(actions, deleted.append) == 1
    assert deleted == ["old"]
    assert any(a.resource_id == "held" and a.action == "hold" for a in actions)


def test_persistent_model_contains_expected_tables() -> None:
    assert RegulatorySourceORM.__tablename__ == "regulatory_sources"
    assert RegulatoryObligationORM.__tablename__ == "regulatory_obligations"
