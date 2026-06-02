from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.config import Settings


def create_app_engine(settings: Settings) -> Engine:
    url = settings.database_url
    kwargs: dict = {
        "pool_pre_ping": True,
        "echo": settings.app_debug and not settings.is_testing,
    }
    if url.startswith("sqlite"):
        if ":memory:" in url or url.rstrip("/").endswith("sqlite://"):
            kwargs["connect_args"] = {"check_same_thread": False}
    else:
        kwargs.update(
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_recycle=settings.db_pool_recycle,
            pool_timeout=settings.db_pool_timeout,
        )
    return create_engine(url, **kwargs)
