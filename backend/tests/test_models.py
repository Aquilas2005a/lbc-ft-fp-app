from datetime import date, datetime, timezone
from decimal import Decimal

from app.models.account import Account
from app.models.alert import Alert
from app.models.audit_log import AuditLog
from app.models.client import Client
from app.models.transaction import Transaction
from app.schemas.account import AccountCreate, AccountRead
from app.schemas.alert import AlertCreate, AlertRead
from app.schemas.audit_log import AuditLogCreate, AuditLogRead
from app.schemas.client import ClientCreate, ClientRead
from app.schemas.transaction import TransactionCreate, TransactionRead


def test_client_model_and_schema():
    client_data = {
        "first_name": "Jean",
        "last_name": "Dupont",
        "email": "jean.dupont@example.com",
        "birth_date": date(1985, 5, 20),
        "nationality": "FR",
        "risk_score": 15.5,
        "is_pep": False,
        "is_sanctioned": False,
    }
    client_create = ClientCreate(**client_data)
    assert client_create.first_name == "Jean"
    assert client_create.email == "jean.dupont@example.com"

    client_orm = Client(
        id=1,
        **client_create.model_dump(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    assert client_orm.id == 1
    assert client_orm.last_name == "Dupont"

    client_read = ClientRead.model_validate(client_orm)
    assert client_read.id == 1
    assert client_read.first_name == "Jean"


def test_account_model_and_schema():
    account_create = AccountCreate(
        account_number="FR7612345678901234567890189",
        client_id=1,
        balance=Decimal("5000.00"),
        currency="EUR",
        status="active",
    )
    assert account_create.account_number == "FR7612345678901234567890189"

    account_orm = Account(
        id=10,
        **account_create.model_dump(),
        created_at=datetime.now(timezone.utc),
    )
    assert account_orm.id == 10
    assert account_orm.client_id == 1

    account_read = AccountRead.model_validate(account_orm)
    assert account_read.id == 10
    assert account_read.balance == Decimal("5000.00")


def test_transaction_model_and_schema():
    tx_create = TransactionCreate(
        account_id=10,
        amount=Decimal("1500.00"),
        currency="EUR",
        transaction_type="transfer",
        status="completed",
        counterparty_name="Alice Smith",
        counterparty_account="GB1234567890",
    )
    assert tx_create.amount == Decimal("1500.00")

    tx_orm = Transaction(
        id=100,
        **tx_create.model_dump(),
        timestamp=datetime.now(timezone.utc),
    )
    assert tx_orm.id == 100

    tx_read = TransactionRead.model_validate(tx_orm)
    assert tx_read.id == 100
    assert tx_read.counterparty_name == "Alice Smith"


def test_alert_model_and_schema():
    alert_create = AlertCreate(
        client_id=1,
        transaction_id=100,
        alert_type="HIGH_TRANSACTION_AMOUNT",
        severity="HIGH",
        status="OPEN",
        description="Transaction de 1500 EUR supérieure au seuil",
    )
    assert alert_create.severity == "HIGH"

    alert_orm = Alert(
        id=50,
        **alert_create.model_dump(),
        created_at=datetime.now(timezone.utc),
    )
    assert alert_orm.id == 50

    alert_read = AlertRead.model_validate(alert_orm)
    assert alert_read.id == 50
    assert alert_read.alert_type == "HIGH_TRANSACTION_AMOUNT"


def test_audit_log_model_and_schema():
    audit_create = AuditLogCreate(
        user_id="user_admin",
        action="CREATE_CLIENT",
        entity_type="Client",
        entity_id="1",
        details="Création du client Jean Dupont",
    )
    assert audit_create.action == "CREATE_CLIENT"

    audit_orm = AuditLog(
        id=1,
        **audit_create.model_dump(),
        timestamp=datetime.now(timezone.utc),
    )
    assert audit_orm.id == 1

    audit_read = AuditLogRead.model_validate(audit_orm)
    assert audit_read.id == 1
    assert audit_read.user_id == "user_admin"
