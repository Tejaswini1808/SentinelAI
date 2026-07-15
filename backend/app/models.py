from typing import Optional

from pydantic import BaseModel, Field


class AlertIn(BaseModel):
    event_type: str
    description: str
    severity_hint: Optional[str] = None
    src_ip: Optional[str] = None
    dest_ip: Optional[str] = None
    user: Optional[str] = None
    user_email: Optional[str] = None
    domain: Optional[str] = None
    file_hash: Optional[str] = None
    raw_log: Optional[str] = None
    source: Optional[str] = "unknown"
    timestamp: Optional[str] = None


class AlertOut(AlertIn):
    id: str
    status: str = "new"


class InvestigateRequest(BaseModel):
    alert_id: str


class IncidentOut(BaseModel):
    id: str
    alert: dict
    triage: dict
    investigation: dict
    report: dict
    grounding: dict
    security_flags: list[dict] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str
    source_filter: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]
    grounding: dict
    security: dict


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    source_filter: Optional[str] = None
