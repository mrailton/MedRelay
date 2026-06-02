from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.db.models.event import Event
from app.db.models.incident import Incident
from app.db.models.organisation import Organisation
from app.db.models.user import User
from app.repositories.organisation import OrganisationRepository
from app.security import hash_password


def create_organisation(
    db: Session,
    *,
    code: str = "default",
    name: str = "Default Organisation",
) -> Organisation:
    org = Organisation(
        code=code,
        name=name,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def create_user(
    db: Session,
    *,
    role: str = "CONTROLLER",
    email: str | None = None,
    password: str = "password",
    organisation: Organisation | None = None,
) -> User:
    user = User(
        name="Test User",
        email=email or f"user{db.query(User).count()}@example.com",
        password=hash_password(password),
        role=role,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(user)
    db.flush()
    if organisation:
        OrganisationRepository(db).add_user(user.id, organisation.id, role)
        db.flush()
    db.commit()
    db.refresh(user)
    return user


def create_event(db: Session, organisation: Organisation, **kwargs) -> Event:
    event = Event(
        organisation_id=organisation.id,
        name=kwargs.get("name", "Test Event"),
        location=kwargs.get("location", "Test Location"),
        start_time=kwargs.get("start_time", datetime.now(UTC)),
        is_active=kwargs.get("is_active", True),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def make_incident(db: Session, event: Event, **kwargs) -> Incident:
    incident = Incident(
        event_id=event.id,
        reference=kwargs.get("reference", "INC-001"),
        location=kwargs.get("location", "Loc"),
        priority=kwargs.get("priority", "P1"),
        category=kwargs.get("category", "medical"),
        description=kwargs.get("description", "Test"),
        status=kwargs.get("status", "NEW"),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident
