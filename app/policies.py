from __future__ import annotations

from app.enums import UserRole
from app.repositories import Event, Incident, Resource, Staff, User


class AuthorizationError(Exception):
    """Raised when a user is not allowed to perform an action."""


def authorize(
    user: User,
    action: str,
    subject: str | None = None,
    obj=None,
    *,
    organisation_id: int | None = None,
) -> None:
    if not can(user, action, subject, obj, organisation_id=organisation_id):
        raise AuthorizationError(f"Not allowed: {action} on {subject}")


def _is_controller_or_admin(user: User, organisation_id: int | None = None) -> bool:
    role = user.get_role(organisation_id) if organisation_id else user.user_role
    return role in (UserRole.ADMIN, UserRole.CONTROLLER)


def can_view_any_event(user: User, organisation_id: int | None = None) -> bool:
    return True


def can_create_event(user: User, organisation_id: int | None = None) -> bool:
    return _is_controller_or_admin(user, organisation_id)


def can_update_event(user: User, event: Event, organisation_id: int | None = None) -> bool:
    return _is_controller_or_admin(user, organisation_id)


def can_delete_event(user: User, event: Event, organisation_id: int | None = None) -> bool:
    return user.is_admin(organisation_id)


def can_create_incident(user: User, organisation_id: int | None = None) -> bool:
    return _is_controller_or_admin(user, organisation_id)


def can_update_incident(user: User, incident: Incident, organisation_id: int | None = None) -> bool:
    return _is_controller_or_admin(user, organisation_id)


def can_update_incident_status(user: User, incident: Incident, organisation_id: int | None = None) -> bool:
    return _is_controller_or_admin(user, organisation_id)


def can_assign_resource(user: User, incident: Incident, organisation_id: int | None = None) -> bool:
    return _is_controller_or_admin(user, organisation_id)


def can_create_resource(user: User, organisation_id: int | None = None) -> bool:
    return _is_controller_or_admin(user, organisation_id)


def can_update_resource(user: User, resource: Resource, organisation_id: int | None = None) -> bool:
    return _is_controller_or_admin(user, organisation_id)


def can_create_staff(user: User, organisation_id: int | None = None) -> bool:
    return _is_controller_or_admin(user, organisation_id)


def can_update_staff(user: User, staff: Staff, organisation_id: int | None = None) -> bool:
    return _is_controller_or_admin(user, organisation_id)


def can_view_any_user(user: User, organisation_id: int | None = None) -> bool:
    return user.is_admin(organisation_id)


def can_create_user(user: User, organisation_id: int | None = None) -> bool:
    return user.is_admin(organisation_id)


def can(user: User, action: str, subject: str | None = None, obj=None, *, organisation_id: int | None = None) -> bool:
    """Jinja-friendly policy check mirroring Laravel Gate::authorize patterns."""
    if action == "admin-only":
        return user.is_admin(organisation_id)

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
