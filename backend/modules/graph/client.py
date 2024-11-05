from backend.modules.graph import get_graph_db_client
from backend.settings import settings

GRAPHRAG_STORE_CLIENT = get_graph_db_client(config=settings.GRAPHRAG_CONFIG)