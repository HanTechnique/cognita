from backend.modules.graph.base import GraphRAGDB
from nano_graphrag import GraphRAG, QueryParam
import os
import shutil
from backend.modules.graph.milvuslitestorage import MilvusLiteStorage
from backend.types.core import DataPointVector

def get_subdirectories(working_dir: str) -> list[str]:
    """Returns a list of subdirectory names within the given working directory."""
    return [
        f.name for f in os.scandir(working_dir) if f.is_dir()
    ]

class NanoGraphRAG(GraphRAGDB):
    def __init__(self, config):
        self.config = config

    def create_knowledge(self, knowledge_name: str):
        """Creates a knowledge directory if it doesn't exist."""
        knowledge_path = os.path.join(self.config.config['working_dir'], knowledge_name)
        if not os.path.exists(knowledge_path):
            try:
                os.makedirs(knowledge_path)
                print(f"Created knowledge: {knowledge_name}")
            except OSError as e:
                print(f"Error creating knowledge {knowledge_name}: {e}")
        else:
            print(f"Knowledge already exists: {knowledge_name}")

        if not os.path.exists(knowledge_path+"_milvus"):
            try:
                os.makedirs(knowledge_path+"_milvus")
                print(f"Created knowledge: {knowledge_name}_milvus")
            except OSError as e:
                print(f"Error creating knowledge {knowledge_name}_milvus: {e}")
        else:
            print(f"Knowledge already exists: {knowledge_name}_milvus")

    def upsert_documents(
        self,
        knowledge_name: str,
        documents,
    ):
        import nest_asyncio

        nest_asyncio.apply()

        graph_func = GraphRAG(working_dir= self.config.config['working_dir']+"/"+knowledge_name,
            enable_llm_cache=True,
            vector_db_storage_cls=MilvusLiteStorage,)

        page_contents = [document.page_content for document in documents]
        graph_func.insert(page_contents)

    def get_knowledges(self) -> list[str]:

        return get_subdirectories(self.config.config['working_dir'])

    def delete_knowledge(self, knowledge_name: str):
        """Deletes the knowledge directory, effectively removing the knowledge."""
        knowledge_path = os.path.join(self.config.config['working_dir'], knowledge_name)
        if os.path.exists(knowledge_path):
            try:
                shutil.rmtree(knowledge_path)
                print(f"Deleted knowledge: {knowledge_name}")
            except OSError as e:
                print(f"Error deleting knowledge {knowledge_name}: {e}")
        else:
            print(f"Knowledge not found: {knowledge_name}")

    def get_graph_store(self, knowledge_name: str):
        graph_func = GraphRAG(working_dir= self.config.config['working_dir']+"/"+knowledge_name,
            enable_llm_cache=True,
            vector_db_storage_cls=MilvusLiteStorage,)
        return graph_func

    def list_data_point_vectors(
        self, knowledge_name: str, data_source_fqn: str, batch_size: int = 1000
    ):
        """
        Lists all data point vectors for the specified knowledge.
        Returns an empty list if the knowledge does not exist.
        """
        knowledge_path = os.path.join(self.config.config['working_dir'], knowledge_name)
        if not os.path.exists(knowledge_path) or not os.listdir(knowledge_path):
            print(f"Collection not found: {knowledge_name}, returning empty list.")
            return []  # Return empty list if knowledge doesn't exist

        import nest_asyncio
        nest_asyncio.apply()

        graph_func = GraphRAG(working_dir= self.config.config['working_dir']+"/"+knowledge_name,
            enable_llm_cache=True,
            vector_db_storage_cls=MilvusLiteStorage,)
        
        all_docs = graph_func.query("", param=QueryParam(mode="local", top_k=1000))

        data_point_vectors = []
        for vector in all_docs:
            data_point_vectors.append(
                DataPointVector(
                    data_point_vector_id=vector['id'],
                    data_point_fqn=vector['text'],
                    data_point_hash='not available' #TODO: get hash of text
                )
            )
        return data_point_vectors


    def delete_data_point_vectors(
        self,
        knowledge_name: str,
        data_point_vectors,
        batch_size: int = 100,
    ):
        pass  # Not applicable to NanoGraphRAG

    def query(self, query: str, mode: str = "local"):
        import nest_asyncio

        nest_asyncio.apply()

        if mode == "local":
            return self.graph_func.query(query, param=QueryParam(mode="local"))
        else:
            return self.graph_func.query(query)
