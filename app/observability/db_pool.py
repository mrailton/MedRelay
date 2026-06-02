from __future__ import annotations

from sqlalchemy.pool import QueuePool

from app.config import get_settings
from app.db.session import engine


def get_db_pool_metrics() -> dict[str, int | str | bool]:
    settings = get_settings()
    pool = engine.pool
    if not isinstance(pool, QueuePool):
        return {
            "backend": type(pool).__name__,
            "metrics_available": False,
        }

    return {
        "backend": "QueuePool",
        "metrics_available": True,
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "configured_pool_size": settings.db_pool_size,
        "configured_max_overflow": settings.db_max_overflow,
    }
