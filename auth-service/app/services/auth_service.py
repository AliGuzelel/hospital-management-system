from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.config.settings import settings
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ROLES = {"admin", "doctor", "patient"}

class AuthService:
    @staticmethod
    def register(db: Session, username: str, password: str, role: str):
        if role not in ROLES:
            raise ValueError("Invalid role")
        if db.query(User).filter(User.username == username).first():
            raise ValueError("Username already exists")
        user = User(username=username, hashed_password=pwd_context.hash(password), role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def login(db: Session, username: str, password: str):
        user = db.query(User).filter(User.username == username).first()
        if not user or not pwd_context.verify(password, user.hashed_password):
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
