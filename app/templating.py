from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app import policies
from app.dependencies import get_csrf_token
from app.enums import ClinicalLevel, IncidentStatus, ResourceStatus, ResourceType, UserRole

TEMPLATES_DIR = Path(__file__).parent / "templates"
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


def flash(request: Request, category: str, message: str) -> None:
    request.session[f"flash_{category}"] = message


def render(request: Request, name: str, context: dict | None = None, user=None):
    ctx = {
        "request": request,
        "csrf_token": get_csrf_token(request),
        "user": user,
        "errors": {},
        "current_org_id": request.session.get("organisation_id"),
        "current_org_code": request.session.get("organisation_code"),
    }
    for key in ("success", "error"):
        if key in request.session:
            ctx[key] = request.session.pop(f"flash_{key}", request.session.pop(key, None))
    if "validation_errors" in request.session:
        ctx["errors"] = request.session.pop("validation_errors")
    if context:
        ctx.update(context)
    return templates.TemplateResponse(request, name, ctx)
