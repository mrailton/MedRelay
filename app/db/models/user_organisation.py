from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table

from app.db.base import Base

user_organisation = Table(
    "user_organisation",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("organisation_id", Integer, ForeignKey("organisations.id", ondelete="CASCADE"), primary_key=True),
    Column("role", String(20), nullable=False),
    Column("created_at", DateTime, nullable=True),
    extend_existing=True,
)
