from datetime import date
import json

import httpx
import pytest

from app.services.opensanctions import OpenSanctionsUnavailable, match_name


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
