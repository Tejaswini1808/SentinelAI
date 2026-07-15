"""Embedding client using OpenRouter's /embeddings endpoint via raw httpx.

The `openai` SDK's response parser is strict about the embeddings response
shape and rejects OpenRouter's payload ("No embedding data received") even
though the raw JSON is well-formed, so this calls the endpoint directly.
"""
import httpx

from app.config import get_settings
from app.metrics import metrics

_settings = get_settings()


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    with metrics.time_block("embedding_call"):
        response = httpx.post(
            f"{_settings.openrouter_base_url}/embeddings",
            headers={"Authorization": f"Bearer {_settings.openrouter_api_key}"},
            json={"model": _settings.openrouter_embedding_model, "input": texts},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()["data"]
    return [item["embedding"] for item in data]


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]
