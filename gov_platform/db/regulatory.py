"""Persistent customer-loaded regulatory knowledge.

Records are deliberately source-labelled. The platform stores authoritative
claims supplied by an authorized customer but does not itself certify legal
authority or correctness.
"""
from __future__ import annotations

from datetime import date
from sqlalchemy import Boolean, Date, Index, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from .models import Base
from ..regulatory_knowledge import KnowledgeType, RegulatoryObligation, RegulatorySource, SourceAuthority


class RegulatorySourceORM(Base):
    __tablename__ = "regulatory_sources"
    __table_args__ = (Index("ix_regulatory_sources_jurisdiction", "jurisdiction"),)

    source_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    version: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    knowledge_type: Mapped[str] = mapped_column(String(64), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(255), nullable=False)
    publisher: Mapped[str] = mapped_column(String(512), nullable=False)
    authority: Mapped[str] = mapped_column(String(64), nullable=False)
    authoritative: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    source_uri: Mapped[str] = mapped_column(String(2048), nullable=False)
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)


class RegulatoryObligationORM(Base):
    __tablename__ = "regulatory_obligations"
    __table_args__ = (
        Index("ix_regulatory_obligations_source_id", "source_id"),
        Index("ix_regulatory_obligations_jurisdiction", "jurisdiction"),
    )

    obligation_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    source_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    description: Mapped[str] = mapped_column(String(8192), nullable=False)
    evidence_requirements: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    jurisdiction: Mapped[str] = mapped_column(String(255), nullable=False)
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    exceptions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


def source_to_orm(source: RegulatorySource) -> RegulatorySourceORM:
    return RegulatorySourceORM(
        source_id=source.source_id,
        version=source.version,
        title=source.title,
        knowledge_type=source.knowledge_type.value,
        jurisdiction=source.jurisdiction,
        publisher=source.publisher,
        authority=source.authority.value,
        authoritative=source.authoritative,
        source_uri=source.source_uri,
        effective_from=source.effective_from,
        effective_to=source.effective_to,
    )


def obligation_to_orm(obligation: RegulatoryObligation) -> RegulatoryObligationORM:
    return RegulatoryObligationORM(
        obligation_id=obligation.obligation_id,
        source_id=obligation.source_id,
        title=obligation.title,
        description=obligation.description,
        evidence_requirements=list(obligation.evidence_requirements),
        jurisdiction=obligation.jurisdiction,
        effective_from=obligation.effective_from,
        effective_to=obligation.effective_to,
        exceptions=list(obligation.exceptions),
        verified=obligation.verified,
    )


def source_from_orm(row: RegulatorySourceORM) -> RegulatorySource:
    return RegulatorySource(
        source_id=row.source_id,
        title=row.title,
        knowledge_type=KnowledgeType(row.knowledge_type),
        jurisdiction=row.jurisdiction,
        publisher=row.publisher,
        authoritative=row.authoritative,
        source_uri=row.source_uri,
        effective_from=row.effective_from,
        effective_to=row.effective_to,
        version=row.version,
        authority=SourceAuthority(row.authority),
    )


def obligation_from_orm(row: RegulatoryObligationORM) -> RegulatoryObligation:
    return RegulatoryObligation(
        obligation_id=row.obligation_id,
        source_id=row.source_id,
        title=row.title,
        description=row.description,
        evidence_requirements=tuple(row.evidence_requirements),
        jurisdiction=row.jurisdiction,
        effective_from=row.effective_from,
        effective_to=row.effective_to,
        exceptions=tuple(row.exceptions),
        verified=row.verified,
    )
