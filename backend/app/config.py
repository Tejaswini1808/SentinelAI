import os
from functools import lru_cache

import truststore
from dotenv import load_dotenv

# Use the OS trust store instead of certifi's public-CA-only bundle. Needed on
# networks with a TLS-inspecting proxy (e.g. Zscaler) whose root CA is trusted
# by the OS/browsers but not by certifi.
truststore.inject_into_ssl()

load_dotenv()


class Settings:
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free")
    openrouter_fallback_models: list[str] = [
        m.strip() for m in os.getenv("OPENROUTER_FALLBACK_MODELS", "").split(",") if m.strip()
    ]
    openrouter_embedding_model: str = os.getenv(
        "OPENROUTER_EMBEDDING_MODEL", "nvidia/llama-nemotron-embed-vl-1b-v2:free"
    )

    # Optional self-hosted OpenAI-compatible vLLM server. When set, chat_completion
    # calls it directly (no rate limits, single fixed model) instead of OpenRouter's
    # free tier. DEMO_MODE reflects which path is active.
    vllm_api_url: str = os.getenv("VLLM_API_URL", "")
    vllm_model: str = os.getenv("VLLM_MODEL", "")
    demo_mode: bool = not os.getenv("VLLM_API_URL", "")

    qdrant_url: str = os.getenv("QDRANT_URL", "")
    qdrant_api_key: str = os.getenv("QDRANT_API_KEY", "")
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "security_knowledge_base")
    embedding_dim: int = int(os.getenv("EMBEDDING_DIM", "2048"))

    grounding_threshold: float = float(os.getenv("GROUNDING_THRESHOLD", "0.15"))
    retrieval_top_k: int = int(os.getenv("RETRIEVAL_TOP_K", "5"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
