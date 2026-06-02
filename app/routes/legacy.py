from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(include_in_schema=False)


@router.get("/admin/organisations")
@router.get("/admin/organisations/create")
def redirect_admin_organisations_index():
    return RedirectResponse(url="/platform/organisations", status_code=303)


@router.post("/admin/organisations")
def redirect_admin_organisations_store():
    return RedirectResponse(url="/platform/organisations", status_code=303)


@router.get("/admin/organisations/{organisation_id}/edit")
def redirect_admin_organisations_edit(organisation_id: int):
    return RedirectResponse(url=f"/platform/organisations/{organisation_id}/edit", status_code=303)


@router.post("/admin/organisations/{organisation_id}")
def redirect_admin_organisations_update(organisation_id: int):
    return RedirectResponse(url=f"/platform/organisations/{organisation_id}", status_code=303)
