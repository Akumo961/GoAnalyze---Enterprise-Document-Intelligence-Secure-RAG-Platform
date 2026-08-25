"""Phase 2 document-to-RAG pipeline adapter.

This adapter keeps document extraction, tenant-scoped indexing and RAG
retrieval separate from the legacy ingestion pipeline so Phase 1 behavior is
not silently changed.
"""
from __future__ import annotations

from dataclasses import dataclass

from .document_extract import ExtractedDocument, extract_text
from .models import EvidenceCitation
from .rag_engine import RAGAnswer, ProductionRAG
from .rag_index import TenantScopedIndex


@dataclass(frozen=True)
class Phase2DocumentResult:
    extraction: ExtractedDocument
    indexed_chunks: int


class Phase2Pipeline:
    def __init__(self, index: TenantScopedIndex | None = None, rag: ProductionRAG | None = None) -> None:
        self.index = index or TenantScopedIndex()
        self.rag = rag or ProductionRAG()

    def ingest(self, tenant_id: str, document_id, data: bytes, content_type: str) -> Phase2DocumentResult:
        extracted = extract_text(data, content_type)
        chunks = [chunk.strip() for chunk in extracted.text.split("\n\n") if chunk.strip()]
        if not chunks:
            chunks = [extracted.text.strip()] if extracted.text.strip() else []
        for number, chunk in enumerate(chunks):
            self.index.add(
                tenant_id,
                EvidenceCitation(
                    document_id=document_id,
                    version=1,
                    chunk_id=str(number),
                    sha256=extracted.sha256,
                    excerpt=chunk[:4000],
                ),
            )
        return Phase2DocumentResult(extraction=extracted, indexed_chunks=len(chunks))

    def answer(self, tenant_id: str, question: str, top_k: int = 5) -> RAGAnswer:
        retrieved = self.index.search(tenant_id, question, top_k=top_k)
        return self.rag.answer(question, [item.citation for item in retrieved], tenant_id=tenant_id)
