"""Async persistence operations for customer regulatory knowledge."""
from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..regulatory_knowledge import RegulatoryObligation, RegulatorySource, active_on
from .regulatory import (
    RegulatoryObligationORM,
    RegulatorySourceORM,
    obligation_from_orm,
    obligation_to_orm,
    source_from_orm,
    source_to_orm,
)


class RegulatoryKnowledgeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_source(self, source: RegulatorySource) -> RegulatorySource:
        existing = await self._session.get(
            RegulatorySourceORM, (source.source_id, source.version)
        )
        if existing is None:
            self._session.add(source_to_orm(source))
        else:
            for field in (
                "title",
                "knowledge_type",
                "jurisdiction",
                "publisher",
                "authority",
                "authoritative",
                "source_uri",
                "effective_from",
                "effective_to",
            ):
                setattr(
                    existing,
                    field,
                    getattr(source, field).value
                    if field in {"knowledge_type", "authority"}
                    else getattr(source, field),
                )
        await self._session.commit()
        return source

    async def add_obligation(
        self, obligation: RegulatoryObligation
    ) -> RegulatoryObligation:
        self._session.add(obligation_to_orm(obligation))
        await self._session.commit()
        return obligation

    async def active_obligations(
        self, *, jurisdiction: str, when: date
    ) -> list[RegulatoryObligation]:
        result = await self._session.execute(
            select(RegulatoryObligationORM)
            .where(RegulatoryObligationORM.jurisdiction == jurisdiction)
            .order_by(RegulatoryObligationORM.obligation_id)
        )
        return [
            obligation_from_orm(row)
            for row in result.scalars().all()
            if active_on(obligation_from_orm(row), when)
        ]

    async def source(self, source_id: str, version: str) -> RegulatorySource | None:
        row = await self._session.get(RegulatorySourceORM, (source_id, version))
        return source_from_orm(row) if row is not None else None
