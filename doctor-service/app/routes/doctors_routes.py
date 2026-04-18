from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.doctor import DoctorCreate, DoctorUpdate, DoctorOut
from app.services.doctor_service import DoctorService

router = APIRouter(prefix="/doctors", tags=["doctors"])

@router.post("", response_model=DoctorOut)
def create_item(data: DoctorCreate, db: Session = Depends(get_db)):
    return DoctorService.create(db, data)

@router.get("/{item_id}", response_model=DoctorOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = DoctorService.get(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item

@router.put("/{item_id}", response_model=DoctorOut)
def update_item(item_id: int, data: DoctorUpdate, db: Session = Depends(get_db)):
    item = DoctorService.update(db, item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item
