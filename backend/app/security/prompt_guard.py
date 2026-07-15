"""Prompt injection / jailbreak detection.

Heuristic pattern classifier (regex + weighted scoring) rather than a full
LlamaGuard-style model classifier, to keep the MVP dependency-light and fast.
Swappable later for a hosted moderation model behind the same interface.
"""
import re

from app.metrics import metrics

_PATTERNS: list[tuple[str, float]] = [
    (r"ignore (all|any|the)?\s*(previous|prior|above)\s*instructions?", 0.9),
    (r"disregard (all|any|the)?\s*(previous|prior|above)", 0.8),
    (r"forget (all|everything|your)\s*(previous|prior|instructions)?", 0.6),
    (r"you are now\b", 0.4),
    (r"act as (an?|a) (unrestricted|unfiltered|jailbroken)", 0.8),
    (r"\bdan mode\b", 0.9),
    (r"jailbreak", 0.7),
    (r"reveal (your|the) (system prompt|instructions|api key|secret)", 0.9),
    (r"print (your|the) (system prompt|instructions)", 0.8),
    (r"bypass (safety|security|restrictions?|guardrails?)", 0.8),
    (r"override (safety|security|restrictions?)", 0.8),
    (r"delete (the )?database", 0.9),
    (r"drop table", 0.9),
    (r"rm\s+-rf", 0.9),
    (r"execute (shell|system) command", 0.8),
    (r"\bsudo\b", 0.3),
    (r"new instructions\s*:", 0.6),
    (r"pretend (you|to) (have no|are not) (restrictions|limits|rules)", 0.7),
    (r"reveal (all|the) secrets?", 0.7),
]

_COMPILED = [(re.compile(p, re.IGNORECASE), w) for p, w in _PATTERNS]

BLOCK_THRESHOLD = 0.6


def scan(text: str) -> dict:
    matched = []
    score = 0.0
    for pattern, weight in _COMPILED:
        if pattern.search(text):
            matched.append(pattern.pattern)
            score = max(score, weight)

    is_injection = score >= BLOCK_THRESHOLD
    if is_injection:
        metrics.incr("prompt_injection_blocked")
    metrics.incr("prompt_injection_scans")

    return {
        "score": round(score, 2),
        "is_injection": is_injection,
        "matched_patterns": matched,
        "action": "blocked" if is_injection else "allowed",
    }
