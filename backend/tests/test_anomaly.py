from app.services.anomaly import detect_demo_anomalies


def test_isolation_forest_demo_is_deterministic_and_flags_anomalies() -> None:
    first = detect_demo_anomalies()
    second = detect_demo_anomalies()

    assert first == second
    assert len(first) == 12
    assert all(0 <= point.score <= 100 for point in first)
    assert any(point.is_anomaly for point in first)
    assert all(point.id.startswith("SIM-") for point in first)
