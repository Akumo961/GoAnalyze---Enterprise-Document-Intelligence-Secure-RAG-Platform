"""Versioned regulatory knowledge primitives.

Authoritative legal content is external to the core platform. This module
provides a schema and deterministic matching engine for customer-loaded,
source-controlled regulatory knowledge.
"""
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class KnowledgeType(StrEnum):
    law = "law"
    regulation = "regulation"
    policy = "policy"
    directive = "directive"
    permit_condition = "permit_condition"
    guidance = "guidance"


class SourceAuthority(StrEnum):
    demo = "demo"
    customer = "customer"
    authoritative = "authoritative"
    unverified = "unverified"


@dataclass(frozen=True, init=False)
class RegulatorySource:
    source_id: str
    title: str
    knowledge_type: KnowledgeType
    jurisdiction: str
    publisher: str
    authoritative: bool
    source_uri: str
    effective_from: date | None
    effective_to: date | None
    version: str
    authority: SourceAuthority

    def __init__(
        self,
        source_id: str,
        title: str,
        knowledge_type: KnowledgeType | None = None,
        jurisdiction: str = "",
        publisher: str = "",
        authoritative: bool = False,
        source_uri: str = "",
        effective_from: date | None = None,
        effective_to: date | None = None,
        version: str = "1",
        authority: SourceAuthority | None = None,
    ) -> None:
        resolved_authority = authority or (SourceAuthority.authoritative if authoritative else SourceAuthority.unverified)
        object.__setattr__(self, "source_id", source_id)
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "knowledge_type", knowledge_type or KnowledgeType.guidance)
        object.__setattr__(self, "jurisdiction", jurisdiction)
        object.__setattr__(self, "publisher", publisher)
        object.__setattr__(self, "authoritative", authoritative or resolved_authority == SourceAuthority.authoritative)
        object.__setattr__(self, "source_uri", source_uri)
        object.__setattr__(self, "effective_from", effective_from)
        object.__setattr__(self, "effective_to", effective_to)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "authority", resolved_authority)


@dataclass(frozen=True, init=False)
class RegulatoryObligation:
    obligation_id: str
    source_id: str
    title: str
    description: str
    evidence_types: tuple[str, ...]
    jurisdiction: str
    effective_from: date | None
    effective_to: date | None
    exceptions: tuple[str, ...]
    evidence_requirements: tuple[str, ...]
    verified: bool

    def __init__(
        self,
        obligation_id: str,
        source_id: str,
        title: str,
        description: str,
        evidence_types: tuple[str, ...] = (),
        jurisdiction: str = "",
        effective_from: date | None = None,
        effective_to: date | None = None,
        exceptions: tuple[str, ...] = (),
        evidence_requirements: tuple[str, ...] | None = None,
        verified: bool = False,
    ) -> None:
        resolved_evidence = evidence_requirements if evidence_requirements is not None else evidence_types
        object.__setattr__(self, "obligation_id", obligation_id)
        object.__setattr__(self, "source_id", source_id)
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "evidence_types", tuple(resolved_evidence))
        object.__setattr__(self, "jurisdiction", jurisdiction)
        object.__setattr__(self, "effective_from", effective_from)
        object.__setattr__(self, "effective_to", effective_to)
        object.__setattr__(self, "exceptions", tuple(exceptions))
        object.__setattr__(self, "evidence_requirements", tuple(resolved_evidence))
        object.__setattr__(self, "verified", verified)


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
