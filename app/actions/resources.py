from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.resources import get_resource_with_details
from app.services.staff import list_staff_by_last_name
from app.web.responses import ActionResult, redirect_to, render_page


def show_page(
    db: Session,
    resource_id: int,
    organisation_id: int,
) -> ActionResult:
    resource = get_resource_with_details(db, resource_id, organisation_id)
    if not resource:
        return redirect_to("/")
    all_staff = list_staff_by_last_name(db, organisation_id)
    return render_page(
        "resources/show.html",
        {"resource": resource, "all_staff": all_staff},
    )
