# Deployment

This MVP can run as a single FastAPI service. The local JSON knowledge store is mounted as a persistent volume in Docker Compose.

## Required Environment

Create `backend/.env` from `backend/.env.example` and set:

```text
OPENAI_API_KEY=your_openai_key
ADMIN_API_TOKEN=use_a_long_random_token
OPENAI_MODEL=gpt-5.5
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

## Run With Docker Compose

```powershell
docker compose up --build
```

Open:

- API docs: `http://127.0.0.1:8000/docs`
- Admin dashboard: `http://127.0.0.1:8000/static/admin/index.html`
- Demo storefront: `http://127.0.0.1:8000/static/demo/index.html`

## Production Notes

- Change `ADMIN_API_TOKEN` before deployment.
- Keep `backend/.env` out of Git.
- Mount `backend/storage` as a persistent volume if using the local JSON store.
- Replace the local JSON store with Qdrant or Pinecone before high-traffic production use.
- Put the service behind HTTPS when embedding the widget on real websites.
