from fastapi import APIRouter

from app.routes import admin, auth, dashboard, events, health, incidents, legacy, platform, realtime, resources, staff

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(events.router)
api_router.include_router(incidents.router)
api_router.include_router(resources.router)
api_router.include_router(staff.router)
api_router.include_router(admin.router)
api_router.include_router(platform.router)
api_router.include_router(legacy.router)
api_router.include_router(realtime.router)
