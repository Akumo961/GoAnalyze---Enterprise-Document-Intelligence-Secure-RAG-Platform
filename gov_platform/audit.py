import hashlib
import hmac
import json

from sqlalchemy.ext.asyncio import AsyncSession

from .config import get_settings
from .db.repositories import AuditRepository
from .models import AuditEvent
from .observability import CASE_ASSIGNMENTS, record_human_decision


class AuditLog:
    """Hash-chained, tenant-scoped audit trail persisted to PostgreSQL.

    Each event's ``event_hash`` is an HMAC over the event payload plus the
    previous event's hash for that tenant, so any tampering with historical
    records breaks the chain.

    Concurrency: a naive "read the latest event, then write a new one
    referencing it" is a classic read-then-write race. Two concurrent
    appends for the *same tenant* can otherwise both read the same head and
    both link to it, forking the chain. The current mechanism uses a dedicated
    `audit_chain_state` table and a real `SELECT ... FOR UPDATE` row lock on
    that tenant's row before reading the head and writing the next event.
    """

    async def append(self, session: AsyncSession, event: AuditEvent) -> AuditEvent:
        result = await AuditRepository(session).append_with_chain_lock(event, self._hash_event)
        if event.action == "case.human_decision_recorded":
            decision = str(event.details.get("decision", "unknown"))
            record_human_decision(decision, override=bool(event.details.get("ai_override", False)))
        elif event.action == "case.assigned":
            queue = str(event.details.get("queue", "unknown"))
            CASE_ASSIGNMENTS.labels(queue=queue).inc()
        return result

    async def list_events(self, session: AsyncSession, tenant_id: str) -> list[AuditEvent]:
        return await AuditRepository(session).list_for_tenant(tenant_id)

    async def list_events_paginated(
        self, session: AsyncSession, tenant_id: str, page: int, page_size: int
    ) -> tuple[list[AuditEvent], int]:
        return await AuditRepository(session).list_for_tenant_paginated(tenant_id, page, page_size)

    def _hash_event(self, event: AuditEvent) -> str:
        secret = get_settings().audit_hash_secret.encode("utf-8")
        payload = event.model_dump(mode="json")
        payload["event_hash"] = None
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hmac.new(secret, serialized, hashlib.sha256).hexdigest()


audit_log = AuditLog()
