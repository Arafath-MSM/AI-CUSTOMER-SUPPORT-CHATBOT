from app.schemas.chat import ChatRequest, ChatResponse


def generate_support_reply(request: ChatRequest) -> ChatResponse:
    message = request.message.strip()
    answer = (
        "Step 1 backend is running. "
        "In Step 2, this endpoint will call an LLM; in Step 3, it will answer from uploaded company data. "
        f"You asked: {message}"
    )

    return ChatResponse(
        answer=answer,
        source="local-placeholder",
        conversation_id=request.conversation_id,
    )
