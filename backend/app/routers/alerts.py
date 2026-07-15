from fastapi import APIRouter, HTTPException

from app.models import AlertIn, AlertOut
from app.store import store

router = APIRouter(tags=["alerts"])


@router.post("/alerts", response_model=AlertOut)
def create_alert(alert: AlertIn):
    record = store.add_alert(alert.model_dump())
    return record


@router.get("/alerts", response_model=list[AlertOut])
def list_alerts():
    return store.list_alerts()


@router.get("/alerts/{alert_id}", response_model=AlertOut)
def get_alert(alert_id: str):
    record = store.get_alert(alert_id)
    if not record:
        raise HTTPException(status_code=404, detail="alert not found")
    return record
