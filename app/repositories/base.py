from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from app.db.base import Base


class BaseRepository:
    model: type[Base]

    def __init__(self, db: Session):
        self.db = db
