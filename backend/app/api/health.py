import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import __version__
from app.core.config import Settings, get_settings
from app.db.session import get_db

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
    version: str
    timestamp: datetime


class DatabaseHealthResponse(BaseModel):
    status: str
    database: str
    connected: bool
    timestamp: datetime


@router.get("/health", response_model=HealthResponse)
def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.app_env,
        version=__version__,
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/health/db", response_model=DatabaseHealthResponse)
def database_health_check(
    db: Session = Depends(get_db),
) -> DatabaseHealthResponse:
    try:
        database_name = db.execute(text("SELECT current_database()")).scalar_one()
        return DatabaseHealthResponse(
            status="ok",
            database=database_name,
            connected=True,
            timestamp=datetime.now(timezone.utc),
        )
    except SQLAlchemyError as exc:
        logger.exception("Database health check failed.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La base de donnees est indisponible.",
        ) from exc
