"""LLM provider: a self-hosted vLLM server if VLLM_API_URL is configured
(single fixed model, no rate limits), otherwise OpenRouter's free tier with
retry + fallback across models (DEMO_MODE).

Free OpenRouter models get globally rate-limited across all users, so a single
hardcoded model is unreliable for a demo. This tries the configured model first,
then falls through a fallback list on 429/404/5xx/empty-content before giving up.
"""
import logging
import time

from openai import APIStatusError, OpenAI

from app.config import get_settings
from app.metrics import metrics

logger = logging.getLogger(__name__)

_settings = get_settings()

if _settings.demo_mode:
    _client = OpenAI(api_key=_settings.openrouter_api_key, base_url=_settings.openrouter_base_url)
else:
    _client = OpenAI(api_key="not-needed", base_url=_settings.vllm_api_url)


class LLMUnavailableError(RuntimeError):
    pass


def _candidate_models() -> list[str]:
    if not _settings.demo_mode:
        return [_settings.vllm_model]
    models = [_settings.openrouter_model] + _settings.openrouter_fallback_models
    seen = set()
    ordered = []
    for m in models:
        if m not in seen:
            seen.add(m)
            ordered.append(m)
    return ordered


def chat_completion(
    messages: list[dict],
    temperature: float = 0.2,
    max_tokens: int = 1024,
    metric_name: str = "llm_call",
) -> dict:
    """Returns {"content": str, "model": str, "usage": dict}. Raises LLMUnavailableError
    if every candidate model fails."""
    last_error = None
    with metrics.time_block(metric_name):
        for model in _candidate_models():
            for attempt in range(2):
                try:
                    response = _client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    choice = response.choices[0].message.content or ""
                    usage = response.usage.model_dump() if response.usage else {}
                    metrics.add_token_usage(usage)
                    if not choice.strip():
                        # Some free reasoning models burn the whole token budget on
                        # hidden reasoning and emit no final answer. Treat as a
                        # failure and fall through to the next candidate model.
                        logger.warning("model %s returned empty content, trying next candidate", model)
                        metrics.incr("llm_calls_empty")
                        last_error = RuntimeError(f"{model} returned empty content")
                        break
                    metrics.incr("llm_calls_ok")
                    return {"content": choice, "model": model, "usage": usage}
                except APIStatusError as exc:
                    last_error = exc
                    body = exc.response.json() if exc.response is not None else {}
                    meta = (body.get("error") or {}).get("metadata") or {}
                    retry_after = meta.get("retry_after_seconds") or 0
                    if exc.status_code == 429 and retry_after and retry_after <= 5 and attempt == 0:
                        time.sleep(min(retry_after, 5))
                        continue
                    logger.warning("model %s failed (%s), trying next candidate", model, exc.status_code)
                    metrics.incr("llm_calls_failed")
                    break
                except Exception as exc:  # network errors etc.
                    last_error = exc
                    metrics.incr("llm_calls_failed")
                    break
    raise LLMUnavailableError(f"All candidate models failed: {last_error}")
