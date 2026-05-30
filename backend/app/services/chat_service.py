from openai import APIError, APITimeoutError, AsyncOpenAI

from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse


SYSTEM_INSTRUCTIONS = """
You are a helpful customer support assistant for a business website.
Answer clearly and professionally.
If the user asks for company-specific policy details that are not provided, say that the knowledge base has not been connected yet.
Do not invent refund, delivery, pricing, legal, or account information.
"""


class ChatServiceError(Exception):
    """Raised when the LLM provider cannot produce a response."""


async def generate_support_reply(request: ChatRequest) -> ChatResponse:
    message = request.message.strip()

    if not settings.has_openai_api_key:
        return _generate_local_reply(request, message)

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
                            "text": message,
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
        source="openai-responses-api",
        conversation_id=request.conversation_id,
        model=settings.openai_model,
    )


def _generate_local_reply(request: ChatRequest, message: str) -> ChatResponse:
    answer = (
        "Step 2 backend is ready for LLM responses. "
        "Set OPENAI_API_KEY in backend/.env to enable live AI answers. "
        "In Step 3, this endpoint will answer from uploaded company data using RAG. "
        f"You asked: {message}"
    )

    return ChatResponse(
        answer=answer,
        source="local-dev-fallback",
        conversation_id=request.conversation_id,
        model=None,
    )
