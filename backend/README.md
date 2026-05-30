# Backend

FastAPI backend for the AI Customer Support Chatbot SaaS project.

## Endpoints

- `GET /api/health` checks service status.
- `POST /api/chat` accepts a user message and returns a placeholder assistant response.

The chat endpoint is intentionally local and deterministic in Step 1. GPT/RAG integration comes next.

## Run

```powershell
uvicorn app.main:app --reload --app-dir backend
```

