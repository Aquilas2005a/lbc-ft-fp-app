from fastapi.testclient import TestClient
from app.main import app
from app.services.matching import match_name

client = TestClient(app)


def test_matching_service_unit():
    # Exact match for Vladimir Petrov
    results = match_name("Vladimir Petrov", threshold=80.0)
    assert len(results) >= 1
    assert results[0]["matched_name"] == "Vladimir Petrov"
    assert results[0]["score"] >= 95.0

    # Fuzzy match for Wladimir Petrov
    fuzzy_results = match_name("Wladimir Petrov", threshold=70.0)
    assert len(fuzzy_results) >= 1
    assert fuzzy_results[0]["matched_name"] == "Vladimir Petrov"
    assert fuzzy_results[0]["score"] >= 75.0

    accent_results = match_name("Jean Pierre Duval", threshold=85.0)
    assert accent_results[0]["matched_name"] == "Jean-Pierre Duval"


def test_screening_api():
    # 1. Screen raw name via POST /api/v1/screening/match
    res = client.post("/api/v1/screening/match", json={"name": "Vladimir Petrov", "threshold": 75.0})
    assert res.status_code == 200
    data = res.json()
    assert data["has_match"] is True
    assert data["matches_count"] >= 1
    assert data["results"][0]["matched_name"] == "Vladimir Petrov"

    # 2. Seed data first
    client.post("/api/v1/seed")

    # 3. Get clients to find Vladimir Petrov
    c_res = client.get("/api/v1/clients?search=Vladimir")
    assert c_res.status_code == 200
    clients = c_res.json()
    assert len(clients) >= 1
    vladimir_id = clients[0]["id"]

    # 4. Screen client by ID via POST /api/v1/screening/client/{client_id}
    sc_res = client.post(f"/api/v1/screening/client/{vladimir_id}?threshold=70.0")
    assert sc_res.status_code == 200
    sc_data = sc_res.json()
    assert sc_data["has_match"] is True
