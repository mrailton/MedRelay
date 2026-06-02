from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import DefaultOrgAdminUser, verify_csrf
from app.repositories.organisation import OrganisationRepository
from app.repositories.session import get_db
from app.templating import flash, render

if TYPE_CHECKING:
    pass

router = APIRouter(prefix="/admin/organisations", tags=["admin"])


@router.get("", name="admin.organisations.index")
def admin_organisations_index(request: Request, user: DefaultOrgAdminUser, db: Session = Depends(get_db)):
    organisations = OrganisationRepository(db).list_all()
    return render(request, "admin/organisations/index.html", {"organisations": organisations}, user=user)


@router.get("/create", name="admin.organisations.create")
def admin_organisations_create(request: Request, user: DefaultOrgAdminUser, db: Session = Depends(get_db)):
    return render(request, "admin/organisations/create.html", user=user)


@router.post("", name="admin.organisations.store")
def admin_organisations_store(
    request: Request,
    user: DefaultOrgAdminUser,
    db: Session = Depends(get_db),
    code: str = Form(...),
    name: str = Form(...),
    csrf_token: str | None = Form(None),
):
    verify_csrf(request, csrf_token)
    org_repo = OrganisationRepository(db)

    if org_repo.get_by_code(code):
        return render(
            request,
            "admin/organisations/create.html",
            {"errors": {"code": "Organisation with this code already exists."}, "code": code, "name": name},
            user=user,
        )

    org_repo.create(code=code, name=name)
    db.commit()
    flash(request, "success", f"Organisation '{name}' created.")
    return RedirectResponse(url="/admin/organisations", status_code=303)


@router.get("/{organisation_id}/edit", name="admin.organisations.edit")
def admin_organisations_edit(
    request: Request,
    organisation_id: int,
    user: DefaultOrgAdminUser,
    db: Session = Depends(get_db),
):
    org = OrganisationRepository(db).get(organisation_id)
    if not org:
        flash(request, "error", "Organisation not found.")
        return RedirectResponse(url="/admin/organisations", status_code=303)
    return render(request, "admin/organisations/edit.html", {"org": org}, user=user)


@router.post("/{organisation_id}", name="admin.organisations.update")
def admin_organisations_update(
    request: Request,
    organisation_id: int,
    user: DefaultOrgAdminUser,
    db: Session = Depends(get_db),
    code: str = Form(...),
    name: str = Form(...),
    csrf_token: str | None = Form(None),
):
    verify_csrf(request, csrf_token)
    org_repo = OrganisationRepository(db)

    existing = org_repo.get_by_code(code)
    if existing and existing.id != organisation_id:
        return render(
            request,
            "admin/organisations/edit.html",
            {"org": org_repo.get(organisation_id), "errors": {"code": "Organisation with this code already exists."}},
            user=user,
        )

    org = org_repo.update(organisation_id, code=code, name=name)
    if not org:
        flash(request, "error", "Organisation not found.")
        return RedirectResponse(url="/admin/organisations", status_code=303)

    db.commit()
    flash(request, "success", f"Organisation '{name}' updated.")
    return RedirectResponse(url="/admin/organisations", status_code=303)
