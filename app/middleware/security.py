from typing import cast

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import get_settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add baseline security headers for HTML responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = cast(Response, await call_next(request))
        settings = get_settings()

        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")

        if settings.is_production:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")

        return response
