from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/up", name="up")
def health():
    return {"status": "ok"}
