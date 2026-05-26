from app.db.models.event import Event
from app.db.models.incident import Incident
from app.db.models.resource import Resource
from app.db.models.staff import Staff
from app.db.models.user import User
from app.enums import UserRole


def _is_controller_or_admin(user: User) -> bool:
    return user.user_role in (UserRole.ADMIN, UserRole.CONTROLLER)


def can_view_any_event(user: User) -> bool:
    return True


def can_create_event(user: User) -> bool:
    return _is_controller_or_admin(user)


def can_update_event(user: User, event: Event) -> bool:
    return _is_controller_or_admin(user)


def can_delete_event(user: User, event: Event) -> bool:
    return user.user_role == UserRole.ADMIN


def can_create_incident(user: User) -> bool:
    return _is_controller_or_admin(user)


def can_update_incident(user: User, incident: Incident) -> bool:
    return _is_controller_or_admin(user)


def can_update_incident_status(user: User, incident: Incident) -> bool:
    return _is_controller_or_admin(user)


def can_assign_resource(user: User, incident: Incident) -> bool:
    return _is_controller_or_admin(user)


def can_create_resource(user: User) -> bool:
    return _is_controller_or_admin(user)


def can_update_resource(user: User, resource: Resource) -> bool:
    return _is_controller_or_admin(user)


def can_create_staff(user: User) -> bool:
    return _is_controller_or_admin(user)


def can_update_staff(user: User, staff: Staff) -> bool:
    return _is_controller_or_admin(user)


def can_view_any_user(user: User) -> bool:
    return user.is_admin()


def can_create_user(user: User) -> bool:
    return user.is_admin()


def can(user: User, action: str, subject: str | None = None, obj=None) -> bool:
    """Jinja-friendly policy check mirroring Laravel Gate::authorize patterns."""
    if action == "admin-only":
        return user.is_admin()

    mapping: dict[tuple[str, str | None], bool] = {
        ("viewAny", "event"): can_view_any_event(user),
        ("create", "event"): can_create_event(user),
        ("create", "incident"): can_create_incident(user),
        ("create", "resource"): can_create_resource(user),
        ("create", "staff"): can_create_staff(user),
        ("viewAny", "user"): can_view_any_user(user),
        ("create", "user"): can_create_user(user),
    }

    if subject is None:
        return mapping.get((action, None), False)

    key = (action, subject)
    if key in mapping:
        return mapping[key]

    if obj is None:
        return mapping.get(key, False)

    if subject == "event" and action == "update":
        return can_update_event(user, obj)
    if subject == "incident" and obj is not None:
        if action == "updateStatus":
            return can_update_incident_status(user, obj)
        if action == "assignResource":
            return can_assign_resource(user, obj)
        if action == "update":
            return can_update_incident(user, obj)
    if subject == "resource" and action == "update":
        return can_update_resource(user, obj)

    return False
