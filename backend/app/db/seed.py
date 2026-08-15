from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Dict

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.account import Account
from app.models.alert import Alert
from app.models.audit_log import AuditLog
from app.models.client import Client
from app.models.transaction import Transaction


def seed_demo_data(db: Session) -> Dict[str, int]:
    # Vider les tables existantes (ordre de dépendance FK)
    db.query(Alert).delete(synchronize_session=False)
    db.query(Transaction).delete(synchronize_session=False)
    db.query(Account).delete(synchronize_session=False)
    db.query(Client).delete(synchronize_session=False)
    db.query(AuditLog).delete(synchronize_session=False)

    now = datetime.now(timezone.utc)

    # 1. Clients exemple
    c1 = Client(
        first_name="Jean",
        last_name="Dupont",
        email="jean.dupont@example.com",
        birth_date=date(1980, 4, 12),
        nationality="FR",
        risk_score=10.0,
        is_pep=False,
        is_sanctioned=False,
    )
    c2 = Client(
        first_name="Vladimir",
        last_name="Petrov",
        email="vladimir.petrov@example.com",
        birth_date=date(1975, 9, 30),
        nationality="RU",
        risk_score=85.0,
        is_pep=True,
        is_sanctioned=True,
    )
    c3 = Client(
        first_name="Amina",
        last_name="Al-Mansoor",
        email="amina.mansoor@example.com",
        birth_date=date(1992, 1, 15),
        nationality="AE",
        risk_score=60.0,
        is_pep=True,
        is_sanctioned=False,
    )
    c4 = Client(
        first_name="Carlos",
        last_name="Mendoza",
        email="carlos.mendoza@example.com",
        birth_date=date(1988, 11, 5),
        nationality="MX",
        risk_score=45.0,
        is_pep=False,
        is_sanctioned=False,
    )

    db.add_all([c1, c2, c3, c4])
    db.flush()

    # 2. Comptes bancaires
    a1 = Account(
        account_number="FR7630001007941234567890185",
        client_id=c1.id,
        balance=Decimal("15400.00"),
        currency="EUR",
        status="active",
    )
    a2 = Account(
        account_number="FR7630001007949876543210922",
        client_id=c2.id,
        balance=Decimal("5000000.00"),
        currency="EUR",
        status="frozen",
    )
    a3 = Account(
        account_number="FR7630001007945556667778933",
        client_id=c3.id,
        balance=Decimal("250000.00"),
        currency="EUR",
        status="active",
    )

    db.add_all([a1, a2, a3])
    db.flush()

    # 3. Transactions exemple
    t1 = Transaction(
        account_id=a1.id,
        amount=Decimal("120.00"),
        currency="EUR",
        transaction_type="debit",
        status="completed",
        counterparty_name="Supermarche Paris",
        counterparty_account="FR763000100111",
        timestamp=now,
    )
    t2 = Transaction(
        account_id=a2.id,
        amount=Decimal("2500000.00"),
        currency="EUR",
        transaction_type="transfer",
        status="flagged",
        counterparty_name="Offshore Holding Ltd",
        counterparty_account="CH93000000001234",
        timestamp=now,
    )
    t3 = Transaction(
        account_id=a3.id,
        amount=Decimal("150000.00"),
        currency="EUR",
        transaction_type="transfer",
        status="completed",
        counterparty_name="Al-Mansoor Trading",
        counterparty_account="AE1234567890",
        timestamp=now,
    )

    db.add_all([t1, t2, t3])
    db.flush()

    # 4. Alertes exemple
    al1 = Alert(
        client_id=c2.id,
        transaction_id=t2.id,
        alert_type="SANCTION_MATCH",
        severity="CRITICAL",
        status="OPEN",
        description="Client sous liste de sanctions internationales ayant tente un virement de 2.5M EUR.",
        created_at=now,
    )
    al2 = Alert(
        client_id=c3.id,
        transaction_id=t3.id,
        alert_type="HIGH_TRANSACTION_AMOUNT",
        severity="HIGH",
        status="IN_REVIEW",
        description="Virement d'un montant élevé (150k EUR) associe a une Personne Politiquement Exposee (PEP).",
        created_at=now,
    )

    db.add_all([al1, al2])

    # 5. Audit Log
    log = AuditLog(
        user_id="system_seed",
        action="SEED_DEMO_DATA",
        entity_type="Database",
        entity_id="ALL",
        details="Initialisation des donnees de demonstration du projet LBC/FT/FP.",
        timestamp=now,
    )
    db.add(log)
    db.commit()

    return {
        "clients": 4,
        "accounts": 3,
        "transactions": 3,
        "alerts": 2,
        "audit_logs": 1,
    }


if __name__ == "__main__":
    db = SessionLocal()
    try:
        counts = seed_demo_data(db)
        print(f"Seed de donnees demo reussi ! Elements crees : {counts}")
    finally:
        db.close()
