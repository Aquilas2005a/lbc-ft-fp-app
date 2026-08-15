"""
Tests T17 – Génération automatique d'alertes.

Couvre :
- create_transaction_alerts : HIGH_TRANSACTION_AMOUNT, HIGH_TRANSACTION_FREQUENCY
- create_screening_alerts   : SCREENING_SANCTION, SCREENING_PEP
- déduplication (_create_once) : pas de doublon sur même type+transaction
- intégration API : POST /transactions génère une alerte si montant > seuil
"""
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from starlette.testclient import TestClient

from tests.conftest import TestSessionLocal, app, override_get_db
from app.core.config import Settings
from app.db.session import get_db
from app.models.account import Account
from app.models.alert import Alert
from app.models.client import Client
from app.models.transaction import Transaction
from app.services.alerting import (
    create_screening_alerts,
    create_transaction_alerts,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_client(db, *, first_name="Test", last_name="User") -> Client:
    client = Client(
        first_name=first_name,
        last_name=last_name,
        email=f"{first_name.lower()}.{last_name.lower()}@test.invalid",
        risk_score=0.0,
        is_pep=False,
        is_sanctioned=False,
    )
    db.add(client)
    db.flush()
    return client


def _make_account(db, client_id: int, balance: Decimal = Decimal("9999999")) -> Account:
    account = Account(
        account_number=f"TEST{client_id:010d}",
        client_id=client_id,
        balance=balance,
        currency="EUR",
        status="active",
    )
    db.add(account)
    db.flush()
    return account


def _make_transaction(
    db,
    account_id: int,
    amount: Decimal,
    status: str = "completed",
) -> Transaction:
    tx = Transaction(
        account_id=account_id,
        amount=amount,
        currency="EUR",
        transaction_type="transfer",
        status=status,
        timestamp=_now(),
    )
    db.add(tx)
    db.flush()
    return tx


def _settings(
    *,
    high_amount: float = 1_000_000.0,
    freq_count: int = 3,
    freq_window: int = 24,
) -> Settings:
    return Settings(
        high_transaction_amount=high_amount,
        transaction_frequency_count=freq_count,
        transaction_frequency_window_hours=freq_window,
    )


# ---------------------------------------------------------------------------
# Tests unitaires du service alerting
# ---------------------------------------------------------------------------

class TestCreateTransactionAlerts:
    def test_no_alert_below_threshold(self, migrated_test_database):
        db = TestSessionLocal()
        try:
            client = _make_client(db)
            account = _make_account(db, client.id)
            tx = _make_transaction(db, account.id, Decimal("500.00"))
            settings = _settings(high_amount=1_000_000.0, freq_count=5)

            alerts = create_transaction_alerts(db, transaction=tx, client_id=client.id, settings=settings)
            assert alerts == []
        finally:
            db.rollback()
            db.close()

    def test_alert_created_above_threshold(self, migrated_test_database):
        db = TestSessionLocal()
        try:
            client = _make_client(db)
            account = _make_account(db, client.id)
            tx = _make_transaction(db, account.id, Decimal("1500000.00"))
            settings = _settings(high_amount=1_000_000.0, freq_count=5)

            alerts = create_transaction_alerts(db, transaction=tx, client_id=client.id, settings=settings)
            assert len(alerts) == 1
            assert alerts[0].alert_type == "HIGH_TRANSACTION_AMOUNT"
            assert alerts[0].severity == "HIGH"
            assert alerts[0].status == "OPEN"
            assert alerts[0].transaction_id == tx.id
            assert alerts[0].client_id == client.id
        finally:
            db.rollback()
            db.close()

    def test_no_duplicate_alert_same_transaction(self, migrated_test_database):
        db = TestSessionLocal()
        try:
            client = _make_client(db)
            account = _make_account(db, client.id)
            tx = _make_transaction(db, account.id, Decimal("2000000.00"))
            settings = _settings(high_amount=1_000_000.0, freq_count=5)

            alerts_first = create_transaction_alerts(db, transaction=tx, client_id=client.id, settings=settings)
            db.flush()
            alerts_second = create_transaction_alerts(db, transaction=tx, client_id=client.id, settings=settings)

            assert len(alerts_first) == 1
            assert len(alerts_second) == 0  # déduplication
        finally:
            db.rollback()
            db.close()

    def test_high_frequency_alert(self, migrated_test_database):
        db = TestSessionLocal()
        try:
            client = _make_client(db)
            account = _make_account(db, client.id, Decimal("99999999"))
            settings = _settings(high_amount=9_999_999.0, freq_count=3, freq_window=24)

            # Créer 3 transactions completed pour déclencher l'alerte de fréquence
            txs = [
                _make_transaction(db, account.id, Decimal("100.00"), status="completed")
                for _ in range(3)
            ]

            all_alerts = []
            for tx in txs:
                all_alerts.extend(
                    create_transaction_alerts(db, transaction=tx, client_id=client.id, settings=settings)
                )

            freq_alerts = [a for a in all_alerts if a.alert_type == "HIGH_TRANSACTION_FREQUENCY"]
            assert len(freq_alerts) >= 1
        finally:
            db.rollback()
            db.close()


class TestCreateScreeningAlerts:
    def _fake_match(self, category: str, name: str = "Vladimir Petrov", score: float = 95.0):
        return {
            "matched_name": name,
            "score": score,
            "watchlist_item": {
                "name": name,
                "category": category,
                "country": "RU",
                "notes": "Test",
            },
        }

    def test_sanction_alert_critical(self, migrated_test_database):
        db = TestSessionLocal()
        try:
            client = _make_client(db, first_name="Ivan", last_name="Sokolov")
            matches = [self._fake_match("SANCTION")]
            alerts = create_screening_alerts(db, client=client, matches=matches)
            assert len(alerts) == 1
            assert alerts[0].alert_type == "SCREENING_SANCTION"
            assert alerts[0].severity == "CRITICAL"
            assert alerts[0].client_id == client.id
            assert alerts[0].transaction_id is None
        finally:
            db.rollback()
            db.close()

    def test_pep_alert_high(self, migrated_test_database):
        db = TestSessionLocal()
        try:
            client = _make_client(db, first_name="Paul", last_name="Martin")
            matches = [self._fake_match("PEP")]
            alerts = create_screening_alerts(db, client=client, matches=matches)
            assert len(alerts) == 1
            assert alerts[0].alert_type == "SCREENING_PEP"
            assert alerts[0].severity == "HIGH"
        finally:
            db.rollback()
            db.close()

    def test_no_duplicate_screening_alert(self, migrated_test_database):
        db = TestSessionLocal()
        try:
            client = _make_client(db, first_name="Marie", last_name="Dupuis")
            matches = [self._fake_match("SANCTION")]
            alerts_first = create_screening_alerts(db, client=client, matches=matches)
            db.flush()
            alerts_second = create_screening_alerts(db, client=client, matches=matches)
            assert len(alerts_first) == 1
            assert len(alerts_second) == 0
        finally:
            db.rollback()
            db.close()


# ---------------------------------------------------------------------------
# Test d'intégration API : POST /transactions → alerte auto
# ---------------------------------------------------------------------------

class TestTransactionAPITriggersAlert:
    def setup_method(self):
        app.dependency_overrides[get_db] = override_get_db
        self.api = TestClient(app)

    def teardown_method(self):
        app.dependency_overrides[get_db] = override_get_db

    def test_large_transaction_creates_alert(self, migrated_test_database):
        db = TestSessionLocal()
        try:
            client = _make_client(db, first_name="Riche", last_name="Client")
            account = _make_account(db, client.id, Decimal("9999999"))
            db.commit()

            # Poster une transaction bien au-dessus du seuil de 1 000 000 €
            response = self.api.post("/api/v1/transactions", json={
                "account_id": account.id,
                "amount": "2000000.00",
                "currency": "EUR",
                "transaction_type": "transfer",
                "status": "completed",
            })
            assert response.status_code == 201

            # Vérifier qu'une alerte a bien été créée
            alerts = (
                db.query(Alert)
                .filter(Alert.client_id == client.id, Alert.alert_type == "HIGH_TRANSACTION_AMOUNT")
                .all()
            )
            assert len(alerts) == 1
            assert alerts[0].severity == "HIGH"
        finally:
            db.rollback()
            db.close()


class TestAlertReviewWorkflow:
    def setup_method(self):
        app.dependency_overrides[get_db] = override_get_db
        self.api = TestClient(app)

    def teardown_method(self):
        app.dependency_overrides[get_db] = override_get_db

    def test_alert_list_detail_and_review(self, migrated_test_database):
        db = TestSessionLocal()
        try:
            client = _make_client(db, first_name="Alicia", last_name="Martin")
            account = _make_account(db, client.id, Decimal("1000000"))
            tx = _make_transaction(db, account.id, Decimal("1500000.00"), status="completed")
            alert = Alert(
                client_id=client.id,
                transaction_id=tx.id,
                alert_type="HIGH_TRANSACTION_AMOUNT",
                severity="HIGH",
                status="OPEN",
                description="Montant inhabituel sur la transaction de test.",
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)

            list_response = self.api.get("/api/v1/alerts")
            assert list_response.status_code == 200
            alerts = list_response.json()
            assert any(item["id"] == alert.id for item in alerts)

            detail_response = self.api.get(f"/api/v1/alerts/{alert.id}")
            assert detail_response.status_code == 200
            detail = detail_response.json()
            assert detail["id"] == alert.id
            assert detail["status"] == "OPEN"

            review_payload = {
                "status": "VALIDATED",
                "review_note": "Transaction conforme après vérification humaine.",
            }
            update_response = self.api.put(f"/api/v1/alerts/{alert.id}/review", json=review_payload)
            assert update_response.status_code == 200
            updated = update_response.json()
            assert updated["status"] == "VALIDATED"
            assert updated["review_note"] == review_payload["review_note"]
            assert updated["reviewed_by"] == "system"
            assert updated["reviewed_at"] is not None
        finally:
            db.rollback()
            db.close()

    def test_alert_filters(self, migrated_test_database):
        """Test les filtres sur GET /alerts"""
        db = TestSessionLocal()
        try:
            client1 = _make_client(db, first_name="Alice", last_name="Dupont")
            client2 = _make_client(db, first_name="Bob", last_name="Martin")
            
            account1 = _make_account(db, client1.id)
            account2 = _make_account(db, client2.id)
            
            tx1 = _make_transaction(db, account1.id, Decimal("1500000.00"), status="completed")
            tx2 = _make_transaction(db, account2.id, Decimal("100.00"), status="completed")
            
            alert1 = Alert(
                client_id=client1.id,
                transaction_id=tx1.id,
                alert_type="HIGH_TRANSACTION_AMOUNT",
                severity="HIGH",
                status="OPEN",
                description="Alert 1",
            )
            alert2 = Alert(
                client_id=client2.id,
                transaction_id=tx2.id,
                alert_type="HIGH_TRANSACTION_FREQUENCY",
                severity="MEDIUM",
                status="OPEN",
                description="Alert 2",
            )
            db.add_all([alert1, alert2])
            db.commit()
            
            # Filtrer par client_id
            response = self.api.get(f"/api/v1/alerts?client_id={client1.id}")
            assert response.status_code == 200
            alerts = response.json()
            assert len(alerts) == 1
            assert alerts[0]["client_id"] == client1.id
            
            # Filtrer par severity
            response = self.api.get("/api/v1/alerts?severity=HIGH")
            assert response.status_code == 200
            alerts = response.json()
            assert all(a["severity"] == "HIGH" for a in alerts)
            
            # Filtrer par status
            response = self.api.get("/api/v1/alerts?status=OPEN")
            assert response.status_code == 200
            alerts = response.json()
            assert len(alerts) >= 2
        finally:
            db.rollback()
            db.close()

    def test_invalid_status_transition(self, migrated_test_database):
        """Test qu'une transition invalide est rejetée"""
        db = TestSessionLocal()
        try:
            client = _make_client(db)
            alert = Alert(
                client_id=client.id,
                alert_type="SCREENING_SANCTION",
                severity="CRITICAL",
                status="OPEN",
                description="Test alert",
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            # Tenter une transition invalide : OPEN -> REJECTED (invalide, doit être VALIDATED, REJECTED, ou ESCALATED)
            # En fait REJECTED est valide depuis OPEN. Essayons VALIDATED -> OPEN (invalide)
            # D'abord, OPEN -> VALIDATED
            review_payload = {
                "status": "VALIDATED",
                "review_note": "First review",
            }
            response = self.api.put(f"/api/v1/alerts/{alert.id}/review", json=review_payload)
            assert response.status_code == 200
            
            # Ensuite, tenter VALIDATED -> OPEN (invalide)
            invalid_review = {
                "status": "OPEN",
                "review_note": "Try to go back",
            }
            response = self.api.put(f"/api/v1/alerts/{alert.id}/review", json=invalid_review)
            assert response.status_code == 400
            assert "Transition invalide" in response.json()["detail"]
        finally:
            db.rollback()
            db.close()

    def test_alert_summary_stats(self, migrated_test_database):
        """Test l'endpoint de statistiques des alertes"""
        db = TestSessionLocal()
        try:
            client = _make_client(db)
            account = _make_account(db, client.id)
            
            # Créer des alertes avec différents statuts et sévérités
            alerts = [
                Alert(
                    client_id=client.id,
                    alert_type="HIGH_TRANSACTION_AMOUNT",
                    severity="HIGH",
                    status="OPEN",
                    description="Alert 1",
                ),
                Alert(
                    client_id=client.id,
                    alert_type="SCREENING_SANCTION",
                    severity="CRITICAL",
                    status="OPEN",
                    description="Alert 2",
                ),
                Alert(
                    client_id=client.id,
                    alert_type="HIGH_TRANSACTION_FREQUENCY",
                    severity="MEDIUM",
                    status="VALIDATED",
                    description="Alert 3",
                ),
            ]
            db.add_all(alerts)
            db.commit()
            
            response = self.api.get(f"/api/v1/alerts/stats/summary?client_id={client.id}")
            assert response.status_code == 200
            summary = response.json()
            
            assert summary["total"] >= 3
            assert summary["by_status"]["OPEN"] >= 2
            assert summary["by_status"]["VALIDATED"] >= 1
            assert summary["by_severity"]["CRITICAL"] >= 1
            assert summary["by_severity"]["HIGH"] >= 1
        finally:
            db.rollback()
            db.close()
