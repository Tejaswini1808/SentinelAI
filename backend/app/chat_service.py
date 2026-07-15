"""Shared RAG-chat logic used by both the FastAPI /chat route and the
Streamlit UI, so the two surfaces don't duplicate the guardrail/retrieval/
generation/grounding sequence."""
from app.llm.provider import chat_completion
from app.rag import retrieval
from app.security import hallucination_guard, prompt_guard

SYSTEM_PROMPT = """You are SentinelAI's security knowledge assistant. Answer the
user's question using ONLY the provided context (MITRE ATT&CK, OWASP, NIST, CVEs,
runbooks, past incidents). If the context doesn't support an answer, say so
explicitly instead of guessing. Cite source ids (e.g. T1566, A03, CVE-2021-44228)
inline when you use them."""


def answer_question(message: str, source_filter: str | None = None) -> dict:
    """Returns {"answer": str, "sources": list[dict], "grounding": dict, "security": dict}."""
    injection = prompt_guard.scan(message)
    if injection["is_injection"]:
        return {
            "answer": "Request blocked: this message matched prompt-injection patterns and was not sent to the model.",
            "sources": [],
            "grounding": {"is_grounded": False, "reason": "blocked before generation"},
            "security": injection,
        }

    sources = retrieval.search(message, source_filter=source_filter)
    context_block = "\n".join(f"- {s['title']}: {s['text']}" for s in sources)

    response = chat_completion(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"CONTEXT:\n{context_block}\n\nQUESTION: {message}"},
        ],
        metric_name="chat_llm",
    )

    grounding = hallucination_guard.check_grounding(response["content"], sources)

    return {"answer": response["content"], "sources": sources, "grounding": grounding, "security": injection}
