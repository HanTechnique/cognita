import asyncio

import async_timeout
from fastapi import Body, HTTPException, Depends
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from backend.modules.graph.client import GRAPHRAG_STORE_CLIENT
from langchain.docstore.document import Document

from backend.logger import logger
from backend.modules.query_controllers.base import BaseQueryController
from backend.modules.query_controllers.multimodal.payload import (
    PROMPT,
    QUERY_WITH_CONTEXTUAL_COMPRESSION_MULTI_QUERY_RETRIEVER_SIMILARITY_PAYLOAD,
    QUERY_WITH_CONTEXTUAL_COMPRESSION_RETRIEVER_PAYLOAD,
    QUERY_WITH_VECTOR_STORE_RETRIEVER_PAYLOAD,
)
from backend.modules.query_controllers.graph.types import GraphRAGQueryInput
from backend.modules.query_controllers.types import GENERATION_TIMEOUT_SEC, Answer, Docs
from backend.server.decorators import post, query_controller
from langsmith import traceable
from backend.server.auth import get_current_user

@query_controller("/graph-rag")
class GraphRAGQueryController(BaseQueryController):
    @traceable
    @post("/answer")
    async def answer(
        self,        
        user: dict = Depends(get_current_user),
        request: GraphRAGQueryInput = Body(),
    ):
        """
        Sample answer method to answer the question using the context from the collection
        """
        import asyncio
        import nest_asyncio
        import uvloop

        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
        nest_asyncio.apply()

        try:
            knowledge_graph = GRAPHRAG_STORE_CLIENT.get_graph_store(
                knowledge_name=request.knowledge_name,
            )
            knowledge_response = knowledge_graph.query(request.query)
            document = Document(
                page_content=knowledge_response,
                metadata={"_data_point_fqn": "knowledge::" + request.knowledge_name},
            )

            return {
                "answer": knowledge_response,
                "docs": [document],
            }

        except HTTPException as exp:
            raise exp
        except Exception as exp:
            logger.exception(exp)
            raise HTTPException(status_code=500, detail=str(exp))
