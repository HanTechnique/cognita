import os
import tempfile
from concurrent.futures import Executor
from typing import Dict, List, Optional

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from truefoundry.deploy import trigger_job

from backend.constants import DATA_POINT_FQN_METADATA_KEY, DATA_POINT_HASH_METADATA_KEY
from backend.logger import logger
from backend.modules.dataloaders.loader import get_loader_for_data_source
from backend.modules.metadata_store.client import get_client
from backend.modules.model_gateway.model_gateway import model_gateway
from backend.modules.parsers.parser import get_parser_for_extension
from backend.modules.vector_db.client import VECTOR_STORE_CLIENT
from backend.modules.graph.client import GRAPHRAG_STORE_CLIENT

from backend.settings import settings
from backend.types.core import (
    DataPointVector,
)

def get_data_point_fqn_to_hash_map(
    data_point_vectors: List[DataPointVector],
) -> Dict[str, str]:
    """
    Returns a map of data point fqn to hash
    """
    data_point_fqn_to_hash: Dict[str, str] = {}
    for data_point_vector in data_point_vectors:
        if data_point_vector.data_point_fqn not in data_point_fqn_to_hash:
            data_point_fqn_to_hash[
                data_point_vector.data_point_fqn
            ] = data_point_vector.data_point_hash

    return data_point_fqn_to_hash

