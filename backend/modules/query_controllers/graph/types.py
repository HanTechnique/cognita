
from pydantic import (
    BaseModel,
    Field,
)

class GraphRAGQueryInput(BaseModel):
    knowledge_name: str = Field(
        default=None,
        title="Collection name on which to search",
    )

    query: str = Field(title="Question to search for")
