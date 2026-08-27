import pytest

from gov_platform.config import Settings
from gov_platform.production_config import ProductionConfigError, validate_production_config


@pytest.fixture(autouse=True)
def isolate_production_settings_from_host_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep acceptance tests deterministic when CI has GOV_* variables configured."""
    for name in (
        "GOV_ENVIRONMENT",
        "GOV_ALLOW_INSECURE_DEV_AUTH",
        "GOV_AUDIT_HASH_SECRET",
        "GOV_OTEL_TRACING_ENABLED",
        "GOV_RATE_LIMIT_ENABLED",
        "GOV_MINIO_SECURE",
        "GOV_DATABASE_URL",
        "GOV_REDIS_URL",
        "GOV_OPENSEARCH_URL",
        "GOV_ALLOWED_ORIGINS",
    ):
        monkeypatch.delenv(name, raising=False)


def production_settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "environment": "production",
        "audit_hash_secret": "x" * 64,
        "otel_tracing_enabled": True,
        "rate_limit_enabled": True,
        "minio_secure": True,
        "database_url": "postgresql+asyncpg://app:secret@postgres.internal:5432/goanalyze",
        "redis_url": "rediss://redis.internal:6379/0",
        "opensearch_url": "https://opensearch.internal:9200",
        "allowed_origins": ["https://app.internal.example"],
    }
    values.update(overrides)
    return Settings(**values)


def test_valid_production_configuration_passes() -> None:
    validate_production_config(production_settings())


@pytest.mark.parametrize(
    "override",
    [
        {"minio_secure": False},
        {"rate_limit_enabled": False},
        {"otel_tracing_enabled": False},
        {"audit_hash_secret": "short"},
        {"database_url": "sqlite+aiosqlite:///./local.db"},
        {"database_url": "postgresql+asyncpg://app:secret@localhost:5432/goanalyze"},
        {"allowed_origins": ["http://app.internal.example"]},
        {"allowed_origins": ["*"]},
    ],
)
def test_unsafe_production_configuration_fails_closed(override: dict[str, object]) -> None:
    with pytest.raises(ProductionConfigError):
        validate_production_config(production_settings(**override))


def test_non_production_configuration_is_not_blocked_by_production_rules() -> None:
    validate_production_config(Settings(environment="development"))
