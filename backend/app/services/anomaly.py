from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import IsolationForest


@dataclass(frozen=True)
class AnomalyPoint:
    id: str
    amount: float
    hour: float
    country_risk: float
    frequency_24h: float
    score: float
    is_anomaly: bool


def detect_demo_anomalies() -> list[AnomalyPoint]:
    """Run IsolationForest on deterministic simulated transaction features.

    This is deliberately a demo-only dataset: no real customer data is used.
    Higher score means a more unusual observation on a 0-100 scale.
    """
    raw = np.array(
        [
            [120_000, 10, 0.0, 1],
            [180_000, 11, 0.0, 2],
            [220_000, 13, 0.1, 2],
            [150_000, 9, 0.0, 1],
            [260_000, 14, 0.1, 2],
            [340_000, 15, 0.2, 3],
            [3_800_000, 2, 1.0, 11],
            [190_000, 12, 0.0, 2],
            [240_000, 16, 0.1, 2],
            [4_200_000, 3, 1.0, 13],
            [175_000, 10, 0.0, 1],
            [290_000, 17, 0.2, 3],
        ],
        dtype=float,
    )

    model = IsolationForest(
        n_estimators=150,
        contamination=0.16,
        random_state=42,
    )
    model.fit(raw)

    raw_scores = -model.score_samples(raw)
    low = float(raw_scores.min())
    high = float(raw_scores.max())
    span = high - low or 1.0

    result: list[AnomalyPoint] = []
    for index, (features, raw_score) in enumerate(zip(raw, raw_scores)):
        normalized = round(((float(raw_score) - low) / span) * 100, 1)
        result.append(
            AnomalyPoint(
                id=f"SIM-{index + 1:02d}",
                amount=float(features[0]),
                hour=float(features[1]),
                country_risk=float(features[2]),
                frequency_24h=float(features[3]),
                score=normalized,
                is_anomaly=normalized >= 75.0,
            )
        )
    return result
