from backend.modules.vector_db.base import BaseVectorDB
from nano_graphrag import GraphRAG, QueryParam
import os
import shutil
from backend.modules.vector_db.milvuslitestorage import MilvusLiteStorage
from backend.types import DataPointVector

def get_subdirectories(working_dir: str) -> list[str]:
    """Returns a list of subdirectory names within the given working directory."""
    return [
        f.name for f in os.scandir(working_dir) if f.is_dir()
    ]

class NanoGraphRAG(BaseVectorDB):
    def __init__(self, config):
        self.config = config

    def create_collection(self, collection_name: str, embeddings):
        """Creates a collection directory if it doesn't exist."""
        collection_path = os.path.join(self.config.config['working_dir'], collection_name)
        if not os.path.exists(collection_path):
            try:
                os.makedirs(collection_path)
                print(f"Created collection: {collection_name}")
            except OSError as e:
                print(f"Error creating collection {collection_name}: {e}")
        else:
            print(f"Collection already exists: {collection_name}")

        if not os.path.exists(collection_path+"_milvus"):
            try:
                os.makedirs(collection_path+"_milvus")
                print(f"Created collection: {collection_name}_milvus")
            except OSError as e:
                print(f"Error creating collection {collection_name}_milvus: {e}")
        else:
            print(f"Collection already exists: {collection_name}_milvus")

    def upsert_documents(
        self,
        collection_name: str,
        documents,
        embeddings,
        incremental: bool = True,
    ):
        import nest_asyncio

        nest_asyncio.apply()

        graph_func = GraphRAG(working_dir= self.config.config['working_dir']+"/"+collection_name,
            enable_llm_cache=True,
            vector_db_storage_cls=MilvusLiteStorage,)

        page_contents = [document.page_content for document in documents]
        graph_func.insert(page_contents)

    def get_collections(self) -> list[str]:

        return get_subdirectories(self.config.config['working_dir'])

    def delete_collection(self, collection_name: str):
        """Deletes the collection directory, effectively removing the collection."""
        collection_path = os.path.join(self.config.config['working_dir'], collection_name)
        if os.path.exists(collection_path):
            try:
                shutil.rmtree(collection_path)
                print(f"Deleted collection: {collection_name}")
            except OSError as e:
                print(f"Error deleting collection {collection_name}: {e}")
        else:
            print(f"Collection not found: {collection_name}")

    def get_vector_store(self, collection_name: str, embeddings):
        graph_func = GraphRAG(working_dir= self.config.config['working_dir']+"/"+collection_name,
            enable_llm_cache=True,
            vector_db_storage_cls=MilvusLiteStorage,)
        return graph_func


    def get_vector_client(self):
        pass  # Not applicable to NanoGraphRAG

    def list_data_point_vectors(
        self, collection_name: str, data_source_fqn: str, batch_size: int = 1000
    ):
        """
        Lists all data point vectors for the specified collection.
        Returns an empty list if the collection does not exist.
        """
        collection_path = os.path.join(self.config.config['working_dir'], collection_name)
        if not os.path.exists(collection_path) or not os.listdir(collection_path):
            print(f"Collection not found: {collection_name}, returning empty list.")
            return []  # Return empty list if collection doesn't exist

        import nest_asyncio
        nest_asyncio.apply()

        graph_func = GraphRAG(working_dir= self.config.config['working_dir']+"/"+collection_name,
            enable_llm_cache=True,
            vector_db_storage_cls=MilvusLiteStorage,)
        
        all_docs = graph_func.query("", param=QueryParam(mode="local", top_k=1000))

        data_point_vectors = []
        for vector in all_docs:
            print(vector)
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
        collection_name: str,
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
