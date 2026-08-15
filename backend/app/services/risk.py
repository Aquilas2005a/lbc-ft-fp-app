from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.alert import Alert
from app.models.client import Client
from app.models.transaction import Transaction


def assess_client_risk(db: Session, client: Client) -> tuple[float, list[str]]:
    """Return a deterministic demonstration score with human-readable factors."""
    score = 0.0
    factors: list[str] = []
    if client.is_pep:
        score += 35.0
        factors.append("Client declare PEP (+35)")
    if client.is_sanctioned:
        score += 50.0
        factors.append("Statut sanctionne renseigne manuellement (+50)")

    open_alerts = db.scalar(
        select(func.count(Alert.id)).where(
            Alert.client_id == client.id,
            Alert.status.in_(("OPEN", "IN_REVIEW", "ESCALATED")),
        )
    )
    if open_alerts:
        addition = min(open_alerts * 5.0, 15.0)
        score += addition
        factors.append(f"{open_alerts} alerte(s) active(s) (+{addition:.0f})")

    total_volume = db.scalar(
        select(func.coalesce(func.sum(Transaction.amount), Decimal("0")))
        .join(Account, Transaction.account_id == Account.id)
        .where(Account.client_id == client.id, Transaction.status == "completed")
    )
    if total_volume >= Decimal("1000000"):
        score += 15.0
        factors.append("Volume cumule de transactions eleve (+15)")

    return min(score, 100.0), factors or ["Aucun facteur de risque automatique identifie"]
