import enum
import uuid
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import (
    Field,
    StringConstraints,
    model_validator,
)
from typing_extensions import Annotated

from backend.constants import FQN_SEPARATOR
from backend.types.core import ConfiguredBaseModel, DataIngestionMode, ParserConfig, BaseDataIngestionRun,DataIngestionRunStatus
from backend.types.core import BaseCollection
class CreateCollectionDataIngestionRun(BaseDataIngestionRun):
    collection_name: str = Field(
        title="Name of the collection",
    )


class ListCollectionDataIngestionRunsDto(ConfiguredBaseModel):
    collection_name: str = Field(
        title="Name of the collection",
    )
    data_source_fqn: Optional[str] = Field(
        title="Fully qualified name of the data source", default=None
    )



class CollectionDataIngestionRun(BaseDataIngestionRun):
    collection_name: str = Field(
        title="Name of the collection",
    )

    name: str = Field(
        title="Name of the data ingestion run",
    )
    status: Optional[DataIngestionRunStatus] = Field(
        None,
        title="Status of the data ingestion run",
    )


class IngestDataToCollectionDto(ConfiguredBaseModel):
    """
    Configuration to ingest data to collection
    """

    collection_name: str = Field(
        title="Name of the collection",
    )

    data_source_fqn: Optional[str] = Field(
        None,
        title="Fully qualified name of the data source",
    )

    data_ingestion_mode: DataIngestionMode = Field(
        default=DataIngestionMode.INCREMENTAL,
        title="Data ingestion mode for the data ingestion",
    )

    raise_error_on_failure: bool = Field(
        title="Flag to configure weather to raise error on failure or not. Default is True",
        default=True,
    )

    run_as_job: bool = Field(
        title="Flag to configure weather to run the ingestion as a job or not. Default is False",
        default=False,
    )

    batch_size: int = Field(
        title="Batch size for data ingestion",
        default=100,
    )


class AssociateDataSourceWithCollection(ConfiguredBaseModel):
    """
    Configuration to associate data source to collection
    """

    data_source_fqn: str = Field(
        title="Fully qualified name of the data source",
        example="localdir::/app/user_data/report",
    )
    parser_config: Dict[str, ParserConfig] = Field(
        title="Parser configuration for the data transformation",
        default_factory=dict,
        example={
            ".pdf": {
                "name": "UnstructuredIoParser",
                "parameters": {
                    "max_chunk_size": 2000,
                },
            }
        },
    )


class AssociateDataSourceWithCollectionDto(AssociateDataSourceWithCollection):
    """
    Configuration to associate data source to collection
    """

    collection_name: str = Field(
        title="Name of the collection",
    )
    data_source_fqn: str = Field(
        title="Fully qualified name of the data source",
    )
    parser_config: Dict[str, ParserConfig] = Field(
        title="Parser configuration for the data transformation", default_factory=dict
    )


class UnassociateDataSourceWithCollectionDto(ConfiguredBaseModel):
    """
    Configuration to unassociate data source to collection
    """

    collection_name: str = Field(
        title="Name of the collection",
    )
    data_source_fqn: str = Field(
        title="Fully qualified name of the data source",
    )



class CreateCollection(BaseCollection):
    pass



class CreateCollectionDto(CreateCollection):
    associated_data_sources: Optional[List[AssociateDataSourceWithCollection]] = Field(
        None, title="Data sources associated with the collection"
    )