from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.dependencies import CurrentOrg, CurrentUser, DbSession, verify_csrf
from app.schemas.forms import DashboardSelectEventForm, dashboard_select_event_form
from app.services.dashboard import build_dashboard_context
from app.templating import render
from app.web import handle, redirect_to
from app.web.responses import ActionResult

router = APIRouter(tags=["dashboard"])


@router.api_route("/", methods=["GET", "POST"], name="dashboard")
def dashboard(
    request: Request,
    user: CurrentUser,
    db: DbSession,
    organisation_id: CurrentOrg,
    form: DashboardSelectEventForm = Depends(dashboard_select_event_form),
):
    if request.method == "POST" and form.selected_event_id is not None:
        verify_csrf(request, form.csrf_token)
        request.session["selected_event_id"] = int(form.selected_event_id)
        accept = request.headers.get("accept", "")
        if "application/json" in accept or request.headers.get("x-requested-with") == "XMLHttpRequest":
            return handle(request, ActionResult(empty_response=True))
        return handle(request, redirect_to("/"))

    selected_event_id = request.session.get("selected_event_id")
    context = build_dashboard_context(db, organisation_id, selected_event_id)
    return render(request, "dashboard.html", context, user=user)
