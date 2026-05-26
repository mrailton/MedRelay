from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db.models.audit_log import AuditLog
from app.db.models.user import User
from app.db.session import get_db
from app.dependencies import AdminUser, verify_csrf
from app.enums import UserRole
from app.services.users import create_user
from app.templating import render

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", name="admin.users.index")
def admin_users_index(request: Request, user: AdminUser, db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.name).all()
    return render(request, "admin/users/index.html", {"users": users}, user=user)


@router.get("/users/create", name="admin.users.create")
def admin_users_create(request: Request, user: AdminUser):
    return render(request, "admin/users/create.html", {"roles": UserRole}, user=user)


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
    csrf_token: str | None = Form(None),
):
    verify_csrf(request, csrf_token)
    if password != password_confirmation:
        return render(
            request,
            "admin/users/create.html",
            {"roles": UserRole, "errors": {"password": "Passwords do not match."}},
            user=user,
        )
    if len(password) < 8:
        return render(
            request,
            "admin/users/create.html",
            {"roles": UserRole, "errors": {"password": "Password must be at least 8 characters."}},
            user=user,
        )
    if db.query(User).filter(User.email == email).first():
        return render(
            request,
            "admin/users/create.html",
            {"roles": UserRole, "errors": {"email": "Email already exists."}},
            user=user,
        )
    create_user(db, {"name": name, "email": email, "password": password, "role": role}, user, request)
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
    query = db.query(AuditLog).order_by(AuditLog.created_at.desc())
    total = query.count()
    logs = query.offset((page - 1) * per_page).limit(per_page).all()
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
