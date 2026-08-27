"""Tenant-scoped persistence for analyst workflow cases."""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .cases import CaseORM, validate_decision, validate_transition


class CasePersistenceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        tenant_id: str,
        external_reference: str,
        title: str,
        priority: str = "normal",
        attributes: dict | None = None,
    ) -> CaseORM:
        case = CaseORM(
            tenant_id=tenant_id,
            external_reference=external_reference,
            title=title,
            priority=priority,
            attributes=attributes or {},
        )
        self._session.add(case)
        await self._session.commit()
        await self._session.refresh(case)
        return case

    async def get(self, *, tenant_id: str, case_id: UUID) -> CaseORM | None:
        result = await self._session.execute(
            select(CaseORM).where(CaseORM.id == case_id, CaseORM.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def list_queue(
        self, *, tenant_id: str, queue: str | None = None, states: set[str] | None = None
    ) -> list[CaseORM]:
        conditions = [CaseORM.tenant_id == tenant_id]
        if queue is not None:
            conditions.append(CaseORM.assigned_queue == queue)
        if states:
            conditions.append(CaseORM.state.in_(states))
        result = await self._session.execute(
            select(CaseORM).where(*conditions).order_by(CaseORM.created_at, CaseORM.id)
        )
        return list(result.scalars().all())

    async def assign(
        self, *, tenant_id: str, case_id: UUID, queue: str, assignee: str | None = None
    ) -> CaseORM:
        case = await self.get(tenant_id=tenant_id, case_id=case_id)
        if case is None:
            raise LookupError("case_not_found")
        case.assigned_queue = queue
        case.assigned_to = assignee
        case.updated_at = datetime.now(UTC)
        await self._session.commit()
        await self._session.refresh(case)
        return case

    async def transition(
        self,
        *,
        tenant_id: str,
        case_id: UUID,
        target: str,
        actor: str,
        decision_reason: str | None = None,
    ) -> CaseORM:
        case = await self.get(tenant_id=tenant_id, case_id=case_id)
        if case is None:
            raise LookupError("case_not_found")
        validate_transition(case.state, target)
        decision_officer = actor if target in {"approved", "rejected"} else case.decision_officer
        validate_decision(target, decision_officer, decision_reason)
        case.state = target
        case.updated_at = datetime.now(UTC)
        if target in {"approved", "rejected"}:
            case.decision_officer = actor
            case.decision_reason = decision_reason.strip() if decision_reason else None
        if target == "closed":
            case.closed_at = datetime.now(UTC)
        await self._session.commit()
        await self._session.refresh(case)
        return case
