from fastapi import APIRouter, Depends

from app.dependencies import require_default_org_admin

router = APIRouter(
    prefix="/platform",
    tags=["platform"],
    dependencies=[Depends(require_default_org_admin)],
)

from app.routes.platform import organisations, system  # noqa: E402, F401

router.include_router(organisations.router)
router.include_router(system.router)
