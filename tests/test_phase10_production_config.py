import pytest

from gov_platform.config import Settings
from gov_platform.production_config import ProductionConfigError, validate_production_config


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
    ],
)
def test_unsafe_production_configuration_fails_closed(override: dict[str, object]) -> None:
    with pytest.raises(ProductionConfigError):
        validate_production_config(production_settings(**override))


def test_non_production_configuration_is_not_blocked_by_production_rules() -> None:
    validate_production_config(Settings(environment="development"))
