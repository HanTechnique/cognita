from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from backend.types.core import (
    CreateDataSource,
    DataSource,
    MetadataStoreConfig,
    RagApplication,
    RagApplicationDto,
)


class BaseMetadataStore(ABC):
    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    async def aconnect(cls, **kwargs) -> "BaseMetadataStore":
        return cls(**kwargs)


    #####
    # DATA SOURCE
    #####

    @abstractmethod
    async def aget_data_source_from_fqn(self, fqn: str) -> Optional[DataSource]:
        """
        Get a data source from the metadata store by fqn
        """
        raise NotImplementedError()

    @abstractmethod
    async def acreate_data_source(self, data_source: CreateDataSource) -> DataSource:
        """
        Create a data source in the metadata store
        """
        raise NotImplementedError()

    @abstractmethod
    async def aget_data_sources(self) -> List[DataSource]:
        """
        Get all data sources from the metadata store
        """
        raise NotImplementedError()


    @abstractmethod
    async def alist_data_sources(
        self,
    ) -> List[Dict[str, str]]:
        """
        List all data source names from metadata store
        """
        raise NotImplementedError()

    @abstractmethod
    async def adelete_data_source_by_user(self, user: dict, data_source_fqn: str):
        """
        Delete a data source from the metadata store
        """
        raise NotImplementedError()

    
    ####
    # RAG APPLICATIONS
    ####

    @abstractmethod
    async def aget_rag_app(self, app_name: str) -> Optional[RagApplicationDto]:
        """
        Get a RAG application from the metadata store by name
        """
        raise NotImplementedError()

    @abstractmethod
    async def acreate_rag_app(self, app: RagApplication) -> RagApplicationDto:
        """
        create a RAG application in the metadata store
        """
        raise NotImplementedError()

    @abstractmethod
    async def alist_rag_apps(self) -> List[str]:
        """
        List all RAG application names from metadata store
        """
        raise NotImplementedError()

    @abstractmethod
    async def adelete_rag_app(self, app_name: str):
        """
        Delete a RAG application from the metadata store
        """
        raise NotImplementedError()


# A global registry to store all available metadata store.
METADATA_STORE_REGISTRY = {}


def register_metadata_store(provider: str, cls):
    """
    Registers all the available metadata store.

    Args:
        provider: The type of the metadata store to be registered.
        cls: The metadata store class to be registered.

    Returns:
        None
    """
    global METADATA_STORE_REGISTRY
    if provider in METADATA_STORE_REGISTRY:
        raise ValueError(
            f"Error while registering class {cls.__name__}, "
            f"key {provider} is already taken by {METADATA_STORE_REGISTRY[provider].__name__}"
        )
    METADATA_STORE_REGISTRY[provider] = cls


async def get_metadata_store_client(
    config: MetadataStoreConfig,
) -> BaseMetadataStore:
    if config.provider in METADATA_STORE_REGISTRY:
        kwargs = config.config
        return await METADATA_STORE_REGISTRY[config.provider].aconnect(**kwargs)
    else:
        raise ValueError(f"Unknown metadata store type: {config.provider}")
