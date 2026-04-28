from datetime import datetime, timedelta, timezone
import base64
import hashlib
import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.config.settings import settings
from app.models.user import User

ROLES = {"admin", "doctor", "patient"}


def _bcrypt_input(password: str) -> bytes:
    # Hash to fixed length first so bcrypt can safely support long passwords.
    return base64.b64encode(hashlib.sha256(password.encode("utf-8")).digest())


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(_bcrypt_input(password), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(_bcrypt_input(password), password_hash.encode("utf-8"))

class AuthService:
    @staticmethod
    def register(db: Session, username: str, password: str, role: str):
        if role not in ROLES:
            raise ValueError("Invalid role")
        if db.query(User).filter(User.username == username).first():
            raise ValueError("Username already exists")
        user = User(username=username, hashed_password=_hash_password(password), role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def login(db: Session, username: str, password: str):
        user = db.query(User).filter(User.username == username).first()
        if not user or not _verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")
        exp = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        token = jwt.encode({"sub": user.username, "role": user.role, "exp": exp}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        return token, user.role

    @staticmethod
    def validate(token: str):
        try:
            return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        except JWTError as exc:
            raise ValueError("Invalid token") from exc
