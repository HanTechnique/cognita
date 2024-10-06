import asyncio

import async_timeout
from fastapi import Body, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from backend.logger import logger
from backend.modules.query_controllers.base import BaseQueryController
from backend.modules.query_controllers.graph.payload import (
    PROMPT,
    QUERY_WITH_GRAPHRAG_STORE_RETRIEVER_PAYLOAD
)
from backend.modules.query_controllers.multimodal.types import MultiModalQueryInput
from backend.modules.query_controllers.types import GENERATION_TIMEOUT_SEC, Answer, Docs
from backend.server.decorators import post, query_controller
from langsmith import traceable
from backend.modules.query_controllers.types import Context
from nano_graphrag import GraphRAG
from langchain_core.runnables import RunnableMap

EXAMPLES = {
    "graph-rag": QUERY_WITH_GRAPHRAG_STORE_RETRIEVER_PAYLOAD,
}


@query_controller("/graph-rag")
class GraphRAGQueryController(BaseQueryController):
    async def _stream_vlm_answer(self, llm, message_payload, docs):
        try:
            async with async_timeout.timeout(GENERATION_TIMEOUT_SEC):
                yield Docs(content=self._cleanup_metadata(docs))
                async for chunk in llm.astream(message_payload):
                    yield Answer(content=chunk.content)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Stream timed out")

    def _generate_payload_for_vlm(self, prompt: str, images_set: set):
        content = [
            {
                "type": "text",
                "text": prompt,
            }
        ]

        for b64_image in images_set:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{b64_image}",
                        "detail": "high",
                    },
                }
            )
        return [HumanMessage(content=content)]
    
    @traceable
    @post("/answer")
    async def answer(
        self,
        request: MultiModalQueryInput = Body(
            openapi_examples=EXAMPLES,
        ),
    ):
        """
        Sample answer method to answer the question using the context from the collection
        """
        try:
            # Get the vector store
            retriever = await self._get_vector_store(request.collection_name)

            # Define a coroutine function for GraphRAG retrieval
            async def graphrag_retrieval(question: str) -> Context:
                # Get the current running event loop
                loop = asyncio.get_running_loop()
                # Run the GraphRAG query in the current event loop
                docs = await loop.run_in_executor(None, retriever.query, question)
                return Context(content=docs)


            # Use RunnableMap for asynchronous retrieval with GraphRAG
            setup_and_retrieval = RunnableMap(
                input_to_output_fn=graphrag_retrieval,
                # You can add other runnables in parallel if needed
            )
            context = await setup_and_retrieval.ainvoke(request.query)
            return {
                "answer": context['input_to_output_fn'].content,
                "docs": [],
            }

        except HTTPException as exp:
            raise exp
        except Exception as exp:
            logger.exception(exp)
            raise HTTPException(status_code=500, detail=str(exp))
