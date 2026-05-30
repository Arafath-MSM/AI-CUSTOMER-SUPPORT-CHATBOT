# Backend

FastAPI backend for the AI Customer Support Chatbot SaaS project.

## Endpoints

- `GET /api/health` checks service status.
- `POST /api/chat` accepts a user message and returns an LLM response when `OPENAI_API_KEY` is configured.

Without `OPENAI_API_KEY`, the chat endpoint returns a local development fallback so the API remains testable.

## Environment

Copy `.env.example` to `.env` and set:

```powershell
OPENAI_API_KEY="your_api_key_here"
OPENAI_MODEL="gpt-5.5"
```

## Run

```powershell
uvicorn app.main:app --reload --app-dir backend
```
