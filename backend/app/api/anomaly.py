from fastapi import APIRouter
from pydantic import BaseModel

from app.services.anomaly import detect_demo_anomalies

router = APIRouter(prefix="/anomaly", tags=["anomaly"])


class AnomalyPointRead(BaseModel):
    id: str
    amount: float
    hour: float
    country_risk: float
    frequency_24h: float
    score: float
    is_anomaly: bool


@router.get("/demo", response_model=list[AnomalyPointRead])
def demo_anomaly_detection() -> list[AnomalyPointRead]:
    """Return IsolationForest scores on a fixed simulated transaction set."""
    return [AnomalyPointRead(**point.__dict__) for point in detect_demo_anomalies()]
