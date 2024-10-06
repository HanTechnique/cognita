PROMPT = "You are an AI assistant specialising in information retrieval. Answer the following question precisely by extracting the relavant information given in the images. Please respone in the same language as the question.\nQuestion: {question}"
QUERY_WITH_GRAPHRAG_STORE_RETRIEVER_SIMILARITY = {
    "collection_name": "finance",
    "query": "Explain key operating metrics of FY20",
    "model_configuration": {
        "name": "openai/gpt-4o-mini",
        "parameters": {"temperature": 0.1, "max_tokens": 1024},
    },
    "prompt_template": PROMPT,
    "retriever_name": "graphragstore",
    "retriever_config": {"search_type": "none", "search_kwargs": {"k": 5}},
    "stream": False,
    "internet_search_enabled": False,
}

QUERY_WITH_GRAPHRAG_STORE_RETRIEVER_PAYLOAD = {
    "summary": "search with graphRAG",
    "description": """
        Requires k in search_kwargs for graphRAG search.""",
    "value": QUERY_WITH_GRAPHRAG_STORE_RETRIEVER_SIMILARITY,
}
#######
