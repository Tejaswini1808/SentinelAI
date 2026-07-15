from fastapi import APIRouter, HTTPException

from app.agents.graph import run_alert_pipeline
from app.models import IncidentOut
from app.store import store

router = APIRouter(tags=["investigate"])


@router.post("/investigate/{alert_id}", response_model=IncidentOut)
def investigate_alert(alert_id: str):
    alert = store.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="alert not found")

    store.update_alert_status(alert_id, "investigating")
    result = run_alert_pipeline(alert)

    triage = result.get("triage", {})
    classification = triage.get("classification", "Medium")
    store.update_alert_status(alert_id, "closed_false_positive" if classification == "False Positive" else "investigated")

    incident = store.add_incident(
        {
            "alert": alert,
            "triage": triage,
            "investigation": result.get("investigation", {}),
            "report": result.get("report", {}),
            "grounding": result.get("grounding", {}),
            "security_flags": result.get("security_flags", []),
        }
    )
    return incident
