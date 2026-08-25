"""Tenant-scoped chunk index used by the Phase 2 retrieval layer.

The interface is intentionally small so it can later be backed by OpenSearch
without changing RAG authorization semantics. The in-memory implementation is
for local execution and tests; it is not presented as a production datastore.
"""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from .models import EvidenceCitation
from .rag_engine import RetrievalChunk, retrieve


@dataclass(frozen=True)
class IndexedChunk:
    tenant_id: str
    citation: EvidenceCitation


class TenantScopedIndex:
    def __init__(self) -> None:
        self._chunks: list[IndexedChunk] = []

    def add(self, tenant_id: str, citation: EvidenceCitation) -> None:
        if not tenant_id:
            raise ValueError("tenant_id_required")
        self._chunks.append(IndexedChunk(tenant_id, citation))

    def search(self, tenant_id: str, question: str, top_k: int = 5) -> list[RetrievalChunk]:
        candidates = [item.citation for item in self._chunks if item.tenant_id == tenant_id]
        return retrieve(question, candidates, top_k=top_k)

    def count(self, tenant_id: str) -> int:
        return sum(1 for item in self._chunks if item.tenant_id == tenant_id)


index = TenantScopedIndex()
