from __future__ import annotations

from urllib.parse import urlparse

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.requests import Request


def _format_validation_errors(exc: RequestValidationError) -> dict[str, str]:
    errors: dict[str, str] = {}
    for err in exc.errors():
        loc = err.get("loc", ())
        field = loc[-1] if loc else "form"
        if field == "body":
            field = "form"
        msg = err.get("msg", "Invalid value")
        key = str(field)
        if key not in errors:
            errors[key] = msg
    return errors


def _wants_html(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    return "text/html" in accept or "*/*" in accept or not accept.strip()


async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    if not _wants_html(request):
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    request.session["validation_errors"] = _format_validation_errors(exc)
    request.session["error"] = "Please correct the highlighted fields and try again."

    referer = request.headers.get("referer")
    redirect_to = "/"
    if referer:
        ref = urlparse(referer)
        base = urlparse(str(request.base_url))
        if ref.netloc == base.netloc:
            redirect_to = referer
    return RedirectResponse(url=redirect_to, status_code=303)
