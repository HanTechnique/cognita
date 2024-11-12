import enum
import uuid
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import (
    Field,
    computed_field,
    model_validator,
)

from backend.constants import FQN_SEPARATOR
from backend.types.core import BaseKnowledge, BaseDataIngestionRun, DataIngestionRunStatus, ConfiguredBaseModel, DataIngestionMode, ParserConfig, AssociatedDataSources

class CreateKnowledgeDataIngestionRun(BaseDataIngestionRun):
    knowledge_name: str = Field(
        title="Name of the knowledge",
    )




class KnowledgeDataIngestionRun(BaseDataIngestionRun):
    knowledge_name: str = Field(
        title="Name of the knowledge",
    )

    name: str = Field(
        title="Name of the data ingestion run",
    )
    status: Optional[DataIngestionRunStatus] = Field(
        None,
        title="Status of the data ingestion run",
    )
class ListKnowledgeDataIngestionRunsDto(ConfiguredBaseModel):
    knowledge_name: str = Field(
        title="Name of the knowledge",
    )
    data_source_fqn: Optional[str] = Field(
        title="Fully qualified name of the data source", default=None
    )


class IngestDataToKnowledgeDto(ConfiguredBaseModel):
    """
    Configuration to ingest data to knowledge
    """

    knowledge_name: str = Field(
        title="Name of the knowledge",
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


class AssociateDataSourceWithKnowledge(ConfiguredBaseModel):
    """
    Configuration to associate data source to knowledge
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


class AssociateDataSourceWithKnowledgeDto(AssociateDataSourceWithKnowledge):
    """
    Configuration to associate data source to knowledge
    """

    knowledge_name: str = Field(
        title="Name of the knowledge",
    )
    data_source_fqn: str = Field(
        title="Fully qualified name of the data source",
    )
    parser_config: Dict[str, ParserConfig] = Field(
        title="Parser configuration for the data transformation", default_factory=dict
    )


class UnassociateDataSourceWithKnowledgeDto(ConfiguredBaseModel):
    """
    Configuration to unassociate data source to knowledge
    """

    knowledge_name: str = Field(
        title="Name of the knowledge",
    )
    data_source_fqn: str = Field(
        title="Fully qualified name of the data source",
    )




class CreateKnowledge(BaseKnowledge):    
    owner_id: str = Field(
        title="Owner of the collection",
    )





class CreateKnowledgeDto(BaseKnowledge):
    associated_data_sources: Optional[List[AssociateDataSourceWithKnowledge]] = Field(
        None, title="Data sources associated with the knowledge"
    )