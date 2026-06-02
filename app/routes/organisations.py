from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.dependencies import DbSession, DefaultOrgAdminUser
from app.schemas.forms import OrganisationForm, organisation_form
from app.services.organisations import (
    create_organisation,
    get_organisation,
    list_organisations,
    update_organisation,
)
from app.templating import render
from app.web import handle, redirect_to, render_page, verified_form

router = APIRouter(prefix="/admin/organisations", tags=["admin"])


@router.get("", name="admin.organisations.index")
def admin_organisations_index(request: Request, user: DefaultOrgAdminUser, db: DbSession):
    organisations = list_organisations(db)
    return render(request, "admin/organisations/index.html", {"organisations": organisations}, user=user)


@router.get("/create", name="admin.organisations.create")
def admin_organisations_create(request: Request, user: DefaultOrgAdminUser, db: DbSession):
    return render(request, "admin/organisations/create.html", user=user)


@router.post("", name="admin.organisations.store")
def admin_organisations_store(
    request: Request,
    user: DefaultOrgAdminUser,
    db: DbSession,
    form: OrganisationForm = Depends(verified_form(organisation_form)),
):
    outcome = create_organisation(db, form.code, form.name)
    if not outcome.success:
        return handle(
            request,
            render_page(
                "admin/organisations/create.html",
                {"code": form.code, "name": form.name},
                errors=outcome.errors,
                user=user,
            ),
        )

    return handle(
        request,
        redirect_to(
            "/admin/organisations",
            commit=True,
            flash=("success", f"Organisation '{form.name}' created."),
        ),
        db=db,
    )


@router.get("/{organisation_id}/edit", name="admin.organisations.edit")
def admin_organisations_edit(request: Request, organisation_id: int, user: DefaultOrgAdminUser, db: DbSession):
    org = get_organisation(db, organisation_id)
    if not org:
        return handle(
            request,
            redirect_to("/admin/organisations", flash=("error", "Organisation not found.")),
        )
    return render(request, "admin/organisations/edit.html", {"org": org}, user=user)


@router.post("/{organisation_id}", name="admin.organisations.update")
def admin_organisations_update(
    request: Request,
    organisation_id: int,
    user: DefaultOrgAdminUser,
    db: DbSession,
    form: OrganisationForm = Depends(verified_form(organisation_form)),
):
    outcome = update_organisation(db, organisation_id, form.code, form.name)
    if outcome.not_found:
        return handle(
            request,
            redirect_to("/admin/organisations", flash=("error", "Organisation not found.")),
        )

    if not outcome.success:
        return handle(
            request,
            render_page(
                "admin/organisations/edit.html",
                {"org": outcome.organisation},
                errors=outcome.errors,
                user=user,
            ),
        )

    return handle(
        request,
        redirect_to(
            "/admin/organisations",
            commit=True,
            flash=("success", f"Organisation '{form.name}' updated."),
        ),
        db=db,
    )
