from datetime import date
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.api import screening as screening_module
from app.core.config import Settings, get_settings
from app.main import app
from app.services.opensanctions import OpenSanctionsUnavailable, match_name

client = TestClient(app)


def test_opensanctions_adapter_builds_request_and_normalizes_results() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["authorization"] = request.headers["Authorization"]
        captured["payload"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "responses": {
                    "client": {
                        "results": [
                            {
                                "id": "OS-123",
                                "caption": "Example Sanctioned Person",
                                "score": 0.91,
                                "datasets": ["eu_fsf"],
                                "properties": {
                                    "topics": ["sanction"],
                                    "country": ["ru"],
                                },
                            }
                        ]
                    }
                }
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        results = match_name(
            name="Example Person",
            birth_date=date(1980, 1, 1),
            nationality="RU",
            api_url="https://api.example.test",
            api_key="demo-key",
            timeout_seconds=5,
            client=http_client,
        )

    assert captured["url"] == "https://api.example.test/match/default"
    assert captured["authorization"] == "ApiKey demo-key"
    assert captured["payload"]["queries"]["client"]["properties"]["birthDate"] == ["1980-01-01"]
    assert results[0]["score"] == 91.0
    assert results[0]["watchlist_item"]["category"] == "SANCTION"
    assert results[0]["watchlist_item"]["country"] == "ru"


def test_opensanctions_adapter_requires_api_key() -> None:
    with pytest.raises(OpenSanctionsUnavailable):
        match_name(
            name="Example Person",
            api_url="https://api.example.test",
            api_key=None,
            timeout_seconds=5,
        )


def test_screening_endpoint_auto_mode_falls_back_to_local_without_api_key() -> None:
    """T18 : le mode 'auto' doit rester utilisable sans cle API, en repli local."""

    def override_settings() -> Settings:
        return Settings(
            screening_mode="auto",
            open_sanctions_api_key=None,
            database_url="postgresql+psycopg://lbc_user:lbc_password@localhost:5432/lbc_test",
        )

    app.dependency_overrides[get_settings] = override_settings
    try:
        res = client.post(
            "/api/v1/screening/match",
            json={"name": "Vladimir Petrov", "threshold": 75.0},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "local"
        assert data["has_match"] is True
    finally:
        app.dependency_overrides.pop(get_settings, None)


def test_screening_endpoint_opensanctions_mode_without_key_returns_503() -> None:
    """T18 : le mode 'opensanctions' force est explicite si aucune cle n'est configuree."""

    def override_settings() -> Settings:
        return Settings(
            screening_mode="opensanctions",
            open_sanctions_api_key=None,
            database_url="postgresql+psycopg://lbc_user:lbc_password@localhost:5432/lbc_test",
        )

    app.dependency_overrides[get_settings] = override_settings
    try:
        res = client.post(
            "/api/v1/screening/match",
            json={"name": "Vladimir Petrov", "threshold": 75.0},
        )
        assert res.status_code == 503
    finally:
        app.dependency_overrides.pop(get_settings, None)
