"""Validate GoAnalyze production configuration before deployment."""

from gov_platform import config, production_config


if __name__ == "__main__":
    production_config.validate_startup_configuration(config.get_settings())
    print("Production configuration validation: PASS")
