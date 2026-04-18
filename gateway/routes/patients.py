from fastapi import APIRouter

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/")
def patients_root():
    """Placeholder: patient CRUD proxies will live here."""
    return {"scope": "patients", "status": "stub"}
