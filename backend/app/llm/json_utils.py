import json
import re

_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def extract_json(text: str) -> dict:
    """Best-effort JSON extraction from an LLM response that may include
    markdown fences or surrounding prose."""
    fence_match = _FENCE_RE.search(text)
    candidate = fence_match.group(1) if fence_match else text

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    start, end = candidate.find("{"), candidate.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(candidate[start : end + 1])
        except json.JSONDecodeError:
            pass

    return {"_raw": text, "_parse_error": True}
