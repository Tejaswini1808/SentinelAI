from fastapi import APIRouter

from app.config import get_settings
from app.metrics import metrics

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
def get_metrics():
    settings = get_settings()
    return {**metrics.snapshot(), "demo_mode": settings.demo_mode}
