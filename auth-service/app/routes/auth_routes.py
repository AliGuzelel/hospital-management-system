from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = AuthService.register(db, data.username, data.password, data.role)
        return {"id": user.id, "username": user.username, "role": user.role}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    try:
        token, role = AuthService.login(db, data.username, data.password)
        return {"access_token": token, "token_type": "bearer", "role": role}
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

@router.get("/validate")
def validate(token: str):
    try:
        payload = AuthService.validate(token)
        return {"valid": True, "username": payload["sub"], "role": payload["role"]}
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
