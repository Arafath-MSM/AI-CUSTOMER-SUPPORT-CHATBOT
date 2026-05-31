from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from openai import APIError, APITimeoutError, AsyncOpenAI

from app.core.config import settings
from app.schemas.knowledge import (
    CompanyListResponse,
    CompanySummary,
    KnowledgeDeleteResponse,
    KnowledgeDocumentSummary,
    KnowledgeMatch,
    KnowledgeQueryResponse,
    KnowledgeSummaryResponse,
    KnowledgeUploadResponse,
)

FALLBACK_EMBEDDING_DIMENSIONS = 256


class KnowledgeBaseError(Exception):
    """Raised when the knowledge base cannot index or query content."""


async def index_text_document(
    *,
    company_id: str,
    title: str,
    content: str,
) -> KnowledgeUploadResponse:
    chunks = split_text(content)
    if not chunks:
        raise KnowledgeBaseError("Document does not contain indexable text.")

    embeddings = await embed_texts(chunks)
    document_id = str(uuid4())
    created_at = datetime.now(UTC).isoformat()

    store = _read_store()
    store["documents"].append(
        {
            "document_id": document_id,
            "company_id": company_id,
            "title": title,
            "chunks_indexed": len(chunks),
            "created_at": created_at,
        }
    )

    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings, strict=True)):
        store["chunks"].append(
            {
                "chunk_id": str(uuid4()),
                "document_id": document_id,
                "company_id": company_id,
                "title": title,
                "chunk_index": index,
                "text": chunk,
                "embedding": embedding,
                "embedding_model": _active_embedding_model(),
                "created_at": created_at,
            }
        )

    _write_store(store)

    return KnowledgeUploadResponse(
        document_id=document_id,
        company_id=company_id,
        title=title,
        chunks_indexed=len(chunks),
        embedding_model=_active_embedding_model(),
    )


async def query_knowledge_base(
    *,
    company_id: str,
    query: str,
    top_k: int | None = None,
) -> KnowledgeQueryResponse:
    store = _read_store()
    chunks = [
        chunk
        for chunk in store["chunks"]
        if chunk.get("company_id") == company_id
        and chunk.get("embedding_model") == _active_embedding_model()
    ]

    if not chunks:
        return KnowledgeQueryResponse(
            query=query,
            company_id=company_id,
            matches=[],
            embedding_model=_active_embedding_model(),
        )

    query_embedding = (await embed_texts([query]))[0]
    ranked = sorted(
        (
            (_cosine_similarity(query_embedding, chunk["embedding"]), chunk)
            for chunk in chunks
        ),
        key=lambda item: item[0],
        reverse=True,
    )

    limit = top_k or settings.rag_top_k
    matches = [
        KnowledgeMatch(
            document_id=chunk["document_id"],
            title=chunk["title"],
            chunk_index=chunk["chunk_index"],
            score=round(score, 4),
            text=chunk["text"],
        )
        for score, chunk in ranked[:limit]
        if score > 0
    ]

    return KnowledgeQueryResponse(
        query=query,
        company_id=company_id,
        matches=matches,
        embedding_model=_active_embedding_model(),
    )


def list_knowledge_documents(company_id: str) -> KnowledgeSummaryResponse:
    store = _read_store()
    documents = [
        KnowledgeDocumentSummary(**document)
        for document in store["documents"]
        if document.get("company_id") == company_id
    ]
    total_chunks = sum(document.chunks_indexed for document in documents)

    return KnowledgeSummaryResponse(
        company_id=company_id,
        documents=documents,
        total_chunks=total_chunks,
    )


