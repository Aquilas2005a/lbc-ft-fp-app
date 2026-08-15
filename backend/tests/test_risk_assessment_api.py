from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_risk_assessment_is_explainable_persisted_and_audited() -> None:
    suffix = uuid4().hex[:8]
    actor = "risk.analyst"
    headers = {"X-Actor": actor}
    client_response = client.post(
        "/api/v1/clients",
        headers=headers,
        json={
            "first_name": "Risk",
            "last_name": "Subject",
            "email": f"risk.subject.{suffix}@example.com",
            "is_pep": True,
        },
    )
    assert client_response.status_code == 201
    client_id = client_response.json()["id"]

    account_response = client.post(
        "/api/v1/accounts",
        json={
            "client_id": client_id,
            "account_number": f"FR76{uuid4().int % 10**23:023d}",
            "balance": 0,
            "currency": "EUR",
        },
    )
    assert account_response.status_code == 201

    transaction_response = client.post(
        "/api/v1/transactions",
        headers=headers,
        json={
            "account_id": account_response.json()["id"],
            "amount": 1_000_000,
            "currency": "EUR",
            "transaction_type": "deposit",
            "status": "completed",
        },
    )
    assert transaction_response.status_code == 201

    response = client.post(
        f"/api/v1/clients/{client_id}/risk-assessment",
        headers=headers,
    )
    assert response.status_code == 200
    assessment = response.json()
    assert assessment["score"] == 55.0
    assert assessment["level"] == "MEDIUM"
    assert "Client declare PEP (+35)" in assessment["factors"]
    assert "Volume cumule de transactions eleve (+15)" in assessment["factors"]
    assert any("alerte(s) active(s)" in factor for factor in assessment["factors"])

    persisted_client = client.get(f"/api/v1/clients/{client_id}")
    assert persisted_client.status_code == 200
    assert persisted_client.json()["risk_score"] == 55.0

    audit_response = client.get(
        "/api/v1/audit-logs",
        params={
            "action": "ASSESS_CLIENT_RISK",
            "entity_type": "Client",
            "entity_id": str(client_id),
            "user_id": actor,
        },
    )
    assert audit_response.status_code == 200
    assert len(audit_response.json()) == 1
    assert "niveau MEDIUM" in audit_response.json()[0]["details"]
