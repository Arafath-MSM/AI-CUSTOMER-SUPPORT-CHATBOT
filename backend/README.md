# Backend

FastAPI backend for the AI Customer Support Chatbot SaaS project.

## Endpoints

- `GET /api/health` checks service status.
- `POST /api/chat` accepts a user message and returns an LLM response when `OPENAI_API_KEY` is configured.
- `POST /api/knowledge/text` indexes raw text into the local knowledge base.
- `POST /api/upload` indexes supported text/PDF files.
- `POST /api/query` retrieves top matching knowledge chunks.
- `GET /api/knowledge?company_id=default` lists indexed documents.
- `GET /static/widget/chatbot.js` serves the embeddable website widget.
- `GET /static/demo/index.html` serves a demo storefront using the widget.

Without `OPENAI_API_KEY`, the chat endpoint returns a local development fallback so the API remains testable.

## Environment

Copy `.env.example` to `.env` and set:

```powershell
OPENAI_API_KEY="your_api_key_here"
OPENAI_MODEL="gpt-5.5"
OPENAI_EMBEDDING_MODEL="text-embedding-3-small"
```

## Run

```powershell
uvicorn app.main:app --reload --app-dir backend
```
