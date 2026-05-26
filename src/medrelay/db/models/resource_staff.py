from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Table, Column, Integer

from medrelay.db.base import Base

resource_staff = Table(
    "resource_staff",
    Base.metadata,
    Column("resource_id", Integer, ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True),
    Column("staff_id", Integer, ForeignKey("staff.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime, nullable=True),
    Column("updated_at", DateTime, nullable=True),
)
