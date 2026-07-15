from typing import TypedDict


class AlertState(TypedDict, total=False):
    alert: dict
    security_flags: list[dict]
    triage: dict
    investigation: dict
    report: dict
    retrieved_context: list[dict]
    grounding: dict
    errors: list[str]
