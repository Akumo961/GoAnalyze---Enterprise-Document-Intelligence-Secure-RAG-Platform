"""Tenant-scoped persistence for registered government documents."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import DocumentORM


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        tenant_id: str,
        case_id: UUID | None,
        filename: str,
        content_type: str,
        classification: str,
        sha256: str,
        object_uri: str,
        metadata: dict,
    ) -> DocumentORM:
        document = DocumentORM(
            tenant_id=tenant_id,
            case_id=case_id,
            filename=filename,
            content_type=content_type,
            classification=classification,
            sha256=sha256,
            object_uri=object_uri,
            doc_metadata=metadata,
        )
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def get(self, *, tenant_id: str, document_id: UUID) -> DocumentORM | None:
        result = await self.session.execute(
            select(DocumentORM).where(
                DocumentORM.id == document_id,
                DocumentORM.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_case(self, *, tenant_id: str, case_id: UUID) -> list[DocumentORM]:
        result = await self.session.execute(
            select(DocumentORM)
            .where(DocumentORM.tenant_id == tenant_id, DocumentORM.case_id == case_id)
            .order_by(DocumentORM.created_at, DocumentORM.id)
        )
        return list(result.scalars().all())
