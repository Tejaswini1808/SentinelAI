import logging
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from app.config import get_settings

logger = logging.getLogger(__name__)
_settings = get_settings()

_client: QdrantClient | None = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        # qdrant-client defaults to port 6333 even when the URL has no explicit
        # port. On networks that only allow outbound 80/443 (e.g. behind a
        # corporate proxy), pin to 443, which Qdrant Cloud also serves REST on.
        _client = QdrantClient(
            url=_settings.qdrant_url,
            api_key=_settings.qdrant_api_key,
            port=443,
            timeout=15,
        )
    return _client


def ensure_collection():
    client = get_client()
    collections = {c.name for c in client.get_collections().collections}
    if _settings.qdrant_collection not in collections:
        client.create_collection(
            collection_name=_settings.qdrant_collection,
            vectors_config=VectorParams(size=_settings.embedding_dim, distance=Distance.COSINE),
        )
        logger.info("created qdrant collection %s", _settings.qdrant_collection)


def upsert_documents(vectors: list[list[float]], payloads: list[dict]):
    client = get_client()
    points = [
        PointStruct(id=str(uuid.uuid4()), vector=vector, payload=payload)
        for vector, payload in zip(vectors, payloads)
    ]
    client.upsert(collection_name=_settings.qdrant_collection, points=points)


def search(vector: list[float], top_k: int = 5, source_filter: str | None = None) -> list[dict]:
    client = get_client()
    query_filter = None
    if source_filter:
        from qdrant_client.http.models import FieldCondition, Filter, MatchValue

        query_filter = Filter(must=[FieldCondition(key="source_type", match=MatchValue(value=source_filter))])

    results = client.query_points(
        collection_name=_settings.qdrant_collection,
        query=vector,
        limit=top_k,
        query_filter=query_filter,
        with_payload=True,
    ).points
    return [{"score": r.score, **(r.payload or {})} for r in results]
