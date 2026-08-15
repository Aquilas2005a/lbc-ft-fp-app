from uuid import uuid4

from fastapi.testclient import TestClient

from app.models.alert import Alert
from app.models.client import Client
from tests.conftest import TestSessionLocal, app


client = TestClient(app)


def test_alert_review_creates_auditable_event() -> None:
    db = TestSessionLocal()
    try:
        suffix = uuid4().hex[:8]
        subject = Client(
            first_name="Audit",
            last_name="Subject",
            email=f"audit.subject.{suffix}@test.invalid",
        )
        db.add(subject)
        db.flush()
        alert = Alert(
            client_id=subject.id,
            alert_type="SCREENING_PEP",
            severity="HIGH",
            status="OPEN",
            description="Correspondance a revoir.",
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)

        response = client.put(
            f"/api/v1/alerts/{alert.id}/review",
            headers={"X-Actor": "compliance.agent"},
            json={
                "status": "VALIDATED",
                "review_note": "Correspondance confirmee apres revue humaine.",
            },
        )
        assert response.status_code == 200
        assert response.json()["reviewed_by"] == "compliance.agent"

        audit_response = client.get(
            "/api/v1/audit-logs",
            params={
                "action": "REVIEW_ALERT",
                "entity_type": "Alert",
                "entity_id": str(alert.id),
                "user_id": "compliance.agent",
            },
        )
        assert audit_response.status_code == 200
        events = audit_response.json()
        assert len(events) == 1
        assert events[0]["action"] == "REVIEW_ALERT"
        assert events[0]["user_id"] == "compliance.agent"
        assert "OPEN vers VALIDATED" in events[0]["details"]
        assert "Correspondance confirmee" not in events[0]["details"]
    finally:
        db.rollback()
        db.close()


def test_business_actions_are_recorded_with_actor() -> None:
    suffix = uuid4().hex[:8]
    actor = "compliance.operator"
    headers = {"X-Actor": actor}
    create_response = client.post(
        "/api/v1/clients",
        headers=headers,
        json={
            "first_name": "Audit",
            "last_name": "Trail",
            "email": f"audit.trail.{suffix}@example.com",
        },
    )
    assert create_response.status_code == 201
    client_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/v1/clients/{client_id}",
        headers=headers,
        json={"nationality": "FR"},
    )
    assert update_response.status_code == 200

    account_number = f"FR76{uuid4().int % 10**23:023d}"
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "client_id": client_id,
            "account_number": account_number,
            "balance": 0,
            "currency": "EUR",
        },
    )
    assert account_response.status_code == 201
    account_id = account_response.json()["id"]

    transaction_response = client.post(
        "/api/v1/transactions",
        headers=headers,
        json={
            "account_id": account_id,
            "amount": 100,
            "currency": "EUR",
            "transaction_type": "deposit",
            "status": "completed",
        },
    )
    assert transaction_response.status_code == 201

    screening_response = client.post(
        f"/api/v1/screening/client/{client_id}",
        headers=headers,
    )
    assert screening_response.status_code == 200
    assert screening_response.json()["has_match"] is False

    delete_response = client.delete(f"/api/v1/clients/{client_id}", headers=headers)
    assert delete_response.status_code == 204

    events_response = client.get(
        "/api/v1/audit-logs",
        params={"entity_id": str(client_id), "user_id": actor, "limit": 50},
    )
    assert events_response.status_code == 200
    actions = {event["action"] for event in events_response.json()}
    assert {
        "CREATE_CLIENT",
        "UPDATE_CLIENT",
        "SCREEN_CLIENT",
        "SOFT_DELETE_CLIENT",
    }.issubset(actions)

    transaction_id = transaction_response.json()["id"]
    transaction_audit_response = client.get(
        "/api/v1/audit-logs",
        params={
            "action": "CREATE_TRANSACTION",
            "entity_type": "Transaction",
            "entity_id": str(transaction_id),
            "user_id": actor,
        },
    )
    assert transaction_audit_response.status_code == 200
    assert len(transaction_audit_response.json()) == 1
