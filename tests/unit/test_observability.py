from app.observability.db_pool import get_db_pool_metrics


def test_db_pool_metrics_in_testing():
    metrics = get_db_pool_metrics()
    assert "backend" in metrics
    assert metrics.get("metrics_available") is True or metrics.get("metrics_available") is False
