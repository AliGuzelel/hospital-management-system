from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/")
def auth_root():
    """Placeholder: auth routes (register, login, etc.) will live here."""
    return {"scope": "auth", "status": "stub"}
