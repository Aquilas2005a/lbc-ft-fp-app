from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.audit import record_audit
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate, RiskAssessmentRead
from app.services.risk import assess_client_risk, risk_level

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(
    client_in: ClientCreate,
    actor: str = Header(default="system", alias="X-Actor", max_length=100),
    db: Session = Depends(get_db),
) -> ClientRead:
    if client_in.email:
        existing = db.query(Client).filter(Client.email == client_in.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un client avec cet email existe deja.",
            )

    client = Client(**client_in.model_dump())
    db.add(client)
    db.flush()
    record_audit(
        db,
        action="CREATE_CLIENT",
        entity_type="Client",
        entity_id=str(client.id),
        user_id=actor,
        details="Creation d'un profil client.",
    )
    db.commit()
    db.refresh(client)
    return client


@router.get("", response_model=List[ClientRead])
def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    is_pep: Optional[bool] = None,
    is_sanctioned: Optional[bool] = None,
    db: Session = Depends(get_db),
) -> List[ClientRead]:
    query = db.query(Client).filter(Client.deleted_at.is_(None))

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                Client.first_name.ilike(pattern),
                Client.last_name.ilike(pattern),
                Client.email.ilike(pattern),
                Client.nationality.ilike(pattern),
            )
        )

    if is_pep is not None:
        query = query.filter(Client.is_pep == is_pep)

    if is_sanctioned is not None:
        query = query.filter(Client.is_sanctioned == is_sanctioned)

    return query.offset(skip).limit(limit).all()


@router.post("/{client_id}/risk-assessment", response_model=RiskAssessmentRead)
def assess_risk(
    client_id: int,
    actor: str = Header(default="system", alias="X-Actor", max_length=100),
    db: Session = Depends(get_db),
) -> RiskAssessmentRead:
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

    score, factors = assess_client_risk(db, client)
    level = risk_level(score)
    client.risk_score = score
    evaluated_at = datetime.now(timezone.utc)
    record_audit(
        db,
        action="ASSESS_CLIENT_RISK",
        entity_type="Client",
        entity_id=str(client.id),
        user_id=actor,
        details=f"Score {score:.0f}/100, niveau {level}, {len(factors)} facteur(s).",
    )
    db.commit()
    db.refresh(client)
    return RiskAssessmentRead(
        client_id=client.id,
        score=score,
        level=level,
        factors=factors,
        evaluated_at=evaluated_at,
    )


@router.get("/{client_id}", response_model=ClientRead)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
) -> ClientRead:
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
    return client


@router.put("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: int,
    client_in: ClientUpdate,
    actor: str = Header(default="system", alias="X-Actor", max_length=100),
    db: Session = Depends(get_db),
) -> ClientRead:
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

    update_data = client_in.model_dump(exclude_unset=True)
    if "email" in update_data and update_data["email"] and update_data["email"] != client.email:
        existing = db.query(Client).filter(Client.email == update_data["email"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un client avec cet email existe deja.",
            )

    for field, value in update_data.items():
        setattr(client, field, value)

    record_audit(
        db,
        action="UPDATE_CLIENT",
        entity_type="Client",
        entity_id=str(client.id),
        user_id=actor,
        details=f"Champs modifies : {', '.join(sorted(update_data)) or 'aucun'}.",
    )
    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    actor: str = Header(default="system", alias="X-Actor", max_length=100),
    db: Session = Depends(get_db),
) -> None:
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

    client.deleted_at = datetime.now(timezone.utc)
    record_audit(
        db,
        action="SOFT_DELETE_CLIENT",
        entity_type="Client",
        entity_id=str(client.id),
        user_id=actor,
        details="Suppression logique du profil client.",
    )
    db.commit()
