"""Versioned regulatory knowledge primitives.

Authoritative legal content is external to the core platform. This module
provides a schema and deterministic matching engine for customer-loaded,
source-controlled regulatory knowledge.
"""
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Iterable


class KnowledgeType(StrEnum):
    law = "law"
    regulation = "regulation"
    policy = "policy"
    directive = "directive"
    permit_condition = "permit_condition"
    guidance = "guidance"


@dataclass(frozen=True)
class RegulatorySource:
    source_id: str
    title: str
    knowledge_type: KnowledgeType
    jurisdiction: str
    publisher: str
    authoritative: bool
    source_uri: str
    effective_from: date | None = None
    effective_to: date | None = None
    version: str = "1"


@dataclass(frozen=True)
class RegulatoryObligation:
    obligation_id: str
    source_id: str
    title: str
    description: str
    evidence_types: tuple[str, ...]
    jurisdiction: str
    effective_from: date | None = None
    effective_to: date | None = None
    exceptions: tuple[str, ...] = ()


def active_on(item: RegulatorySource | RegulatoryObligation, when: date) -> bool:
    return (item.effective_from is None or item.effective_from <= when) and (
        item.effective_to is None or when <= item.effective_to
    )


def obligations_for(
    obligations: Iterable[RegulatoryObligation],
    *,
    jurisdiction: str,
    when: date,
) -> list[RegulatoryObligation]:
    """Return only active obligations for the requested jurisdiction."""
    return [
        obligation
        for obligation in obligations
        if obligation.jurisdiction == jurisdiction and active_on(obligation, when)
    ]
