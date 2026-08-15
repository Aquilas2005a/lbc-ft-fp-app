from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_seed_demo_endpoint():
    response = client.post("/api/v1/seed")
    assert response.status_code == 200
    data = response.json()
    assert "entities_created" in data
    assert data["entities_created"]["clients"] == 4
    assert data["entities_created"]["accounts"] == 3
    assert data["entities_created"]["transactions"] == 3

    # Check clients created
    clients_res = client.get("/api/v1/clients")
    assert clients_res.status_code == 200
    assert len(clients_res.json()) >= 4
