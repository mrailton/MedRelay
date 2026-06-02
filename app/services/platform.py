from __future__ import annotations

from sqlalchemy.orm import Session

from app.observability.db_pool import get_db_pool_metrics
from app.realtime.hub import realtime_hub
from app.repositories import User
from app.repositories.organisation import OrganisationRepository


def user_can_access_platform(user: User, organisation_id: int, db: Session) -> bool:
    """Platform tools are for admins of the default organisation only."""
    default = OrganisationRepository(db).get_default()
    if not default or organisation_id != default.id:
        return False
    return user.is_admin(default.id)


def get_system_dashboard_context(db: Session) -> dict:
    return {
        "db_pool": get_db_pool_metrics(),
        "realtime": realtime_hub.status(),
    }
