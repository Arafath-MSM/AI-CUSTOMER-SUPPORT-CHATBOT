from fastapi import APIRouter, Depends

from app.api.dependencies import require_admin_token
from app.core.config import settings
from app.schemas.admin import AdminStatusResponse

router = APIRouter(dependencies=[Depends(require_admin_token)])

 
@router.get("/admin/status", response_model=AdminStatusResponse)
async def admin_status() -> AdminStatusResponse:
    return AdminStatusResponse(
        status="ok",
        app_env=settings.app_env,
        openai_configured=settings.has_openai_api_key,
        chat_model=settings.openai_model,
        embedding_model=settings.openai_embedding_model,
        rag_top_k=settings.rag_top_k,
        rag_chunk_size=settings.rag_chunk_size,
        rag_chunk_overlap=settings.rag_chunk_overlap,
    )
