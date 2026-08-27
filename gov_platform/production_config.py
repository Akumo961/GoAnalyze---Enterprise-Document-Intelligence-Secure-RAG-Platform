"""Fail-closed production configuration validation.

This validator checks deployment-critical settings without attempting to prove
that external infrastructure (Kubernetes, databases, IdPs, object storage,
etc.) is actually reachable. Runtime/integration validation remains a
separate operational concern.
"""
from __future__ import annotations

from urllib.parse import urlparse

from .config import Settings


class ProductionConfigError(ValueError):
    """Raised when production configuration is unsafe or incomplete."""


def validate_production_config(settings: Settings) -> None:
    """Validate settings required before starting a production deployment."""
    if settings.environment != "production":
        return

    errors: list[str] = []
    if settings.allow_insecure_dev_auth:
        errors.append("insecure development authentication is enabled")
    if settings.otel_tracing_enabled is False:
        errors.append("OpenTelemetry tracing is disabled")
    if not settings.rate_limit_enabled:
        errors.append("rate limiting is disabled")
    if not settings.audit_hash_secret.strip() or len(settings.audit_hash_secret) < 32:
        errors.append("audit hash secret must contain at least 32 characters")
    if settings.minio_secure is False:
        errors.append("object storage TLS must be enabled")

    database = urlparse(settings.database_url)
    if database.scheme not in {"postgresql", "postgresql+asyncpg"}:
        errors.append("production database must use PostgreSQL")
    if database.hostname in {None, "localhost", "127.0.0.1"}:
        errors.append("production database must not use localhost")

    redis = urlparse(settings.redis_url)
    if redis.scheme not in {"redis", "rediss"}:
        errors.append("production Redis URL is invalid")

    opensearch = urlparse(settings.opensearch_url)
    if opensearch.scheme not in {"http", "https"} or not opensearch.hostname:
        errors.append("production OpenSearch URL is invalid")

    if errors:
        raise ProductionConfigError("invalid production configuration: " + "; ".join(errors))


def validate_startup_configuration(settings: Settings) -> None:
    """Validate deployment configuration at application startup."""
    validate_production_config(settings)
