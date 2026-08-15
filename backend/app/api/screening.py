from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models.client import Client
from app.services.matching import match_name

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
    matches_count: int
    has_match: bool
    results: List[ScreeningMatchResult]


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
    raw_matches = match_name(query_name=req.name, threshold=threshold)

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
        matches_count=len(results),
        has_match=len(results) > 0,
        results=results,
    )


@router.post("/client/{client_id}", response_model=ScreeningResponse)
def screen_client(
    client_id: int,
    threshold: Optional[float] = Query(None, ge=0.0, le=100.0),
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
    raw_matches = match_name(query_name=full_name, threshold=match_threshold)

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
        query_name=full_name,
        matches_count=len(results),
        has_match=len(results) > 0,
        results=results,
    )
