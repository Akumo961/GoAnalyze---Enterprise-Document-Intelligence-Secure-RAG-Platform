"""RAG provider configuration.

No external AI provider is enabled implicitly. Production requires explicit
HTTPS endpoint, model and secret configuration supplied by the deployment.
"""
from __future__ import annotations

import os

from .rag_engine import OpenAICompatibleProvider, ProductionRAG


def build_rag_from_environment() -> ProductionRAG:
    provider_name = os.getenv("GOANALYZE_AI_PROVIDER", "retrieval-only")
    if provider_name == "retrieval-only":
        return ProductionRAG()
    if provider_name != "openai-compatible":
        raise ValueError("unsupported_ai_provider")
    endpoint = os.getenv("GOANALYZE_AI_ENDPOINT", "")
    key = os.getenv("GOANALYZE_AI_API_KEY", "")
    model = os.getenv("GOANALYZE_AI_MODEL", "")
    return ProductionRAG(OpenAICompatibleProvider(endpoint, key, model))
