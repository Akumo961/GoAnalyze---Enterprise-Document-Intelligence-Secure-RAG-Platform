"""Tamper-evident audit-chain primitives for decision-support events."""
import hashlib
import json
from typing import Iterable

from .models import AuditEvent


def canonical_event(event: AuditEvent) -> str:
    payload = event.model_dump(mode="json", exclude={"event_hash"})
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def seal_event(event: AuditEvent, previous_hash: str | None) -> AuditEvent:
    unsigned = event.model_copy(update={"previous_hash": previous_hash, "event_hash": None})
    digest = hashlib.sha256(canonical_event(unsigned).encode("utf-8")).hexdigest()
    return unsigned.model_copy(update={"event_hash": digest})


def verify_chain(events: Iterable[AuditEvent]) -> bool:
    previous: str | None = None
    for event in events:
        if event.previous_hash != previous or not event.event_hash:
            return False
        expected = seal_event(event, previous).event_hash
        if event.event_hash != expected:
            return False
        previous = event.event_hash
    return True
