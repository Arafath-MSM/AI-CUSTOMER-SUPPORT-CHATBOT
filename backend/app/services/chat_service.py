from openai import APIError, APITimeoutError, AsyncOpenAI

from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse, ChatSource
from app.services.knowledge_service import KnowledgeBaseError, query_knowledge_base


SYSTEM_INSTRUCTIONS = """
You are a helpful customer support assistant for a business website.
Answer clearly and professionally.
Use the provided company knowledge base context when it is available.
If the context does not contain the answer, say that the knowledge base does not contain that information yet.
Do not invent refund, delivery, pricing, legal, or account information.
"""


class ChatServiceError(Exception):
    """Raised when the LLM provider cannot produce a response."""


async def generate_support_reply(request: ChatRequest) -> ChatResponse:
    message = request.message.strip()
    company_id = request.company_id or "default"
    knowledge_context = await _retrieve_context(company_id=company_id, message=message)
    sources = [
        ChatSource(
            document_id=match.document_id,
            title=match.title,
            chunk_index=match.chunk_index,
            score=match.score,
        )
        for match in knowledge_context.matches
    ]

    if not settings.has_openai_api_key:
        return _generate_local_reply(request, message, sources)

    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        timeout=settings.openai_timeout_seconds,
    )

    try:
        response = await client.responses.create(
            model=settings.openai_model,
            instructions=SYSTEM_INSTRUCTIONS,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": _build_rag_prompt(
                                company_id=company_id,
                                message=message,
                                context=knowledge_context.matches,
                            ),
                        }
                    ],
                }
            ],
            max_output_tokens=settings.openai_max_output_tokens,
        )
    except (APIError, APITimeoutError) as exc:
        raise ChatServiceError("LLM provider request failed.") from exc

    answer = response.output_text.strip()
    if not answer:
        raise ChatServiceError("LLM provider returned an empty response.")

    return ChatResponse(
        answer=answer,
        source="openai-rag-responses-api" if sources else "openai-responses-api",
        conversation_id=request.conversation_id,
        model=settings.openai_model,
        sources=sources,
    )


async def _retrieve_context(company_id: str, message: str):
    try:
        return await query_knowledge_base(
            company_id=company_id,
            query=message,
            top_k=settings.rag_top_k,
        )
    except KnowledgeBaseError as exc:
        raise ChatServiceError("Knowledge base query failed.") from exc


def _build_rag_prompt(company_id: str, message: str, context: list) -> str:
    if context:
        context_text = "\n\n".join(
            f"[{index}] {match.title} (chunk {match.chunk_index}, score {match.score})\n{match.text}"
            for index, match in enumerate(context, start=1)
        )
    else:
        context_text = "No relevant knowledge base context was found."

    return (
        f"Company ID: {company_id}\n\n"
        f"Knowledge base context:\n{context_text}\n\n"
        f"User question:\n{message}"
    )


def _generate_local_reply(
    request: ChatRequest,
    message: str,
    sources: list[ChatSource],
) -> ChatResponse:
    answer = (
        "The backend is ready for RAG chat. "
        "Set OPENAI_API_KEY in backend/.env to enable live AI answers. "
        f"I found {len(sources)} matching knowledge chunks. "
        f"You asked: {message}"
    )

    return ChatResponse(
        answer=answer,
        source="local-dev-fallback",
        conversation_id=request.conversation_id,
        model=None,
        sources=sources,
    )
