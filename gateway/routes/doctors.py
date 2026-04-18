from fastapi import APIRouter

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("/")
def doctors_root():
    """Placeholder: doctor CRUD proxies will live here."""
    return {"scope": "doctors", "status": "stub"}