def list_companies() -> CompanyListResponse:
    store = _read_store()
    company_map: dict[str, dict[str, int | str | None]] = {}

    for document in store["documents"]:
        company_id = document.get("company_id")
        if not company_id:
            continue

        company = company_map.setdefault(
            company_id,
            {
                "documents_count": 0,
                "total_chunks": 0,
                "latest_document_at": None,
            },
        )
        company["documents_count"] = int(company["documents_count"]) + 1
        company["total_chunks"] = int(company["total_chunks"]) + int(
            document.get("chunks_indexed", 0)
        )

        created_at = document.get("created_at")
        latest = company["latest_document_at"]
        if isinstance(created_at, str) and (latest is None or created_at > latest):
            company["latest_document_at"] = created_at

    companies = [
        CompanySummary(
            company_id=company_id,
            documents_count=int(summary["documents_count"]),
            total_chunks=int(summary["total_chunks"]),
            latest_document_at=summary["latest_document_at"]
            if isinstance(summary["latest_document_at"], str)
            else None,
        )
        for company_id, summary in sorted(company_map.items())
    ]

    return CompanyListResponse(companies=companies)


def delete_knowledge_document(document_id: str) -> KnowledgeDeleteResponse:
    store = _read_store()
    matching_documents = [
        document
        for document in store["documents"]
        if document.get("document_id") == document_id
    ]

    if not matching_documents:
        return KnowledgeDeleteResponse(
            document_id=document_id,
            deleted=False,
            chunks_deleted=0,
        )

    original_chunk_count = len(store["chunks"])
    store["documents"] = [
        document
        for document in store["documents"]
        if document.get("document_id") != document_id
    ]
    store["chunks"] = [
        chunk
        for chunk in store["chunks"]
        if chunk.get("document_id") != document_id
    ]
    chunks_deleted = original_chunk_count - len(store["chunks"])

    _write_store(store)

    return KnowledgeDeleteResponse(
        document_id=document_id,
        deleted=True,
        chunks_deleted=chunks_deleted,
    )


def split_text(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []

    chunk_size = max(settings.rag_chunk_size, 200)
    overlap = min(max(settings.rag_chunk_overlap, 0), chunk_size // 2)
    chunks: list[str] = []
    start = 0

    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind(" ", start, end)
            if boundary > start + chunk_size // 2:
                end = boundary

        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(normalized):
            break

        start = max(end - overlap, 0)

    return chunks


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not settings.has_openai_api_key:
        return [_fallback_embedding(text) for text in texts]

    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        timeout=settings.openai_timeout_seconds,
    )

    try:
        response = await client.embeddings.create(
            model=settings.openai_embedding_model,
            input=texts,
        )
    except (APIError, APITimeoutError) as exc:
        raise KnowledgeBaseError("Embedding provider request failed.") from exc

    return [item.embedding for item in response.data]


def _active_embedding_model() -> str:
    if settings.has_openai_api_key:
        return settings.openai_embedding_model
    return f"local-hash-{FALLBACK_EMBEDDING_DIMENSIONS}"


def _fallback_embedding(text: str) -> list[float]:
    vector = [0.0] * FALLBACK_EMBEDDING_DIMENSIONS
    tokens = re.findall(r"[a-z0-9]+", text.lower())

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % FALLBACK_EMBEDDING_DIMENSIONS
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign

    magnitude = math.sqrt(sum(value * value for value in vector))
    if magnitude == 0:
        return vector

    return [value / magnitude for value in vector]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0

    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_mag = math.sqrt(sum(value * value for value in left))
    right_mag = math.sqrt(sum(value * value for value in right))
    if left_mag == 0 or right_mag == 0:
        return 0.0

    return dot / (left_mag * right_mag)


def _read_store() -> dict[str, list[dict]]:
    store_path = _store_path()
    if not store_path.exists():
        return {"documents": [], "chunks": []}

    with store_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return {
        "documents": data.get("documents", []),
        "chunks": data.get("chunks", []),
    }


def _write_store(store: dict[str, list[dict]]) -> None:
    store_path = _store_path()
    store_path.parent.mkdir(parents=True, exist_ok=True)

    with store_path.open("w", encoding="utf-8") as file:
        json.dump(store, file, ensure_ascii=False, indent=2)


def _store_path() -> Path:
    return Path(settings.knowledge_store_path)
