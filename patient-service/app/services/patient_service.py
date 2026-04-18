from sqlalchemy.orm import Session
from app.models.patient import Patient

class PatientService:
    @staticmethod
    def create(db: Session, data):
        obj = Patient(**data.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    @staticmethod
    def get(db: Session, item_id: int):
        return db.query(Patient).filter(Patient.id == item_id).first()
    @staticmethod
    def update(db: Session, item_id: int, data):
        obj = db.query(Patient).filter(Patient.id == item_id).first()
        if not obj:
            return None
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
        return obj
