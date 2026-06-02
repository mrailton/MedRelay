from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import AdminUser, verify_csrf
from app.enums import UserRole
from app.repositories.organisation import OrganisationRepository
from app.repositories.session import get_db
from app.services.audit import count_audit_logs, list_audit_logs_paginated
from app.services.users import create_user, get_user_by_email, list_users
from app.templating import render

if TYPE_CHECKING:
    pass

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", name="admin.users.index")
def admin_users_index(request: Request, user: AdminUser, db: Session = Depends(get_db)):
    users = list_users(db)
    return render(request, "admin/users/index.html", {"users": users}, user=user)


@router.get("/users/create", name="admin.users.create")
def admin_users_create(request: Request, user: AdminUser, db: Session = Depends(get_db)):
    organisations = OrganisationRepository(db).list_all()
    return render(request, "admin/users/create.html", {"roles": UserRole, "organisations": organisations}, user=user)


@router.post("/users", name="admin.users.store")
def admin_users_store(
    request: Request,
    user: AdminUser,
    db: Session = Depends(get_db),
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirmation: str = Form(...),
    role: str = Form(...),
    organisation_ids: list[int] = Form(default=[]),
    csrf_token: str | None = Form(None),
):
    verify_csrf(request, csrf_token)
    if password != password_confirmation:
        return render(
            request,
            "admin/users/create.html",
            {"roles": UserRole, "organisations": OrganisationRepository(db).list_all(), "errors": {"password": "Passwords do not match."}},
            user=user,
        )
    if len(password) < 8:
        return render(
            request,
            "admin/users/create.html",
            {"roles": UserRole, "organisations": OrganisationRepository(db).list_all(), "errors": {"password": "Password must be at least 8 characters."}},
            user=user,
        )
    if get_user_by_email(db, email):
        return render(
            request,
            "admin/users/create.html",
            {"roles": UserRole, "organisations": OrganisationRepository(db).list_all(), "errors": {"email": "Email already exists."}},
            user=user,
        )
    create_user(db, {"name": name, "email": email, "password": password, "role": role, "organisation_ids": organisation_ids}, user, request)
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)


@router.get("/audit-logs", name="admin.audit-logs.index")
def admin_audit_logs(
    request: Request,
    user: AdminUser,
    db: Session = Depends(get_db),
    page: int = 1,
):
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
