"""Validate GoAnalyze production configuration before deployment."""

# ruff: noqa: I001
# The single standard-library import below is already in canonical order.
# Keep this scoped suppression because the current Ruff/isort resolution flags
# the one-line block while its own suggested fix produces no semantic change.
from importlib import import_module


if __name__ == "__main__":
    config = import_module("gov_platform.config")
    production_config = import_module("gov_platform.production_config")
    production_config.validate_startup_configuration(config.get_settings())
    print("Production configuration validation: PASS")
