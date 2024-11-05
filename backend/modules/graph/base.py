from abc import ABC, abstractmethod
from typing import List

from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings
from nano_graphrag import GraphRAG

from backend.constants import DEFAULT_BATCH_SIZE_FOR_VECTOR_STORE
from backend.types.core import DataPointVector


class GraphRAGDB(ABC):
    @abstractmethod
    def create_knowledge(self, knowledge_name: str):
        """
        Create a collection in the vector database
        """
        raise NotImplementedError()

    @abstractmethod
    def upsert_documents(
        self,
        knowledge_name: str,
        documents: List[Document],
    ):
        """
        Upsert documents into the vector database
        """
        raise NotImplementedError()

    @abstractmethod
    def get_knowledges(self) -> List[str]:
        """
        Get all collection names from the vector database
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_knowledge(self, collection_name: str):
        """
        Delete a collection from the vector database
        """
        raise NotImplementedError()

    @abstractmethod
    def get_graph_store(
        self, collection_name: str
    ) -> GraphRAG:
        """
        Get vector store
        """
        raise NotImplementedError()

    @abstractmethod
    def list_data_point_vectors(
        self,
        collection_name: str,
        data_source_fqn: str,
        batch_size: int = DEFAULT_BATCH_SIZE_FOR_VECTOR_STORE,
    ) -> List[DataPointVector]:
        """
        Get vectors from the collection
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_data_point_vectors(
        self,
        collection_name: str,
        data_point_vectors: List[DataPointVector],
        batch_size: int = DEFAULT_BATCH_SIZE_FOR_VECTOR_STORE,
    ):
        """
        Delete vectors from the collection
        """
        raise NotImplementedError()
  