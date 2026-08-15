from datetime import timedelta
from decimal import Decimal
from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.alert import Alert
from app.models.client import Client
from app.models.transaction import Transaction


def _create_once(
    db: Session,
    *,
    alert_type: str,
    description: str,
    severity: str,
    client_id: int | None = None,
    transaction_id: int | None = None,
) -> Alert | None:
    query = select(Alert.id).where(Alert.alert_type == alert_type)
    if transaction_id is not None:
        query = query.where(Alert.transaction_id == transaction_id)
    elif client_id is not None:
        query = query.where(Alert.client_id == client_id, Alert.transaction_id.is_(None))

    if db.scalar(query.limit(1)) is not None:
        return None

    alert = Alert(
        alert_type=alert_type,
        severity=severity,
        status="OPEN",
        description=description,
        client_id=client_id,
        transaction_id=transaction_id,
    )
    db.add(alert)
    return alert


def create_screening_alerts(
    db: Session,
    client: Client,
    matches: Iterable[dict],
) -> list[Alert]:
    alerts: list[Alert] = []
    for match in matches:
        item = match["watchlist_item"]
        category = item["category"]
        severity = "CRITICAL" if category == "SANCTION" else "HIGH"
        alert = _create_once(
            db,
            alert_type=f"SCREENING_{category}",
            severity=severity,
            client_id=client.id,
            description=(
                f"Correspondance de screening a revoir : {match['matched_name']} "
                f"({match['score']:.1f} %, categorie {category})."
            ),
        )
        if alert:
            alerts.append(alert)
    return alerts


def create_transaction_alerts(
    db: Session,
    transaction: Transaction,
    client_id: int,
    settings: Settings,
) -> list[Alert]:
    alerts: list[Alert] = []
    threshold = Decimal(str(settings.high_transaction_amount))
    if transaction.amount >= threshold:
        alert = _create_once(
            db,
            alert_type="HIGH_TRANSACTION_AMOUNT",
            severity="HIGH",
            client_id=client_id,
            transaction_id=transaction.id,
            description=(
                f"Transaction de {transaction.amount} {transaction.currency} au-dessus "
                f"du seuil configure de {threshold} {transaction.currency}."
            ),
        )
        if alert:
            alerts.append(alert)

    if transaction.counterparty_country in settings.high_risk_countries:
        alert = _create_once(
            db,
            alert_type="HIGH_RISK_COUNTRY_TRANSACTION",
            severity="HIGH",
            client_id=client_id,
            transaction_id=transaction.id,
            description=(
                f"Transaction impliquant le pays de contrepartie "
                f"{transaction.counterparty_country}, configure comme a risque."
            ),
        )
        if alert:
            alerts.append(alert)

    window_start = transaction.timestamp - timedelta(
        hours=settings.transaction_frequency_window_hours
    )
    recent_count = db.scalar(
        select(func.count(Transaction.id)).where(
            Transaction.account_id == transaction.account_id,
            Transaction.status == "completed",
            Transaction.timestamp >= window_start,
            Transaction.timestamp <= transaction.timestamp,
        )
    )
    if recent_count >= settings.transaction_frequency_count:
        alert = _create_once(
            db,
            alert_type="HIGH_TRANSACTION_FREQUENCY",
            severity="MEDIUM",
            client_id=client_id,
            transaction_id=transaction.id,
            description=(
                f"{recent_count} transactions finalisees sur les "
                f"{settings.transaction_frequency_window_hours} dernieres heures."
            ),
        )
        if alert:
            alerts.append(alert)
    return alerts
