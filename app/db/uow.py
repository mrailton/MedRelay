from __future__ import annotations

from sqlalchemy.orm import Session

COMMIT_KEY = "commit"


def mark_for_commit(db: Session) -> None:
    db.info[COMMIT_KEY] = True


def should_commit(db: Session) -> bool:
    return bool(db.info.pop(COMMIT_KEY, False))
