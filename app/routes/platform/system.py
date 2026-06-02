from __future__ import annotations

from fastapi import APIRouter, Request

from app.dependencies import DbSession, DefaultOrgAdminUser
from app.services.platform import get_system_dashboard_context
from app.templating import render

router = APIRouter()


@router.get("/system", name="platform.system")
def platform_system(request: Request, user: DefaultOrgAdminUser, db: DbSession):
    return render(
        request,
        "platform/system/index.html",
        get_system_dashboard_context(db),
        user=user,
    )
