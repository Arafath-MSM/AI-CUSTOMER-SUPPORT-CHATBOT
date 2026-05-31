from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pypdf import PdfReader

from app.api.dependencies import require_admin_token
from app.schemas.knowledge import (
    KnowledgeDeleteResponse,
    KnowledgeQueryRequest,
    KnowledgeQueryResponse,
    KnowledgeSummaryResponse,
    KnowledgeTextUploadRequest,
    KnowledgeUploadResponse,
)
from app.services.knowledge_service import (
    KnowledgeBaseError,
    delete_knowledge_document,
    index_text_document,
    list_knowledge_documents,
    query_knowledge_base,
)

router = APIRouter(dependencies=[Depends(require_admin_token)])


@router.post("/knowledge/text", response_model=KnowledgeUploadResponse)
async def upload_text_document(
    request: KnowledgeTextUploadRequest,
) -> KnowledgeUploadResponse:
    try:
        return await index_text_document(
            company_id=request.company_id,
            title=request.title,
            content=request.content,
        )
    except KnowledgeBaseError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/upload", response_model=KnowledgeUploadResponse)
async def upload_file_document(
    company_id: str = Form(default="default"),
    title: str | None = Form(default=None),
    file: UploadFile = File(...),
) -> KnowledgeUploadResponse:
    contents = await file.read()
    document_title = title or file.filename or "Uploaded document"
    text = _extract_text(file.filename or document_title, contents)

    try:
        return await index_text_document(
            company_id=company_id,
            title=document_title,
            content=text,
        )
    except KnowledgeBaseError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/query", response_model=KnowledgeQueryResponse)
async def query_knowledge(
    request: KnowledgeQueryRequest,
) -> KnowledgeQueryResponse:
    try:
        return await query_knowledge_base(
            company_id=request.company_id,
            query=request.query,
            top_k=request.top_k,
        )
    except KnowledgeBaseError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.get("/knowledge", response_model=KnowledgeSummaryResponse)
async def knowledge_summary(
    company_id: str = Query(default="default", min_length=1, max_length=100),
) -> KnowledgeSummaryResponse:
    return list_knowledge_documents(company_id)


@router.delete("/knowledge/{document_id}", response_model=KnowledgeDeleteResponse)
async def delete_knowledge(
    document_id: str,
) -> KnowledgeDeleteResponse:
    result = delete_knowledge_document(document_id)
    if not result.deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge document not found.",
        )

    return result


def _extract_text(filename: str, contents: bytes) -> str:
    suffix = Path(filename).suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf_text(contents)

    if suffix in {".txt", ".md", ".csv", ".json", ".html", ".htm"}:
        return contents.decode("utf-8", errors="ignore")

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported file type. Upload .txt, .md, .csv, .json, .html, or .pdf.",
    )


def _extract_pdf_text(contents: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(contents))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from PDF.",
        ) from exc
