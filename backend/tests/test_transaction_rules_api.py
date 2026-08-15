from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app
from app.models.account import Account
from app.models.client import Client
from app.models.transaction import Transaction
from tests.conftest import TestSessionLocal


client = TestClient(app)


def test_reassessment_flags_high_risk_country_without_changing_financial_state() -> None:
    db = TestSessionLocal()
    try:
        suffix = uuid4().hex[:8]
        subject = Client(
            first_name="Country",
            last_name="Risk",
            email=f"country.risk.{suffix}@example.com",
        )
        db.add(subject)
        db.flush()
        account = Account(
            client_id=subject.id,
            account_number=f"FR76{uuid4().int % 10**23:023d}",
            balance=Decimal("750.00"),
            currency="EUR",
        )
        db.add(account)
        db.flush()
        transaction = Transaction(
            account_id=account.id,
            amount=Decimal("100.00"),
            currency="EUR",
            transaction_type="transfer",
            status="completed",
            counterparty_country="XY",
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        app.dependency_overrides[get_settings] = lambda: Settings(
            _env_file=None,
            high_risk_countries="XY",
        )
        response = client.post(
            f"/api/v1/transactions/{transaction.id}/evaluate-alerts",
            headers={"X-Actor": "rules.analyst"},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["transaction_id"] == transaction.id
        assert len(payload["alerts_created"]) == 1
        assert payload["alerts_created"][0]["alert_type"] == "HIGH_RISK_COUNTRY_TRANSACTION"

        db.refresh(account)
        db.refresh(transaction)
        assert account.balance == Decimal("750.00")
        assert transaction.status == "completed"

        audit_response = client.get(
            "/api/v1/audit-logs",
            params={
                "action": "EVALUATE_TRANSACTION_RULES",
                "entity_type": "Transaction",
                "entity_id": str(transaction.id),
                "user_id": "rules.analyst",
            },
        )
        assert audit_response.status_code == 200
        assert len(audit_response.json()) == 1
    finally:
        app.dependency_overrides.pop(get_settings, None)
        db.rollback()
        db.close()
