from datetime import date
from typing import Any

import httpx


class OpenSanctionsUnavailable(RuntimeError):
    """Raised when the optional screening provider cannot be used."""


def _category(topics: list[str]) -> str:
    if "sanction" in topics:
        return "SANCTION"
    if "role.pep" in topics:
        return "PEP"
    return "WATCHLIST"


def _query(name: str, birth_date: date | None, nationality: str | None) -> dict[str, Any]:
    name_parts = name.strip().split(maxsplit=1)
    properties: dict[str, list[str]] = {"name": [name.strip()]}
    if len(name_parts) == 2:
        properties["firstName"] = [name_parts[0]]
        properties["lastName"] = [name_parts[1]]
    if birth_date:
        properties["birthDate"] = [birth_date.isoformat()]
    if nationality:
        properties["nationality"] = [nationality]
    return {"schema": "Person", "properties": properties}


def match_name(
    *,
    name: str,
    api_url: str,
    api_key: str | None,
    timeout_seconds: float,
    birth_date: date | None = None,
    nationality: str | None = None,
    client: httpx.Client | None = None,
) -> list[dict[str, Any]]:
    if not api_key:
        raise OpenSanctionsUnavailable("La cle OpenSanctions est absente.")

    request_client = client or httpx.Client(timeout=timeout_seconds)
    close_client = client is None
    try:
        response = request_client.post(
            f"{api_url.rstrip('/')}/match/default",
            headers={"Authorization": f"ApiKey {api_key}"},
            json={"queries": {"client": _query(name, birth_date, nationality)}},
        )
        response.raise_for_status()
        raw_results = response.json().get("responses", {}).get("client", {}).get("results", [])
    except (httpx.HTTPError, ValueError) as exc:
        raise OpenSanctionsUnavailable("Le screening OpenSanctions est indisponible.") from exc
    finally:
        if close_client:
            request_client.close()

    results: list[dict[str, Any]] = []
    for result in raw_results:
        properties = result.get("properties", {})
        topics = properties.get("topics", [])
        score = round(float(result.get("score", 0.0)) * 100, 2)
        results.append(
            {
                "matched_name": result.get("caption", result.get("id", "Entite inconnue")),
                "score": score,
                "watchlist_item": {
                    "id": result.get("id"),
                    "name": result.get("caption", result.get("id", "Entite inconnue")),
                    "category": _category(topics),
                    "country": (properties.get("country") or [None])[0],
                    "notes": ", ".join(result.get("datasets", [])[:3]) or None,
                },
                "provider": "opensanctions",
            }
        )
    return results
