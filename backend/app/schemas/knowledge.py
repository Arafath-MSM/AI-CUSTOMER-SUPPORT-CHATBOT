from pydantic import BaseModel, Field


class KnowledgeTextUploadRequest(BaseModel):
    company_id: str = Field(default="default", min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)


class KnowledgeUploadResponse(BaseModel):
    document_id: str
    company_id: str
    title: str
    chunks_indexed: int
    embedding_model: str


class KnowledgeQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    company_id: str = Field(default="default", min_length=1, max_length=100)
    top_k: int | None = Field(default=None, ge=1, le=10)


class KnowledgeMatch(BaseModel):
    document_id: str
    title: str
    chunk_index: int
    score: float
    text: str


class KnowledgeQueryResponse(BaseModel):
    query: str
    company_id: str
    matches: list[KnowledgeMatch]
    embedding_model: str


class KnowledgeDocumentSummary(BaseModel):
    document_id: str
    company_id: str
    title: str
    chunks_indexed: int
    created_at: str


class KnowledgeSummaryResponse(BaseModel):
    company_id: str
    documents: list[KnowledgeDocumentSummary]
    total_chunks: int


class CompanySummary(BaseModel):
    company_id: str
    documents_count: int
    total_chunks: int
    latest_document_at: str | None = None


class CompanyListResponse(BaseModel):
    companies: list[CompanySummary]


class KnowledgeDeleteResponse(BaseModel):
    document_id: str
    deleted: bool
    chunks_deleted: int
