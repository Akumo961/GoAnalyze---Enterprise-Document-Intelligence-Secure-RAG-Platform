"""Fail-closed production configuration validation.

Validation proves configuration safety properties only; it does not prove that
external infrastructure is reachable, correctly configured, patched, or
independently audited.
"""
from __future__ import annotations

from urllib.parse import urlparse

from .config import Settings


class ProductionConfigError(ValueError):
    """Raised when production configuration is unsafe or incomplete."""


def _require_https(value: str, field: str, errors: list[str]) -> None:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname:
        errors.append(f"{field} must use HTTPS in production")


def validate_production_config(settings: Settings) -> None:
    """Validate deployment-critical settings before a production start."""
    if settings.environment != "production":
        return

    errors: list[str] = []
    if settings.allow_insecure_dev_auth:
        errors.append("insecure development authentication is enabled")
    if not settings.otel_tracing_enabled:
        errors.append("OpenTelemetry tracing is disabled")
    if not settings.rate_limit_enabled:
        errors.append("rate limiting is disabled")
    if not settings.audit_hash_secret.strip() or len(settings.audit_hash_secret) < 32:
        errors.append("audit hash secret must contain at least 32 characters")
    if not settings.minio_secure:
        errors.append("object storage TLS must be enabled")

    database = urlparse(str(settings.database_url))
    if database.scheme not in {"postgresql", "postgresql+asyncpg"}:
        errors.append("production database must use PostgreSQL")
    if database.hostname in {None, "localhost", "127.0.0.1"}:
        errors.append("production database must not use localhost")
    if not database.password:
        errors.append("production database credentials must not be embedded without a password")

    redis = urlparse(settings.redis_url)
    if redis.scheme != "rediss":
        errors.append("production Redis must use TLS (rediss://)")
    if not redis.hostname:
        errors.append("production Redis URL must contain a hostname")

    _require_https(settings.opensearch_url, "production OpenSearch URL", errors)
    _require_https(str(settings.keycloak_issuer), "production identity-provider issuer", errors)
    if settings.keycloak_jwks_url:
        _require_https(settings.keycloak_jwks_url, "production JWKS URL", errors)

    if not settings.allowed_origins or any(origin == "*" for origin in settings.allowed_origins):
        errors.append("production CORS origins must be explicit; wildcard origin is forbidden")
    for origin in settings.allowed_origins:
        parsed = urlparse(origin)
        if parsed.scheme != "https" or not parsed.hostname:
            errors.append("production CORS origins must use HTTPS")

    if errors:
        raise ProductionConfigError("invalid production configuration: " + "; ".join(errors))


def validate_startup_configuration(settings: Settings) -> None:
    """Validate deployment configuration at application startup."""
    validate_production_config(settings)
