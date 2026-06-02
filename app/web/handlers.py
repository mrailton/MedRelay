from __future__ import annotations

from typing import cast

from fastapi import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.db.uow import mark_for_commit
from app.templating import flash, render
from app.web.responses import ActionResult


def handle(
    request: Request,
    result: ActionResult,
    *,
    db: Session | None = None,
    user=None,
) -> Response:
    if result.flash:
        flash(request, result.flash[0], result.flash[1])

    if result.empty_response:
        return Response(status_code=204)

    if result.redirect_url is not None:
        if result.commit and db is not None:
            mark_for_commit(db)
        return RedirectResponse(url=result.redirect_url, status_code=result.status_code)

    if result.template is not None:
        ctx = dict(result.context or {})
        if result.errors:
            ctx["errors"] = result.errors
        return cast(
            Response,
            render(
                request,
                result.template,
                ctx,
                user=result.user if result.user is not None else user,
                status_code=result.status_code,
            ),
        )

    raise ValueError("ActionResult must set redirect_url, template, or empty_response")
