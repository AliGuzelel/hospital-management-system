from enum import Enum

from pydantic import BaseModel, Field


class Role(str, Enum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=8, max_length=128)
    role: Role


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    role: str
    user_id: int


class UserOut(BaseModel):
    id: int
    username: str
    role: str

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    detail: str
