from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertRead, AlertUpdate

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=List[AlertRead])
def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    alert_type: Optional[str] = None,
    severity: Optional[str] = None,
    client_id: Optional[int] = None,
    transaction_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
) -> List[AlertRead]:
    """
    Récupère la liste des alertes avec filtres optionnels.
    
    Filtres disponibles:
    - status: OPEN, IN_REVIEW, ESCALATED, RESOLVED, DISMISSED
    - alert_type: type d'alerte (ex: SCREENING_SANCTION, HIGH_TRANSACTION_AMOUNT)
    - severity: LOW, MEDIUM, HIGH, CRITICAL
    - client_id: ID du client
    - transaction_id: ID de la transaction
    - from_date: Date de début (création >= from_date)
    - to_date: Date de fin (création <= to_date)
    """
    query = db.query(Alert)

    if status:
        query = query.filter(Alert.status == status)

    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)

    if severity:
        query = query.filter(Alert.severity == severity)

    if client_id is not None:
        query = query.filter(Alert.client_id == client_id)

    if transaction_id is not None:
        query = query.filter(Alert.transaction_id == transaction_id)

    if from_date:
        query = query.filter(Alert.created_at >= from_date)

    if to_date:
        query = query.filter(Alert.created_at <= to_date)

    # Tri par date descending (les plus récentes en premier)
    alerts = query.order_by(desc(Alert.created_at)).offset(skip).limit(limit).all()
    return alerts


@router.get("/{alert_id}", response_model=AlertRead)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
) -> AlertRead:
    """
    Récupère une alerte spécifique par son ID.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alerte avec ID {alert_id} non trouvée.",
        )
    return alert


@router.put("/{alert_id}/review", response_model=AlertRead, status_code=status.HTTP_200_OK)
def review_alert(
    alert_id: int,
    review_data: AlertUpdate,
    db: Session = Depends(get_db),
) -> AlertRead:
    """
    Met à jour le statut d'une alerte et ajoute une note de révision.
    
    Workflow de révision:
    - OPEN -> VALIDATED (alerte confirmée comme un risque réel)
    - OPEN -> REJECTED (alerte rejetée, faux positif)
    - OPEN -> ESCALATED (nécessite escalade pour révision externe)
    - VALIDATED -> ESCALATED (escalade après validation)
    
    Champs mis à jour:
    - status: nouveau statut de l'alerte
    - review_note: note de révision (min 3, max 2000 caractères)
    - reviewed_by: défini automatiquement à "system"
    - reviewed_at: défini automatiquement à la date/heure actuelle UTC
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alerte avec ID {alert_id} non trouvée.",
        )

    # Validation du statut - on ne peut transitionner que vers certains états
    valid_transitions = {
        "OPEN": ["VALIDATED", "REJECTED", "ESCALATED"],
        "VALIDATED": ["ESCALATED"],
        "REJECTED": [],
        "ESCALATED": [],
    }

    if review_data.status not in valid_transitions.get(alert.status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transition invalide : {alert.status} -> {review_data.status}. "
            f"Transitions autorisées depuis {alert.status}: {valid_transitions.get(alert.status, [])}",
        )

    # Mise à jour
    alert.status = review_data.status
    alert.review_note = review_data.review_note
    alert.reviewed_by = "system"  # En production, utiliser l'utilisateur depuis le contexte
    alert.reviewed_at = datetime.now(timezone.utc)

    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.get("/stats/summary")
def get_alerts_summary(
    client_id: Optional[int] = None,
    db: Session = Depends(get_db),
) -> dict:
    """
    Récupère un résumé des alertes par statut et sévérité.
    
    Utile pour les tableaux de bord de conformité.
    """
    query = db.query(Alert)

    if client_id is not None:
        query = query.filter(Alert.client_id == client_id)

    total = query.count()
    by_status = {}
    by_severity = {}

    for status_val in ["OPEN", "VALIDATED", "REJECTED", "ESCALATED"]:
        by_status[status_val] = query.filter(Alert.status == status_val).count()

    for severity_val in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        by_severity[severity_val] = query.filter(Alert.severity == severity_val).count()

    return {
        "total": total,
        "by_status": by_status,
        "by_severity": by_severity,
    }
