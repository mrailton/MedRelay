from __future__ import annotations

from typing import Annotated

from fastapi import Form

from app.schemas.forms.base import CsrfForm


class DashboardSelectEventForm(CsrfForm):
    selected_event_id: int | None = None


def dashboard_select_event_form(
    selected_event_id: Annotated[int | None, Form()] = None,
    csrf_token: Annotated[str | None, Form()] = None,
) -> DashboardSelectEventForm:
    return DashboardSelectEventForm(selected_event_id=selected_event_id, csrf_token=csrf_token)
