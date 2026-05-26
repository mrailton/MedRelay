from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from medrelay.db.base import Base
from medrelay.db.models.incident_resource import incident_resource
from medrelay.db.models.resource_staff import resource_staff


class Resource(Base):
    __tablename__ = "resources"
    __table_args__ = (UniqueConstraint("event_id", "name", name="resources_event_id_name_unique"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    resource_type: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="AVAILABLE")
    availability: Mapped[str] = mapped_column(String(20), default="AVAILABLE")
    highest_clinical_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_deployable: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime | None] = mapped_column(nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(nullable=True)

    event: Mapped["Event"] = relationship(back_populates="resources")
    staff: Mapped[list["Staff"]] = relationship(secondary=resource_staff, back_populates="resources")
    incidents: Mapped[list["Incident"]] = relationship(
        secondary=incident_resource, back_populates="resources"
    )
