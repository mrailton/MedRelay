from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app.dependencies import AdminUser, CurrentOrg, DbSession, verify_csrf
from app.enums import UserRole
from app.repositories.organisation import OrganisationRepository
from app.repositories.user import UserRepository
from app.schemas.forms import AdminUserCreateForm, admin_user_create_form
from app.services.audit import count_audit_logs, list_audit_logs_paginated
from app.services.users import create_user, get_user_by_email
from app.templating import flash, render

router = APIRouter(prefix="/admin", tags=["admin"])


def _admin_create_context(db: DbSession, organisation_id: int) -> dict:
    org = OrganisationRepository(db).get(organisation_id)
    return {
        "roles": UserRole,
        "organisations": [org] if org else [],
    }


@router.get("/users", name="admin.users.index")
def admin_users_index(request: Request, user: AdminUser, organisation_id: CurrentOrg, db: DbSession):
    users = UserRepository(db).list_all_by_organisation(organisation_id)
    return render(request, "admin/users/index.html", {"users": users}, user=user)


@router.get("/users/create", name="admin.users.create")
def admin_users_create(request: Request, user: AdminUser, organisation_id: CurrentOrg, db: DbSession):
    return render(request, "admin/users/create.html", _admin_create_context(db, organisation_id), user=user)


@router.post("/users", name="admin.users.store")
def admin_users_store(
    request: Request,
    user: AdminUser,
    organisation_id: CurrentOrg,
    db: DbSession,
    form: AdminUserCreateForm = Depends(admin_user_create_form),
):
    verify_csrf(request, form.csrf_token)
    ctx = _admin_create_context(db, organisation_id)

    org_ids = form.filtered_organisation_ids(organisation_id)
    if not org_ids:
        return render(
            request,
            "admin/users/create.html",
            {
                **ctx,
                "errors": {"organisation_ids": "You must assign the user to your organisation."},
                "name": form.name,
                "email": form.email,
            },
            user=user,
        )

    if form.password != form.password_confirmation:
        return render(
            request,
            "admin/users/create.html",
            {
                **ctx,
                "errors": {"password": "Passwords do not match."},
                "name": form.name,
                "email": form.email,
            },
            user=user,
        )

    if len(form.password) < 8:
        return render(
            request,
            "admin/users/create.html",
            {
                **ctx,
                "errors": {"password": "Password must be at least 8 characters."},
                "name": form.name,
                "email": form.email,
            },
            user=user,
        )

    if get_user_by_email(db, form.email):
        return render(
            request,
            "admin/users/create.html",
            {
                **ctx,
                "errors": {"email": "Email already exists."},
                "name": form.name,
                "email": form.email,
            },
            user=user,
        )

    create_user(db, form.to_service_dict(org_ids), user, request)
    db.commit()
    flash(request, "success", f"User '{form.name}' created.")
    return RedirectResponse(url="/admin/users", status_code=303)


@router.get("/audit-logs", name="admin.audit-logs.index")
def admin_audit_logs(request: Request, user: AdminUser, db: DbSession, page: int = 1):
    per_page = 50
    total = count_audit_logs(db)
    logs = list_audit_logs_paginated(db, page, per_page)
    return render(
        request,
        "admin/audit_logs/index.html",
        {
            "audit_logs": logs,
            "page": page,
            "total_pages": max(1, (total + per_page - 1) // per_page),
        },
        user=user,
    )
