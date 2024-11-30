from fastapi import Body, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnableLambda,
    RunnableMap,
    RunnablePassthrough,
)
from fastapi import Depends
from backend.server.auth import get_current_user
from backend.logger import logger
from backend.modules.query_controllers.base import BaseQueryController
from backend.modules.query_controllers.basic.payload import (
    QUERY_WITH_CONTEXTUAL_COMPRESSION_MULTI_QUERY_RETRIEVER_SIMILARITY_PAYLOAD,
    QUERY_WITH_CONTEXTUAL_COMPRESSION_RETRIEVER_PAYLOAD,
    QUERY_WITH_VECTOR_STORE_RETRIEVER_PAYLOAD,
)
from backend.modules.query_controllers.basic.types import ExampleQueryInput
from backend.server.decorators import post, query_controller
from langchain_core.runnables import RunnableMap, RunnablePassthrough
from langchain.retrievers import ContextualCompressionRetriever, MultiQueryRetriever
from langchain.schema.vectorstore import VectorStoreRetriever

EXAMPLES = {
    "vector-store-similarity": QUERY_WITH_VECTOR_STORE_RETRIEVER_PAYLOAD,
    "contextual-compression-similarity": QUERY_WITH_CONTEXTUAL_COMPRESSION_RETRIEVER_PAYLOAD,
    "contextual-compression-multi-query-similarity": QUERY_WITH_CONTEXTUAL_COMPRESSION_MULTI_QUERY_RETRIEVER_SIMILARITY_PAYLOAD,
}

from typing import Dict, Any

@query_controller("/basic-rag")
class BasicRAGQueryController(BaseQueryController):
    @post("/answer")
    async def answer(
        self,
        user: dict = Depends(get_current_user),
        request: ExampleQueryInput = Body(
            openapi_examples=EXAMPLES,
        ),
    ):
        """
        Sample answer method to answer the question using the context from the collection
        """
        try:
            # Get the vector store
            vector_store = await self._get_vector_store(user, request.collection_name)

            # Create the QA prompt template
            QA_PROMPT = self._get_prompt_template(
                input_variables=["context", "question"],
                template=request.prompt_template,
            )

            # Get the LLM
            llm = self._get_llm(request.model_configuration, request.stream)

            print("About to get retriever...")  # New debug print
            # Get retriever
            retriever = await self._get_retriever(
                vector_store=vector_store,
                retriever_name=request.retriever_name,
                retriever_config=request.retriever_config,
            )
            try:
                retrieved_docs = await retriever.aget_relevant_documents(request.query)
                print(retrieved_docs)
            except Exception as e:
                logger.error(f"Error retrieving documents: {e}")
                raise
            # Define process_and_extend_docs function
            def process_and_extend_docs(inputs: Dict[str, Any]) -> Dict[str, Any]:
                """Formats existing docs and appends knowledge documents."""
                docs = inputs["context"]
                formatted_docs = self._format_docs(docs)
                #  Update prompt with formatted docs and original question
                updated_prompt = QA_PROMPT.format(
                    context=formatted_docs, question=inputs["question"]
                )  # Pass formatted_docs to the prompt

                return {
                    "prompt": updated_prompt, # Return the formatted prompt
                }

            # Update chain to pass a dictionary input
            rag_chain = (RunnableMap(
                    {"context": retriever, "question": RunnablePassthrough()}
                ) | process_and_extend_docs | llm | StrOutputParser()
            )


            # If internet search is enabled, modify the chain
            if request.internet_search_enabled:
                # Define a function for internet search
                def internet_search(inputs: Dict[str, Any]) -> Dict[str, Any]:
                    return self._internet_search(inputs)

                internet_search_runnable = RunnableLambda(internet_search)
                rag_chain = rag_chain | internet_search_runnable

            # Prepare the input
            chain_input = {"question": request.query}

            if request.stream:
                return StreamingResponse(
                    self._sse_wrap(
                        self._stream_answer(rag_chain, chain_input),
                    ),
                    media_type="text/event-stream",
                )
            else:
                output = await rag_chain.ainvoke(chain_input)
                return {
                    "answer": output,
                    "docs": [],  # Adjust if you want to return documents
                }

        except HTTPException as exp:
            raise exp
        except Exception as exp:
            logger.exception(exp)
            raise HTTPException(status_code=500, detail=str(exp))
