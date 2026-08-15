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
