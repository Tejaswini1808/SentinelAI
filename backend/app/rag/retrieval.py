"""Retrieval: dense vector search over Qdrant + a lightweight keyword-overlap
re-rank pass (a practical approximation of hybrid search without standing up a
separate BM25/sparse-vector engine for the MVP)."""
import re

from app.config import get_settings
from app.llm.embeddings import embed_text
from app.metrics import metrics
from app.rag import qdrant_store

_settings = get_settings()
_WORD_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> set[str]:
    return set(_WORD_RE.findall(text.lower()))


def _keyword_overlap_score(query_tokens: set[str], doc: dict) -> float:
    doc_tokens = _tokenize(doc.get("text", "") + " " + " ".join(doc.get("tags", [])))
    if not query_tokens or not doc_tokens:
        return 0.0
    overlap = query_tokens & doc_tokens
    return len(overlap) / len(query_tokens)


def search(query: str, top_k: int | None = None, source_filter: str | None = None) -> list[dict]:
    top_k = top_k or _settings.retrieval_top_k
    with metrics.time_block("retrieval_latency"):
        query_vector = embed_text(query)
        candidates = qdrant_store.search(query_vector, top_k=top_k * 3, source_filter=source_filter)

        query_tokens = _tokenize(query)
        for c in candidates:
            keyword_score = _keyword_overlap_score(query_tokens, c)
            c["vector_score"] = c["score"]
            c["keyword_score"] = keyword_score
            c["rerank_score"] = 0.7 * c["vector_score"] + 0.3 * keyword_score

        candidates.sort(key=lambda c: c["rerank_score"], reverse=True)
        results = candidates[:top_k]
    metrics.incr("retrieval_calls")
    return results
