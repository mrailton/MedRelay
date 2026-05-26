from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from app.db.base import Base


class BaseRepository:
    model: type[Base]

    def __init__(self, db: Session):
        self.db = db

    def add(self, instance: object) -> None:
        self.db.add(instance)

    def flush(self) -> None:
        self.db.flush()

    def refresh(self, instance: object, attribute_names: list[str] | None = None) -> None:
        self.db.refresh(instance, attribute_names=attribute_names)
