from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app.dependencies import DbSession, DefaultOrgAdminUser, verify_csrf
from app.repositories.organisation import OrganisationRepository
from app.schemas.forms import OrganisationForm, organisation_form
from app.templating import flash, render

router = APIRouter(prefix="/admin/organisations", tags=["admin"])


@router.get("", name="admin.organisations.index")
def admin_organisations_index(request: Request, user: DefaultOrgAdminUser, db: DbSession):
    organisations = OrganisationRepository(db).list_all()
    return render(request, "admin/organisations/index.html", {"organisations": organisations}, user=user)


@router.get("/create", name="admin.organisations.create")
def admin_organisations_create(request: Request, user: DefaultOrgAdminUser, db: DbSession):
    return render(request, "admin/organisations/create.html", user=user)


@router.post("", name="admin.organisations.store")
def admin_organisations_store(
    request: Request,
    user: DefaultOrgAdminUser,
    db: DbSession,
    form: OrganisationForm = Depends(organisation_form),
):
    verify_csrf(request, form.csrf_token)
    org_repo = OrganisationRepository(db)

    if org_repo.get_by_code(form.code):
        return render(
            request,
            "admin/organisations/create.html",
            {"errors": {"code": "Organisation with this code already exists."}, "code": form.code, "name": form.name},
            user=user,
        )

    org_repo.create(code=form.code, name=form.name)
    db.commit()
    flash(request, "success", f"Organisation '{form.name}' created.")
    return RedirectResponse(url="/admin/organisations", status_code=303)


@router.get("/{organisation_id}/edit", name="admin.organisations.edit")
def admin_organisations_edit(request: Request, organisation_id: int, user: DefaultOrgAdminUser, db: DbSession):
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
    db: DbSession,
    form: OrganisationForm = Depends(organisation_form),
):
    verify_csrf(request, form.csrf_token)
    org_repo = OrganisationRepository(db)

    existing = org_repo.get_by_code(form.code)
    if existing and existing.id != organisation_id:
        return render(
            request,
            "admin/organisations/edit.html",
            {"org": org_repo.get(organisation_id), "errors": {"code": "Organisation with this code already exists."}},
            user=user,
        )

    org = org_repo.update(organisation_id, code=form.code, name=form.name)
    if not org:
        flash(request, "error", "Organisation not found.")
        return RedirectResponse(url="/admin/organisations", status_code=303)

    db.commit()
    flash(request, "success", f"Organisation '{form.name}' updated.")
    return RedirectResponse(url="/admin/organisations", status_code=303)
