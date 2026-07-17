"""RAG pipeline: retrieval with citations for chat and agent context."""
from dataclasses import dataclass

from app.embeddings.embedder import embed_texts
from app.embeddings.vector_store import get_vector_store


@dataclass
class RetrievedChunk:
    chunk_id: str
    document_id: str
    filename: str
    page_number: int
    content: str
    score: float


def index_chunks(chunk_ids: list[str], contents: list[str], payloads: list[dict]) -> None:
    vectors = embed_texts(contents)
    get_vector_store().upsert(chunk_ids, vectors, payloads)


def retrieve(query: str, k: int = 8, filters: dict | None = None) -> list[RetrievedChunk]:
    [qvec] = embed_texts([query])
    hits = get_vector_store().search(qvec, k=k, filters=filters)
    return [RetrievedChunk(
        chunk_id=h.get("id", ""), document_id=h.get("document_id", ""),
        filename=h.get("filename", ""), page_number=int(h.get("page_number", 0)),
        content=h.get("content", ""), score=h.get("score", 0.0),
    ) for h in hits]


def build_context(chunks: list[RetrievedChunk], max_chars: int = 12000) -> str:
    parts, total = [], 0
    for i, c in enumerate(chunks, 1):
        block = f"[Source {i}: {c.filename}, page {c.page_number}]\n{c.content}"
        if total + len(block) > max_chars:
            break
        parts.append(block)
        total += len(block)
    return "\n\n---\n\n".join(parts)
