import abc
import os
from typing import Optional, List
import configparser


def get_config(app) -> None:

    keys: List[str] = [
        "domain",
        "api_key"
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
            app.config[k] = strategy.get_key(k)


class AbcConfigStrategy(abc.ABC):
    @abc.abstractmethod
    def get_key(self, key: str) -> Optional[str]:
        pass


class EnvConfig(AbcConfigStrategy):

    def __init__(self) -> None:
        self.configuration = {
            "domain": os.environ.get('ALMA_DOMAIN'),
            "api_key": os.environ.get('api_key')
        }

    def get_key(self, key: str) -> Optional[str]:
        return self.configuration.get(key)


class ConfigFile(AbcConfigStrategy):

    def __init__(self, config_file: str) -> None:
        self.config_file = config_file
        config = configparser.ConfigParser()
        config.read(self.config_file)
        self.alma_api = config['ALMA_API']

    def get_key(self, key: str) -> Optional[str]:
        return self.alma_api.get(key)


class ConfigLoader:

    def __init__(self, strategy: AbcConfigStrategy) -> None:
        self.strategy = strategy

    def get_key(self, key: str):
        return self.strategy.get_key(key)

