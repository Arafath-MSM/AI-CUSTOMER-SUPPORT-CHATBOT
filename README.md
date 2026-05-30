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

Then open:

- API: `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/api/health`

