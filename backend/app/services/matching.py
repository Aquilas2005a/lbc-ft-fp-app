from typing import Any, Dict, List, Optional
from unicodedata import combining, normalize

from rapidfuzz import fuzz

# Liste de référence locale d'individus et entités sous sanctions / PEP (mode hors-ligne)
LOCAL_WATCHLIST = [
    {
        "id": "PEP-001",
        "name": "Vladimir Petrov",
        "entity_type": "individual",
        "category": "SANCTION_PEP",
        "country": "RU",
        "notes": "Personne sous sanctions internationales et PEP de haut niveau",
    },
    {
        "id": "PEP-002",
        "name": "Amina Al-Mansoor",
        "entity_type": "individual",
        "category": "PEP",
        "country": "AE",
        "notes": "Personne Politiquement Exposee (gouvernement)",
    },
    {
        "id": "SANC-003",
        "name": "Offshore Holding Ltd",
        "entity_type": "company",
        "category": "SANCTION",
        "country": "CY",
        "notes": "Entité juridique sous embargo et sanctions financières",
    },
    {
        "id": "SANC-004",
        "name": "Igor Ivanov",
        "entity_type": "individual",
        "category": "SANCTION",
        "country": "RU",
        "notes": "Individu sous sanctions de gels d'avoirs",
    },
    {
        "id": "PEP-005",
        "name": "Jean-Pierre Duval",
        "entity_type": "individual",
        "category": "PEP",
        "country": "FR",
        "notes": "Ancien membre de parlement",
    },
]


def normalize_name(value: str) -> str:
    decomposed = normalize("NFKD", value)
    without_accents = "".join(char for char in decomposed if not combining(char))
    return " ".join(without_accents.casefold().replace("-", " ").split())


def match_name(
    query_name: str,
    threshold: float = 85.0,
    watchlist: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    if not query_name or not query_name.strip():
        return []

    watchlist_to_search = LOCAL_WATCHLIST if watchlist is None else watchlist
    results = []

    clean_query = normalize_name(query_name)

    for item in watchlist_to_search:
        target_name = item["name"]
        clean_target = normalize_name(target_name)

        # Calcul des scores RapidFuzz
        ratio = fuzz.ratio(clean_query, clean_target)
        token_sort = fuzz.token_sort_ratio(clean_query, clean_target)
        wratio = fuzz.WRatio(clean_query, clean_target)

        max_score = max(ratio, token_sort, wratio)

        if max_score >= threshold:
            results.append(
                {
                    "watchlist_item": item,
                    "score": round(float(max_score), 2),
                    "ratio": round(float(ratio), 2),
                    "token_sort_ratio": round(float(token_sort), 2),
                    "wratio": round(float(wratio), 2),
                    "matched_name": target_name,
                }
            )

    # Trier par score décroissant
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
