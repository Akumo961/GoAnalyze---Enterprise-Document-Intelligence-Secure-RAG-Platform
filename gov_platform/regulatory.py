"""Versioned regulatory knowledge model.

This module deliberately contains no asserted Québec legal requirements.  A
knowledge pack is data supplied by an authorized source owner and carries
provenance, jurisdiction, authority, effective dates, and verification state.
The application refuses to present unverified/demo obligations as authoritative.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Any


class KnowledgeStatus(StrEnum):
    demo = "demo"
    draft = "draft"
    verified = "verified"
    retired = "retired"


@dataclass(frozen=True)
class RegulatorySource:
    source_id: str
    title: str
    publisher: str
    jurisdiction: str
    canonical_uri: str
    retrieved_on: date
    status: KnowledgeStatus
    checksum: str | None = None


@dataclass(frozen=True)
class RegulatoryObligation:
    obligation_id: str
    title: str
    description: str
    source_id: str
    applicable_jurisdictions: tuple[str, ...]
    evidence_types: tuple[str, ...]
    deadline_days: int | None = None
    exceptions: tuple[str, ...] = ()
    status: KnowledgeStatus = KnowledgeStatus.draft
    metadata: dict[str, Any] | None = None


class RegulatoryKnowledgeBase:
    """In-memory registry suitable for demo/testing and replaceable by a DB-backed store."""

    def __init__(self, sources: list[RegulatorySource] | None = None, obligations: list[RegulatoryObligation] | None = None) -> None:
        self._sources = {item.source_id: item for item in sources or []}
        self._obligations = {item.obligation_id: item for item in obligations or []}

    def obligations_for(self, jurisdiction: str, *, include_unverified: bool = False) -> list[RegulatoryObligation]:
        values = []
        for obligation in self._obligations.values():
            if jurisdiction not in obligation.applicable_jurisdictions:
                continue
            if not include_unverified and obligation.status is not KnowledgeStatus.verified:
                continue
            values.append(obligation)
        return sorted(values, key=lambda item: item.obligation_id)

    def source(self, source_id: str) -> RegulatorySource | None:
        return self._sources.get(source_id)

    def add_source(self, source: RegulatorySource) -> None:
        self._sources[source.source_id] = source

    def add_obligation(self, obligation: RegulatoryObligation) -> None:
        if obligation.source_id not in self._sources:
            raise ValueError("obligation_source_not_registered")
        self._obligations[obligation.obligation_id] = obligation

    def health(self) -> dict[str, int]:
        return {
            "sources": len(self._sources),
            "obligations": len(self._obligations),
            "verified_obligations": sum(item.status is KnowledgeStatus.verified for item in self._obligations.values()),
            "demo_obligations": sum(item.status is KnowledgeStatus.demo for item in self._obligations.values()),
        }
