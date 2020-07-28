import abc
import os
from typing import Optional, List
import configparser


def get_config(app) -> None:

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
    @abc.abstractmethod
    def get_config_value(self, key: str) -> Optional[str]:
        """ Get a value for a key given the type config entry

        Args:
            key: the key to look up

        Returns:
            Possible value for the given strategy
        """


class EnvConfig(AbcConfigStrategy):

    def __init__(self) -> None:
        self.configuration = {
            "API_DOMAIN": os.environ.get('ALMA_API_DOMAIN'),
            "API_KEY": os.environ.get('API_KEY')
        }

    def get_config_value(self, key: str) -> Optional[str]:
        return self.configuration.get(key)


class ConfigFile(AbcConfigStrategy):

    def __init__(self, config_file: str) -> None:
        self.config_file = config_file
        config = configparser.ConfigParser()
        config.read(self.config_file)
        self.alma_api = config['ALMA_API']

    def get_config_value(self, key: str) -> Optional[str]:
        return self.alma_api.get(key)


class ConfigLoader:

    def __init__(self, strategy: AbcConfigStrategy) -> None:
        self.strategy = strategy

    def get_config_value(self, key: str):
        return self.strategy.get_config_value(key)
