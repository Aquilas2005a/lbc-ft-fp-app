from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.audit import record_audit
from app.db.session import get_db
from app.models.account import Account
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionRead
from app.services.alerting import create_transaction_alerts

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    tx_in: TransactionCreate,
    actor: str = Header(default="system", alias="X-Actor", max_length=100),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TransactionRead:
    account = db.scalar(
        select(Account)
        .where(Account.id == tx_in.account_id)
        .with_for_update()
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compte ID {tx_in.account_id} introuvable.",
        )

    if account.currency != tx_in.currency:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La devise de la transaction doit correspondre a celle du compte.",
        )

    if tx_in.status == "completed":
        if tx_in.transaction_type in ("deposit", "credit"):
            account.balance += tx_in.amount
        elif tx_in.transaction_type in ("withdrawal", "debit", "transfer"):
            if account.balance < tx_in.amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Solde insuffisant pour cette transaction.",
                )
            account.balance -= tx_in.amount

    transaction = Transaction(**tx_in.model_dump())
    db.add(transaction)
    try:
        db.flush()
        record_audit(
            db,
            action="CREATE_TRANSACTION",
            entity_type="Transaction",
            entity_id=str(transaction.id),
            user_id=actor,
            details=(
                f"Transaction {transaction.transaction_type} de {transaction.amount} "
                f"{transaction.currency}, statut {transaction.status}."
            ),
        )
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La transaction ne peut pas etre enregistree.",
        ) from exc

    db.refresh(transaction)

    # --- T17 : génération automatique d'alertes ---
    alerts = create_transaction_alerts(
        db,
        transaction=transaction,
        client_id=account.client_id,
        settings=settings,
    )
    if alerts:
        db.flush()
        for alert in alerts:
            record_audit(
                db,
                action="CREATE_ALERT",
                entity_type="Alert",
                entity_id=str(alert.id),
                user_id=actor,
                details=f"Alerte automatique {alert.alert_type} pour transaction {transaction.id}.",
            )
        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            # Les alertes sont non-bloquantes : on ne fait pas échouer la transaction

    return transaction


@router.get("", response_model=List[TransactionRead])
def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    account_id: Optional[int] = None,
    db: Session = Depends(get_db),
) -> List[TransactionRead]:
    query = db.query(Transaction)
    if account_id is not None:
        query = query.filter(Transaction.account_id == account_id)

    return query.order_by(Transaction.timestamp.desc()).offset(skip).limit(limit).all()


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
) -> TransactionRead:
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction ID {transaction_id} introuvable.",
        )
    return tx
