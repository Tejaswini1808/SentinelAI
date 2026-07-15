"""Grounding / hallucination check: verify a generated answer is actually
supported by the retrieved context before it's returned to the user.

Combines two independent signals:
1. Embedding cosine similarity between the answer and the retrieved context
   (semantic grounding).
2. Whether the answer explicitly cites at least one retrieved source id/title
   (source attribution).
"""
import numpy as np

from app.config import get_settings
from app.llm.embeddings import embed_texts
from app.metrics import metrics

_settings = get_settings()


def _cosine(a: list[float], b: list[float]) -> float:
    a_arr, b_arr = np.array(a), np.array(b)
    denom = np.linalg.norm(a_arr) * np.linalg.norm(b_arr)
    if denom == 0:
        return 0.0
    return float(np.dot(a_arr, b_arr) / denom)


def check_grounding(answer: str, sources: list[dict]) -> dict:
    if not answer.strip() or not sources:
        metrics.incr("hallucination_flagged")
        return {
            "grounding_score": 0.0,
            "cited_sources": False,
            "is_grounded": False,
            "reason": "no answer or no retrieved sources to ground against",
        }

    context_text = "\n".join(s.get("text", "") for s in sources)
    answer_vec, context_vec = embed_texts([answer, context_text])
    grounding_score = _cosine(answer_vec, context_vec)

    lowered = answer.lower()
    cited = any(
        s.get("doc_id", "").lower() in lowered or s.get("title", "").lower()[:20] in lowered for s in sources
    )

    is_grounded = grounding_score >= _settings.grounding_threshold or cited
    if not is_grounded:
        metrics.incr("hallucination_flagged")

    return {
        "grounding_score": round(grounding_score, 4),
        "cited_sources": cited,
        "is_grounded": is_grounded,
        "reason": "grounded" if is_grounded else "low semantic similarity to retrieved context and no citation found",
    }
