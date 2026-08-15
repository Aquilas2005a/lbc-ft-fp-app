from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_crud_client():
    # 1. Create client
    payload = {
        "first_name": "Sophie",
        "last_name": "Martin",
        "email": "sophie.martin@example.com",
        "birth_date": "1990-03-25",
        "nationality": "FR",
        "risk_score": 25.0,
        "is_pep": False,
        "is_sanctioned": False,
    }
    response = client.post("/api/v1/clients", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Sophie"
    client_id = data["id"]

    # 2. Get client
    get_res = client.get(f"/api/v1/clients/{client_id}")
    assert get_res.status_code == 200
    assert get_res.json()["email"] == "sophie.martin@example.com"

    # 3. List clients
    list_res = client.get("/api/v1/clients?search=Sophie")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 4. Update client
    update_res = client.put(f"/api/v1/clients/{client_id}", json={"risk_score": 40.0, "is_pep": True})
    assert update_res.status_code == 200
    assert update_res.json()["risk_score"] == 40.0
    assert update_res.json()["is_pep"] is True

    # 5. Delete client
    del_res = client.delete(f"/api/v1/clients/{client_id}")
    assert del_res.status_code == 204

    # 6. Verify 404
    get_404 = client.get(f"/api/v1/clients/{client_id}")
    assert get_404.status_code == 404

    list_after_delete = client.get("/api/v1/clients?search=Sophie")
    assert list_after_delete.status_code == 200
    assert list_after_delete.json() == []
