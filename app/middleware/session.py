import re
from typing import cast

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RememberSessionMiddleware(BaseHTTPMiddleware):
    """Extend session cookie Max-Age when the user checked 'Remember me' at login."""

    def __init__(self, app, *, remember_max_age_seconds: int) -> None:
        super().__init__(app)
        self.remember_max_age_seconds = remember_max_age_seconds

    async def dispatch(self, request: Request, call_next) -> Response:
        response = cast(Response, await call_next(request))
        if not request.session.get("remember_me"):
            return response

        cookie = response.headers.get("set-cookie")
        if not cookie or not cookie.lower().startswith("session="):
            return response

        if re.search(r"[Mm]ax-[Aa]ge=\d+", cookie):
            cookie = re.sub(
                r"[Mm]ax-[Aa]ge=\d+",
                f"Max-Age={self.remember_max_age_seconds}",
                cookie,
                count=1,
            )
        else:
            cookie = f"{cookie}; Max-Age={self.remember_max_age_seconds}"

        response.headers["set-cookie"] = cookie
        return response
