from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.dependencies import AdminUser, CurrentOrg, DbSession
from app.schemas.forms import AdminUserCreateForm, admin_user_create_form
from app.services.audit import count_audit_logs, list_audit_logs_paginated
from app.services.users import (
    create_admin_user,
    get_admin_user_create_context,
    list_users_for_organisation,
)
from app.templating import render
from app.web import handle, redirect_to, render_page, verified_form

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", name="admin.users.index")
def admin_users_index(request: Request, user: AdminUser, organisation_id: CurrentOrg, db: DbSession):
    users = list_users_for_organisation(db, organisation_id)
    return render(request, "admin/users/index.html", {"users": users}, user=user)


@router.get("/users/create", name="admin.users.create")
def admin_users_create(request: Request, user: AdminUser, organisation_id: CurrentOrg, db: DbSession):
    return render(
        request,
        "admin/users/create.html",
        get_admin_user_create_context(db, organisation_id),
        user=user,
    )


@router.post("/users", name="admin.users.store")
def admin_users_store(
    request: Request,
    user: AdminUser,
    organisation_id: CurrentOrg,
    db: DbSession,
    form: AdminUserCreateForm = Depends(verified_form(admin_user_create_form)),
):
    ctx = get_admin_user_create_context(db, organisation_id)
    outcome = create_admin_user(db, form, organisation_id, user, request)
    if not outcome.success:
        return handle(
            request,
            render_page(
                "admin/users/create.html",
                {**ctx, "name": form.name, "email": form.email},
                errors=outcome.errors,
                user=user,
            ),
        )

    return handle(
        request,
        redirect_to("/admin/users", commit=True, flash=("success", f"User '{form.name}' created.")),
        db=db,
    )


@router.get("/audit-logs", name="admin.audit-logs.index")
def admin_audit_logs(
    request: Request,
    user: AdminUser,
    organisation_id: CurrentOrg,
    db: DbSession,
    page: int = 1,
):
    per_page = 50
    total = count_audit_logs(db, organisation_id)
    logs = list_audit_logs_paginated(db, organisation_id, page, per_page)
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
