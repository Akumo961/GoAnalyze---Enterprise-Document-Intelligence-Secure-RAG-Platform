"""Validate GoAnalyze production configuration before deployment."""

from gov_platform.config import get_settings
from gov_platform.production_config import validate_startup_configuration

if __name__ == "__main__":
    validate_startup_configuration(get_settings())
    print("Production configuration validation: PASS")
