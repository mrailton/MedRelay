from starlette.requests import Request


def _make_request(path: str, route_name: str = "") -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "headers": [],
        "query_string": b"",
        "client": ("127.0.0.1", 8000),
        "route": type("R", (), {"name": route_name})(),
    }
    return Request(scope)


def test_route_is_dashboard():
    from app.templating import route_is

    request = _make_request("/")
    assert route_is(request, "dashboard") is True


def test_route_is_not_dashboard():
    from app.templating import route_is

    request = _make_request("/events")
    assert route_is(request, "dashboard") is False


def test_route_is_wildcard_match():
    from app.templating import route_is

    request = _make_request("/events/1/incidents", "events.incidents.index")
    assert route_is(request, "events.*") is True


def test_route_is_by_name():
    from app.templating import route_is

    request = _make_request("/incidents/1", "incidents.show")
    assert route_is(request, "incidents.show") is True


def test_route_is_fallback():
    from app.templating import route_is

    request = _make_request("/unknown", "some.route")
    assert route_is(request, "other.route") is False


def test_url_for_unknown_route():
    from app.templating import url_for

    try:
        url_for("nonexistent.route")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
