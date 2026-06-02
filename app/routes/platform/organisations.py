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

router = APIRouter(prefix="/organisations")


@router.get("", name="platform.organisations.index")
def platform_organisations_index(request: Request, user: DefaultOrgAdminUser, db: DbSession):
    organisations = list_organisations(db)
    return render(
        request,
        "platform/organisations/index.html",
        {"organisations": organisations},
        user=user,
    )


@router.get("/create", name="platform.organisations.create")
def platform_organisations_create(request: Request, user: DefaultOrgAdminUser, db: DbSession):
    return render(request, "platform/organisations/create.html", user=user)


@router.post("", name="platform.organisations.store")
def platform_organisations_store(
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
                "platform/organisations/create.html",
                {"code": form.code, "name": form.name},
                errors=outcome.errors,
                user=user,
            ),
        )

    return handle(
        request,
        redirect_to(
            "/platform/organisations",
            commit=True,
            flash=("success", f"Organisation '{form.name}' created."),
        ),
        db=db,
    )


@router.get("/{organisation_id}/edit", name="platform.organisations.edit")
def platform_organisations_edit(
    request: Request,
    organisation_id: int,
    user: DefaultOrgAdminUser,
    db: DbSession,
):
    org = get_organisation(db, organisation_id)
    if not org:
        return handle(
            request,
            redirect_to("/platform/organisations", flash=("error", "Organisation not found.")),
        )
    return render(request, "platform/organisations/edit.html", {"org": org}, user=user)


@router.post("/{organisation_id}", name="platform.organisations.update")
def platform_organisations_update(
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
            redirect_to("/platform/organisations", flash=("error", "Organisation not found.")),
        )

    if not outcome.success:
        return handle(
            request,
            render_page(
                "platform/organisations/edit.html",
                {"org": outcome.organisation},
                errors=outcome.errors,
                user=user,
            ),
        )

    return handle(
        request,
        redirect_to(
            "/platform/organisations",
            commit=True,
            flash=("success", f"Organisation '{form.name}' updated."),
        ),
        db=db,
    )
