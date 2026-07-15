from fastapi import APIRouter

from app.agents.investigation import investigation_node
from app.agents.reporting import report_node
from app.agents.triage import triage_node
from app.models import AlertIn

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/triage")
def run_triage(alert: AlertIn):
    return triage_node({"alert": alert.model_dump()})


@router.post("/hunt")
def run_hunt(alert: AlertIn):
    state = triage_node({"alert": alert.model_dump()})
    return investigation_node({"alert": alert.model_dump(), "triage": state.get("triage", {})})


@router.post("/report")
def run_report(alert: AlertIn):
    state = triage_node({"alert": alert.model_dump()})
    state.update(investigation_node({"alert": alert.model_dump(), **state}))
    return report_node({"alert": alert.model_dump(), **state})
