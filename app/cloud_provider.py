import importlib
from abc import ABCMeta, abstractmethod
from functools import lru_cache
from pathlib import Path
from typing import List

import yaml
from pydantic import BaseModel

from config.settings import settings


class BaseCloudProvider(metaclass=ABCMeta):
    """Interface for a cloud provider"""
    name: str = None
    """Provider name in providers.yml config"""

    @abstractmethod
    def upload(self, local_path: Path) -> str:
        """
        Uploads a file by given path to a remote cloud
        :param local_path: path of file to be uploaded
        :return: remote path of uploaded file
        """

    def __repr__(self):
        return f'<{self.__class__.__name__} name={self.name}>'


class ProviderConfig(BaseModel):
    name: str
    import_name: str
    init_kwargs: dict


@lru_cache
def get_provider_configs() -> List[ProviderConfig]:
    """Loads YAML provider config into collection of ProviderConfig objects"""
    with settings.providers_config_path.open() as f:
        return [ProviderConfig(**record) for record in yaml.load(f, yaml.Loader)]


def create_provider(provider_config: ProviderConfig) -> BaseCloudProvider:
    """Given ProviderConfig, loads and returns a Provider instance"""
    module_name, class_name = provider_config.import_name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    ProviderClass = getattr(module, class_name)

    if not issubclass(ProviderClass, BaseCloudProvider):
        raise NotImplementedError(f'{ProviderClass} should subclass {BaseCloudProvider}')

    # init_kwargs should comply with __init__ signature of corresponding class
    provider = ProviderClass(**provider_config.init_kwargs)
    provider.name = provider_config.name
    return provider


def providers():
    """Yields providers, configured in providers.yml"""
    for provider_config in get_provider_configs():
        yield create_provider(provider_config)
