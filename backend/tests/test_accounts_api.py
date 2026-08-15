from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_crud_account():
    # 1. Create client first
    c_res = client.post(
        "/api/v1/clients",
        json={"first_name": "Marc", "last_name": "Bernard", "email": "marc.bernard@example.com"},
    )
    assert c_res.status_code == 201
    client_id = c_res.json()["id"]

    # 2. Create account
    acc_payload = {
        "account_number": "FR7699998888777766665555444",
        "client_id": client_id,
        "balance": 1000.0,
        "currency": "EUR",
        "status": "active",
    }
    a_res = client.post("/api/v1/accounts", json=acc_payload)
    assert a_res.status_code == 201
    acc_id = a_res.json()["id"]
    assert a_res.json()["account_number"] == "FR7699998888777766665555444"

    # 3. Get account
    get_res = client.get(f"/api/v1/accounts/{acc_id}")
    assert get_res.status_code == 200
    assert float(get_res.json()["balance"]) == 1000.0


    # 4. List accounts for client
    list_res = client.get(f"/api/v1/accounts?client_id={client_id}")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 5. Update account
    up_res = client.put(f"/api/v1/accounts/{acc_id}", json={"status": "frozen"})
    assert up_res.status_code == 200
    assert up_res.json()["status"] == "frozen"

    invalid_res = client.post(
        "/api/v1/accounts",
        json={"account_number": "bad", "client_id": client_id, "balance": 0},
    )
    assert invalid_res.status_code == 422
