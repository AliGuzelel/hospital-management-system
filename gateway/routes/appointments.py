from fastapi import APIRouter

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("/")
def appointments_root():
    """Placeholder: appointment routes will live here."""
    return {"scope": "appointments", "status": "stub"}
