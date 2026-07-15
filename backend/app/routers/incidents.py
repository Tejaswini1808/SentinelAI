from fastapi import APIRouter, HTTPException

from app.models import IncidentOut
from app.store import store

router = APIRouter(tags=["incidents"])


@router.get("/incident/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: str):
    record = store.get_incident(incident_id)
    if not record:
        raise HTTPException(status_code=404, detail="incident not found")
    return record


@router.get("/incidents", response_model=list[IncidentOut])
def list_incidents():
    return store.list_incidents()
