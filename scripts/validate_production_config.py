"""Validate GoAnalyze production configuration before deployment."""

from importlib import import_module

if __name__ == "__main__":
    config = import_module("gov_platform.config")
    production_config = import_module("gov_platform.production_config")
    production_config.validate_startup_configuration(config.get_settings())
    print("Production configuration validation: PASS")
