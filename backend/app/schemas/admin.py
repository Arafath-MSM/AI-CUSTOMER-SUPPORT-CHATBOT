from pydantic import BaseModel


class AdminStatusResponse(BaseModel):
    status: str
    app_env: str
    openai_configured: bool 
    chat_model: str
    embedding_model: str
    rag_top_k: int
    rag_chunk_size: int
    rag_chunk_overlap: int
