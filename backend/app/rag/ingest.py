import logging

from app.data.knowledge_base import build_knowledge_base
from app.llm.embeddings import embed_texts
from app.rag import qdrant_store

logger = logging.getLogger(__name__)

BATCH_SIZE = 16


def ingest_knowledge_base() -> int:
    qdrant_store.ensure_collection()
    docs = build_knowledge_base()
    total = 0
    for i in range(0, len(docs), BATCH_SIZE):
        batch = docs[i : i + BATCH_SIZE]
        vectors = embed_texts([d["text"] for d in batch])
        qdrant_store.upsert_documents(vectors, batch)
        total += len(batch)
        logger.info("ingested %d/%d documents", total, len(docs))
    return total


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    count = ingest_knowledge_base()
    print(f"Ingested {count} documents into Qdrant.")
