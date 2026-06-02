from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.web.csrf import verified_form
from app.web.entities import redirect_if_missing
from app.web.handlers import handle
from app.web.responses import ActionResult, redirect_to, render_page


def test_redirect_if_missing_returns_entity():
    assert redirect_if_missing("ok", "/") == "ok"


def test_redirect_if_missing_returns_action_result():
    result = redirect_if_missing(None, "/events")
    assert isinstance(result, ActionResult)
    assert result.redirect_url == "/events"


def test_handle_redirect_marks_db_for_commit(db_session):
    request = MagicMock()
    request.session = {}
    db = db_session
    response = handle(request, redirect_to("/done", commit=True), db=db)
    assert response.status_code == 303
    assert response.headers["location"] == "/done"
    from app.db.uow import COMMIT_KEY

    assert db.info[COMMIT_KEY] is True


def test_get_db_commits_when_marked(db_engine):
    from sqlalchemy.orm import sessionmaker

    from app.db.uow import mark_for_commit

    Session = sessionmaker(bind=db_engine)
    db = Session()
    mark_for_commit(db)
    from app.db.uow import should_commit

    assert should_commit(db) is True
    db.commit()
    db.close()


def test_render_page_carries_errors_and_status():
    result = render_page("auth/login.html", {"email": "a@b.com"}, errors={"email": "bad"})
    assert result.template == "auth/login.html"
    assert result.errors == {"email": "bad"}
    assert result.status_code == 200


def test_split_entity():
    from app.web.entities import split_entity

    miss, entity = split_entity(None, "/events")
    assert miss is not None
    assert miss.redirect_url == "/events"
    assert entity is None

    miss, entity = split_entity({"id": 1})
    assert miss is None
    assert entity == {"id": 1}


def test_handle_empty_response():
    request = MagicMock()
    request.session = {}
    response = handle(request, ActionResult(empty_response=True))
    assert response.status_code == 204


def test_handle_flash_on_redirect():
    request = MagicMock()
    request.session = {}
    response = handle(request, redirect_to("/x", flash=("success", "Done")))
    assert response.status_code == 303
    assert request.session["flash_success"] == "Done"


def test_verified_form_rejects_bad_csrf():
    from app.schemas.forms.auth import LogoutForm

    request = MagicMock()
    request.session = {"csrf_token": "good"}
    form = LogoutForm(csrf_token="bad")

    def logout_form_dep(csrf_token: str | None = None) -> LogoutForm:
        return LogoutForm(csrf_token=csrf_token)

    dep = verified_form(logout_form_dep)
    with pytest.raises(HTTPException) as exc:
        dep(request, form=form)
    assert exc.value.status_code == 403
