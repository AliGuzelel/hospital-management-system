from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.patient import PatientCreate, PatientUpdate, PatientOut
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["patients"])

@router.post("", response_model=PatientOut)
def create_item(data: PatientCreate, db: Session = Depends(get_db)):
    return PatientService.create(db, data)

@router.get("/{item_id}", response_model=PatientOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = PatientService.get(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item

@router.put("/{item_id}", response_model=PatientOut)
def update_item(item_id: int, data: PatientUpdate, db: Session = Depends(get_db)):
    item = PatientService.update(db, item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item
