from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    company_id: str | None = Field(default=None, max_length=100)
    conversation_id: str | None = Field(default=None, max_length=100)


class ChatResponse(BaseModel):
    answer: str
    source: str
    conversation_id: str | None = None
