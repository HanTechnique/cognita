from backend.modules.graph.base import GraphRAGDB
from backend.modules.graph.nanographrag import NanoGraphRAG
from backend.types.core import VectorDBConfig

SUPPORTED_VECTOR_DBS = {
    "nanographrag": NanoGraphRAG,
}


def get_graph_db_client(config: VectorDBConfig) -> GraphRAGDB:
    if config.provider in SUPPORTED_VECTOR_DBS:
        return SUPPORTED_VECTOR_DBS[config.provider](config=config)
    else:
        raise ValueError(f"Unknown vector db provider: {config.provider}")
