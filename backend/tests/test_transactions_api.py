from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_transaction_api():
    # 1. Create client and account
    c_res = client.post(
        "/api/v1/clients",
        json={"first_name": "Luc", "last_name": "Moreau", "email": "luc.moreau@example.com"},
    )
    client_id = c_res.json()["id"]

    acc_res = client.post(
        "/api/v1/accounts",
        json={
            "account_number": "FR7611112222333344445555666",
            "client_id": client_id,
            "balance": 5000.0,
            "currency": "EUR",
        },
    )
    acc_id = acc_res.json()["id"]

    # 2. Create transaction (withdrawal 500 EUR)
    tx_payload = {
        "account_id": acc_id,
        "amount": 500.0,
        "currency": "EUR",
        "transaction_type": "withdrawal",
        "status": "completed",
        "counterparty_name": "ATM Paris",
    }
    tx_res = client.post("/api/v1/transactions", json=tx_payload)
    assert tx_res.status_code == 201
    tx_id = tx_res.json()["id"]
    assert float(tx_res.json()["amount"]) == 500.0

    # 3. Check account balance updated (5000 - 500 = 4500)
    acc_check = client.get(f"/api/v1/accounts/{acc_id}")
    assert float(acc_check.json()["balance"]) == 4500.0


    # 4. Get transaction details
    get_tx = client.get(f"/api/v1/transactions/{tx_id}")
    assert get_tx.status_code == 200
    assert get_tx.json()["counterparty_name"] == "ATM Paris"

    # 5. List transactions for account
    list_tx = client.get(f"/api/v1/transactions?account_id={acc_id}")
    assert list_tx.status_code == 200
    assert len(list_tx.json()) >= 1

    insufficient_funds = client.post(
        "/api/v1/transactions",
        json={
            "account_id": acc_id,
            "amount": 5000.0,
            "currency": "EUR",
            "transaction_type": "withdrawal",
        },
    )
    assert insufficient_funds.status_code == 400

    wrong_currency = client.post(
        "/api/v1/transactions",
        json={
            "account_id": acc_id,
            "amount": 10.0,
            "currency": "USD",
            "transaction_type": "deposit",
        },
    )
    assert wrong_currency.status_code == 400
