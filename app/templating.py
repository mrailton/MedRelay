from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app import policies
from app.dependencies import get_csrf_token
from app.enums import ClinicalLevel, IncidentStatus, ResourceStatus, ResourceType, UserRole

TEMPLATES_DIR = Path(__file__).parent / "resources" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

_route_names: dict[str, str] = {}


def register_route_names(routes: list) -> None:
    for route in routes:
        name = getattr(route, "name", None)
        path = getattr(route, "path", None)
        if name and path:
            _route_names[name] = path


def url_for(name: str, **path_params: object) -> str:
    path = _route_names.get(name)
    if path is None:
        raise ValueError(f"Unknown route name: {name}")
    for key, value in path_params.items():
        placeholder = "{" + key + "}"
        if placeholder in path:
            path = path.replace(placeholder, str(value))
    return path


def route_is(request: Request, pattern: str) -> bool:
    path = request.url.path
    name = getattr(request.scope.get("route"), "name", "") or ""
    if pattern == "dashboard":
        return path == "/"
    if pattern.endswith(".*"):
        prefix = "/" + pattern[:-2].replace(".", "/")
        return path.startswith(prefix)
    return name == pattern or name.startswith(pattern.replace(".*", ""))


def setup_template_globals() -> None:
    templates.env.globals.update(
        {
            "url_for": url_for,
            "route_is": route_is,
            "can": policies.can,
            "UserRole": UserRole,
            "IncidentStatus": IncidentStatus,
            "ResourceStatus": ResourceStatus,
            "ResourceType": ResourceType,
            "ClinicalLevel": ClinicalLevel,
        }
    )


def _is_platform_admin(user, request: Request) -> bool:
    """True when the user is an admin of the default org in the current session."""
    org_id = request.session.get("organisation_id")
    if user is None or org_id is None:
        return False
    if request.session.get("organisation_code") != "default":
        return False
    return bool(user.is_admin(org_id))


def flash(request: Request, category: str, message: str) -> None:
    request.session[f"flash_{category}"] = message


def render(
    request: Request,
    name: str,
    context: dict | None = None,
    user=None,
    status_code: int = 200,
):
    ctx = {
        "request": request,
        "csrf_token": get_csrf_token(request),
        "user": user,
        "errors": {},
        "current_org_id": request.session.get("organisation_id"),
        "current_org_code": request.session.get("organisation_code"),
        "is_platform_admin": _is_platform_admin(user, request),
    }
    for key in ("success", "error"):
        if key in request.session:
            ctx[key] = request.session.pop(f"flash_{key}", request.session.pop(key, None))
    if "validation_errors" in request.session:
        ctx["errors"] = request.session.pop("validation_errors")
    if context:
        ctx.update(context)
    return templates.TemplateResponse(request, name, ctx, status_code=status_code)
