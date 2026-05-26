from collections.abc import Generator

from sqlalchemy.orm import Session


def get_db() -> Generator[Session]:
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_session() -> Session:
    from app.db.session import SessionLocal

    return SessionLocal()
