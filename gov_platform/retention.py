"""Retention and deletion policy primitives; enforcement remains deployment-specific."""
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True)
class RetentionPolicy:
    policy_id: str
    retention_days: int
    legal_hold_supported: bool = True

    def __post_init__(self) -> None:
        if self.retention_days < 1:
            raise ValueError("retention_days_must_be_positive")


def deletion_due(created_at: datetime, policy: RetentionPolicy, *, now: datetime | None = None) -> bool:
    current = now or datetime.now(UTC)
    if created_at.tzinfo is None:
        raise ValueError("created_at_must_be_timezone_aware")
    return current >= created_at + timedelta(days=policy.retention_days)
