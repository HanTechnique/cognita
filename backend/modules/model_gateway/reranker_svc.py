from typing import Optional, Sequence

import requests
from langchain.callbacks.manager import Callbacks
from langchain.docstore.document import Document
from langchain.retrievers.document_compressors.base import BaseDocumentCompressor

from backend.logger import logger
import cohere


# Reranking Service using Infinity API
class InfinityRerankerSvc(BaseDocumentCompressor):
    """
    Reranker Service that uses Infinity API
    GitHub: https://github.com/michaelfeil/infinity
    """

    model: str
    top_k: int
    base_url: str
    api_key: Optional[str] = None

    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        """Compress retrieved documents given the query context."""
        docs = [doc.page_content for doc in documents]

        payload = {
            "query": query,
            "documents": docs,
            "return_documents": False,
            "model": self.model,
        }

        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        reranked_docs = requests.post(
            self.base_url.rstrip("/") + "/rerank", headers=headers, json=payload
        ).json()

        """
        reranked_docs =
        {
            "results": [
                {
                    "relevance_score": 0.039407938718795776,
                    "index": 0,
                },
                {
                    "relevance_score": 0.03979039937257767,
                    "index": 1,
                },
                {
                    "relevance_score": 0.1976623684167862,
                    "index": 2,
                }
            ]
        }
        """

        logger.info(f"Reranked documents: {reranked_docs}")

        # Sort the results by relevance_score in descending order
        sorted_results = sorted(
            reranked_docs.get("results"),
            key=lambda x: x["relevance_score"],
            reverse=True,
        )

        # Extract the indices from the sorted results
        sorted_indices = [result["index"] for result in sorted_results][: self.top_k]
        relevance_scores = [result["relevance_score"] for result in sorted_results][
            : self.top_k
        ]

        # sort documents based on the sorted indices
        ranked_documents = list()
        for idx, index in enumerate(sorted_indices):
            # show relevance scores upto 2 decimal places
            documents[index].metadata["relevance_score"] = relevance_scores[idx]
            ranked_documents.append(documents[index])
        return ranked_documents
# Reranking Service using Cohere API
class CohereRerankerSvc(BaseDocumentCompressor):
    """
    Reranker Service that uses Cohere API
    GitHub: https://github.com/cohere-ai/cohere-python
    """

    model: str
    top_k: int
    api_key: Optional[str] = None

    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        """Compress retrieved documents given the query context."""
        docs = [doc.page_content for doc in documents]

        co = cohere.Client(self.api_key)
        response = co.rerank(
            query=query,
            documents=docs,
            model=self.model,
            top_n=self.top_k,
        )

        logger.info(f"Reranked documents: {response}")

        # sort documents based on the reranked results
        ranked_documents = list()
        for result in response.results:
            # show relevance scores upto 2 decimal places
            documents[result.index].metadata["relevance_score"] = round(result.relevance_score, 2)
            ranked_documents.append(documents[result.index])
        return ranked_documents