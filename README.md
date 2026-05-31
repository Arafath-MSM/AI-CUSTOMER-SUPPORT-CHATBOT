# AI Customer Support Chatbot

RAG-based SaaS chatbot project for website customer support.

## Current Phase

Step 1: FastAPI backend scaffold.

## Project Layout

```text
backend/
  app/
    api/routes/
    core/
    schemas/
    services/
    main.py
  requirements.txt
  .env.example
```

## Run The Backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
uvicorn app.main:app --reload --app-dir backend
```

To enable live AI answers, create `backend\.env` from `backend\.env.example` and set:

```powershell
OPENAI_API_KEY="your_api_key_here"
OPENAI_MODEL="gpt-5.5"
ADMIN_API_TOKEN="change-this-token"
```

Then open:

- API: `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/api/health`

## RAG MVP Endpoints

- Public: `POST /api/chat` answers with retrieved company context when available.
- Admin: `GET /api/admin/status` checks protected admin configuration.
- Admin: `POST /api/knowledge/text` indexes raw text content.
- Admin: `POST /api/upload` indexes `.txt`, `.md`, `.csv`, `.json`, `.html`, or `.pdf` files.
- Admin: `POST /api/query` retrieves the most relevant knowledge chunks.
- Admin: `DELETE /api/knowledge/{document_id}` deletes a document and its indexed chunks.

Admin endpoints require:

```text
X-Admin-Token: your_admin_token
```

## Website Widget

Demo page:

- `http://127.0.0.1:8000/static/demo/index.html`

Admin dashboard:

- `http://127.0.0.1:8000/static/admin/index.html`

The local development admin token defaults to `dev-admin-token`. Change `ADMIN_API_TOKEN` before deployment.

Embed script:

```html
<script
  src="http://127.0.0.1:8000/static/widget/chatbot.js"
  data-api-base-url="http://127.0.0.1:8000"
  data-company-id="demo-company"
  data-title="Demo Store Support"
></script>
```
