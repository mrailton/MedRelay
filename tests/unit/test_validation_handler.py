import asyncio

from fastapi.exceptions import RequestValidationError

from app.handlers.validation import request_validation_exception_handler


def _make_request(*, accept: str = "text/html", referer: str | None = None):
    headers = [(b"accept", accept.encode())]
    if referer:
        headers.append((b"referer", referer.encode()))
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/events",
        "headers": headers,
        "scheme": "http",
        "server": ("testserver", 80),
        "client": ("127.0.0.1", 12345),
    }
    from starlette.requests import Request

    request = Request(scope)
    request.scope["session"] = {}
    return request


def test_html_validation_redirects_with_session_errors():
    request = _make_request(referer="http://testserver/events/create")
    exc = RequestValidationError(
        [
            {
                "type": "string_too_short",
                "loc": ("body", "name"),
                "msg": "String should have at least 1 characters",
                "input": "",
            }
        ]
    )
    response = asyncio.run(request_validation_exception_handler(request, exc))
    assert response.status_code == 303
    assert request.session.get("validation_errors") == {"name": "String should have at least 1 characters"}
    assert request.session.get("error")


def test_json_validation_returns_422():
    request = _make_request(accept="application/json")
    exc = RequestValidationError([{"type": "missing", "loc": ("body", "name"), "msg": "Field required", "input": None}])
    response = asyncio.run(request_validation_exception_handler(request, exc))
    assert response.status_code == 422
