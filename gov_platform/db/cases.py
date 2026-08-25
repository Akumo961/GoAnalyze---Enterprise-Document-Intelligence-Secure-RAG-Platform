"""Persistent government case/workflow records.

The state machine is deliberately explicit and human-controlled. This table
stores decision-support workflow state; it never represents an autonomous
legal decision.
"""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Index, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from .models import Base

CASE_STATES = frozenset({"intake", "analysis", "review", "approved", "rejected", "closed"})
TERMINAL_STATES = frozenset({"approved", "rejected", "closed"})
ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    "intake": frozenset({"analysis", "closed"}),
    "analysis": frozenset({"review", "closed"}),
    "review": frozenset({"approved", "rejected", "analysis"}),
    "approved": frozenset({"closed"}),
    "rejected": frozenset({"closed", "analysis"}),
    "closed": frozenset(),
}


def _utcnow() -> datetime:
    return datetime.now(UTC)


class CaseORM(Base):
    __tablename__ = "government_cases"
    __table_args__ = (
        Index("ix_government_cases_tenant_state", "tenant_id", "state"),
        Index("ix_government_cases_tenant_created", "tenant_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(255), nullable=False)
    external_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False, default="intake")
    priority: Mapped[str] = mapped_column(String(32), nullable=False, default="normal")
    assigned_queue: Mapped[str | None] = mapped_column(String(255), nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    decision_officer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    decision_reason: Mapped[str | None] = mapped_column(String(8192), nullable=True)
    attributes: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


def validate_transition(current: str, target: str) -> None:
    if current not in CASE_STATES or target not in CASE_STATES:
        raise ValueError("unknown_case_state")
    if target not in ALLOWED_TRANSITIONS[current]:
        raise ValueError(f"invalid_case_transition:{current}->{target}")


def validate_decision(target: str, decision_officer: str | None, reason: str | None) -> None:
    if target in {"approved", "rejected"}:
        if not decision_officer:
            raise ValueError("decision_officer_required")
        if not reason or not reason.strip():
            raise ValueError("decision_reason_required")
