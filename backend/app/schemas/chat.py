from pydantic import BaseModel, Field


class ChatSource(BaseModel):
    document_id: str
    title: str
    chunk_index: int
    score: float


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    company_id: str | None = Field(default=None, max_length=100)
    conversation_id: str | None = Field(default=None, max_length=100)


class ChatResponse(BaseModel):
    answer: str
    source: str
    conversation_id: str | None = None
    model: str | None = None
    sources: list[ChatSource] = Field(default_factory=list)
