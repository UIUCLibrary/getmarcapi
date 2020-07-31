"""Load configurations for the app."""
import abc
import os
from typing import Optional, List
import configparser


def get_config(app) -> None:
    """Load the app with the correct configurations.

    Args:
        app: App to apply the configurations to

    Returns:
        None

    """
    keys: List[str] = [
        "API_DOMAIN",
        "API_KEY"
    ]
    strategies: List[AbcConfigStrategy] = [
        EnvConfig(),

    ]
    if "GETMARCAPI_SETTINGS" in os.environ:
        config_file = os.environ['GETMARCAPI_SETTINGS']
        if os.path.exists(config_file):
            strategies.append(ConfigFile(config_file))
        else:
            app.logger.warning(f"WARNING: Cannot load settings from "
                               f"GETMARCAPI_SETTINGS environment variable. "
                               f"Cannot locate {config_file}")

    for k in keys:
        if k in app.config and app.config[k] is not None:
            continue

        for strategy in strategies:
            value = ConfigLoader(strategy).get_config_value(k)
            if value is not None:
                app.config[k] = value
                break
        else:
            app.config[k] = None


class AbcConfigStrategy(abc.ABC):
    """Base class for loading configurations."""

    @abc.abstractmethod
    def get_config_value(self, key: str) -> Optional[str]:
        """Get a value for a key given the type config entry.

        Args:
            key: the key to look up.

        Returns:
            Possible value for the given strategy.
        """


class EnvConfig(AbcConfigStrategy):
    """Load app configurations from environment Variables."""

    def __init__(self) -> None:
        """Loads the possible setting from environment variables."""
        self.configuration = {
            "API_DOMAIN": os.environ.get('ALMA_API_DOMAIN'),
            "API_KEY": os.environ.get('API_KEY')
        }

    def get_config_value(self, key: str) -> Optional[str]:
        """Get the value from the environment variable.

        Args:
            key: Configuration key

        Returns:
            Possible value if exists, else returns None

        """
        return self.configuration.get(key)


class ConfigFile(AbcConfigStrategy):
    """Load app configurations from a file."""
    def __init__(self, config_file: str) -> None:
        """Parse a config file for settings.

        Args:
            config_file: path to the config file to use.
        """
        self.config_file = config_file
        config = configparser.ConfigParser()
        config.read(self.config_file)
        self.alma_api = config['ALMA_API']

    def get_config_value(self, key: str) -> Optional[str]:
        """Get the value from the config file.

        Args:
            key: Configuration key

        Returns:
            Possible value if exists, else returns None

        """
        return self.alma_api.get(key)


class ConfigLoader:

    def __init__(self, strategy: AbcConfigStrategy) -> None:
        self.strategy = strategy

    def get_config_value(self, key: str):
        return self.strategy.get_config_value(key)


def check_config(app) -> bool:
    """Check if the app configuration is valid.

    Args:
        app: App in question

    Returns:
        True if valid, else False

    """
    app.logger.debug("Checking API Domain")
    domain = app.config.get('API_DOMAIN')
    if domain is None:
        app.logger.error("Missing domain")
        return False
    app.logger.debug("Checking API key")
    api_key = app.config.get('API_KEY')
    if api_key is None:
        app.logger.error("Missing api key")
    app.logger.info("Correctly configured")
    return True
