from __future__ import annotations

import logging
from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.db.engine import create_app_engine
from app.db.uow import should_commit

logger = logging.getLogger(__name__)

settings = get_settings()
engine = create_app_engine(settings)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        try:
            if should_commit(db):
                db.commit()
            else:
                db.rollback()
        except Exception:
            logger.exception("Database transaction failed on session teardown")
            db.rollback()
            raise
        finally:
            db.close()


def create_session() -> Session:
    return SessionLocal()
