"""Safe retention execution planning.

This layer intentionally separates policy evaluation from destructive deletion.
A caller must provide a legal-hold decision and an explicit deletion callback;
the platform never silently deletes records merely because they are old.
"""
from dataclasses import dataclass
from datetime import UTC, datetime
from collections.abc import Callable, Iterable

from .retention import RetentionPolicy, deletion_due


@dataclass(frozen=True)
class RetentionCandidate:
    resource_id: str
    created_at: datetime
    legal_hold: bool = False


@dataclass(frozen=True)
class RetentionAction:
    resource_id: str
    action: str
    reason: str


def plan_retention(
    candidates: Iterable[RetentionCandidate],
    policy: RetentionPolicy,
    *,
    now: datetime | None = None,
) -> list[RetentionAction]:
    current = now or datetime.now(UTC)
    actions: list[RetentionAction] = []
    for candidate in candidates:
        if candidate.legal_hold:
            actions.append(RetentionAction(candidate.resource_id, "hold", "legal_hold"))
        elif deletion_due(candidate.created_at, policy, now=current):
            actions.append(RetentionAction(candidate.resource_id, "delete_eligible", "retention_expired"))
        else:
            actions.append(RetentionAction(candidate.resource_id, "retain", "retention_active"))
    return actions


def execute_deletions(
    actions: Iterable[RetentionAction],
    delete: Callable[[str], None],
) -> int:
    """Execute only explicitly eligible actions; report count for audit/metrics."""
    count = 0
    for action in actions:
        if action.action == "delete_eligible":
            delete(action.resource_id)
            count += 1
    return count
