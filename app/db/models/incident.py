from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.incident_resource import incident_resource

if TYPE_CHECKING:
    from app.db.models.event import Event
    from app.db.models.incident_note import IncidentNote
    from app.db.models.resource import Resource


class Incident(Base):
    __tablename__ = "incidents"
    __table_args__ = (UniqueConstraint("event_id", "reference", name="incidents_event_id_reference_unique"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    reference: Mapped[str] = mapped_column(String(255))
    location: Mapped[str] = mapped_column(String(255))
    priority: Mapped[str] = mapped_column(String(10))
    category: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="NEW")
    created_at: Mapped[datetime | None] = mapped_column(nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(nullable=True)

    event: Mapped[Event] = relationship(back_populates="incidents")
    resources: Mapped[list[Resource]] = relationship(secondary=incident_resource, back_populates="incidents")
    notes: Mapped[list[IncidentNote]] = relationship(back_populates="incident")
