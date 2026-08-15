from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.audit import record_audit
from app.db.session import get_db
from app.models.client import Client
from app.services.alerting import create_screening_alerts
from app.services.matching import match_name
from app.services.opensanctions import OpenSanctionsUnavailable, match_name as match_opensanctions

router = APIRouter(prefix="/screening", tags=["screening"])


class ScreeningRequest(BaseModel):
    name: str = Field(..., min_length=2)
    threshold: Optional[float] = Field(default=None, ge=0.0, le=100.0)


class ScreeningMatchResult(BaseModel):
    matched_name: str
    score: float
    category: str
    country: Optional[str] = None
    notes: Optional[str] = None
    details: Dict[str, Any]


class ScreeningResponse(BaseModel):
    query_name: str
    provider: str
    matches_count: int
    has_match: bool
    results: List[ScreeningMatchResult]


def _screen(
    *,
    name: str,
    settings: Settings,
    threshold: float,
    birth_date=None,
    nationality: Optional[str] = None,
) -> tuple[list[dict], str]:
    if settings.screening_mode in ("opensanctions", "auto"):
        try:
            external_matches = match_opensanctions(
                name=name,
                birth_date=birth_date,
                nationality=nationality,
                api_url=settings.open_sanctions_api_url,
                api_key=settings.open_sanctions_api_key,
                timeout_seconds=settings.open_sanctions_timeout_seconds,
            )
            return [match for match in external_matches if match["score"] >= threshold], "opensanctions"
        except OpenSanctionsUnavailable:
            if settings.screening_mode == "opensanctions":
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Le fournisseur OpenSanctions est indisponible ou non configure.",
                )

    return match_name(query_name=name, threshold=threshold), "local"


@router.post("/match", response_model=ScreeningResponse)
def screen_name(
    req: ScreeningRequest,
    settings: Settings = Depends(get_settings),
) -> ScreeningResponse:
    threshold = (
        settings.default_match_threshold
        if req.threshold is None
        else req.threshold
    )
    raw_matches, provider = _screen(name=req.name, settings=settings, threshold=threshold)

    results = [
        ScreeningMatchResult(
            matched_name=m["matched_name"],
            score=m["score"],
            category=m["watchlist_item"]["category"],
            country=m["watchlist_item"].get("country"),
            notes=m["watchlist_item"].get("notes"),
            details=m,
        )
        for m in raw_matches
    ]

    return ScreeningResponse(
        query_name=req.name,
        provider=provider,
        matches_count=len(results),
        has_match=len(results) > 0,
        results=results,
    )


@router.post("/client/{client_id}", response_model=ScreeningResponse)
def screen_client(
    client_id: int,
    threshold: Optional[float] = Query(None, ge=0.0, le=100.0),
    actor: str = Header(default="system", alias="X-Actor", max_length=100),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ScreeningResponse:
    client = (
        db.query(Client)
        .filter(Client.id == client_id, Client.deleted_at.is_(None))
        .first()
    )
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client ID {client_id} introuvable.",
        )

    full_name = f"{client.first_name} {client.last_name}"
    match_threshold = (
        settings.default_match_threshold if threshold is None else threshold
    )
    raw_matches, provider = _screen(
        name=full_name,
        settings=settings,
        threshold=match_threshold,
        birth_date=client.birth_date,
        nationality=client.nationality,
    )

    results = [
        ScreeningMatchResult(
            matched_name=m["matched_name"],
            score=m["score"],
            category=m["watchlist_item"]["category"],
            country=m["watchlist_item"].get("country"),
            notes=m["watchlist_item"].get("notes"),
            details=m,
        )
        for m in raw_matches
    ]

    alerts = []
    if raw_matches:
        alerts = create_screening_alerts(db, client=client, matches=raw_matches)
        if alerts:
            db.flush()
            for alert in alerts:
                record_audit(
                    db,
                    action="CREATE_ALERT",
                    entity_type="Alert",
                    entity_id=str(alert.id),
                    user_id=actor,
                    details=f"Alerte automatique {alert.alert_type} apres screening du client {client.id}.",
                )

    record_audit(
        db,
        action="SCREEN_CLIENT",
        entity_type="Client",
        entity_id=str(client.id),
        user_id=actor,
        details=(
            f"Screening {provider} execute avec {len(raw_matches)} correspondance(s) "
            f"et {len(alerts)} alerte(s) nouvelle(s)."
        ),
    )
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        # Le resultat de screening reste disponible, mais l'erreur est a surveiller en production.

    return ScreeningResponse(
        query_name=full_name,
        provider=provider,
        matches_count=len(results),
        has_match=len(results) > 0,
        results=results,
    )
