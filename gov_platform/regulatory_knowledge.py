"""Regulatory knowledge primitives.

This module deliberately contains no invented Québec legal requirements.
Authoritative content is customer-managed data and must carry provenance,
version, jurisdiction, effective dates, and verification state before it can
be used as a regulatory source.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from typing import Any


class SourceAuthority(StrEnum):
    authoritative = "authoritative"
    customer_approved = "customer_approved"
    demo = "demo"
    unverified = "unverified"


@dataclass(frozen=True)
class RegulatorySource:
    source_id: str
    title: str
    authority: SourceAuthority
    jurisdiction: str
    publisher: str
    source_uri: str | None = None
    version: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    checksum: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RegulatoryObligation:
    obligation_id: str
    source_id: str
    title: str
    description: str
    evidence_requirements: tuple[str, ...] = ()
    deadlines: tuple[str, ...] = ()
    conditions: tuple[str, ...] = ()
    exceptions: tuple[str, ...] = ()
    jurisdiction: str | None = None
    verified: bool = False


@dataclass(frozen=True)
class EvidenceMapping:
    obligation_id: str
    document_id: str
    evidence_excerpt: str
    confidence: float
    verified_by_human: bool = False


def source_is_usable(source: RegulatorySource) -> bool:
    """Only approved/authoritative sources may drive regulatory assertions."""
    return source.authority in {
        SourceAuthority.authoritative,
        SourceAuthority.customer_approved,
    }


def map_evidence(
    obligation: RegulatoryObligation,
    document_id: str,
    excerpt: str,
    confidence: float,
) -> EvidenceMapping:
    if not obligation.verified:
        raise ValueError("unverified_regulatory_obligation")
    if not excerpt.strip():
        raise ValueError("empty_evidence_excerpt")
    if not 0 <= confidence <= 1:
        raise ValueError("confidence_out_of_range")
    return EvidenceMapping(
        obligation_id=obligation.obligation_id,
        document_id=document_id,
        evidence_excerpt=excerpt[:4000],
        confidence=confidence,
    )


DEMO_SOURCES: tuple[RegulatorySource, ...] = ()
DEMO_OBLIGATIONS: tuple[RegulatoryObligation, ...] = ()


__all__ = [
    "DEMO_OBLIGATIONS",
    "DEMO_SOURCES",
    "EvidenceMapping",
    "RegulatoryObligation",
    "RegulatorySource",
    "SourceAuthority",
    "map_evidence",
    "source_is_usable",
]
