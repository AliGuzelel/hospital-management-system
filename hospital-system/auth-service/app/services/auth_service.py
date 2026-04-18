from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(*, user_id: int, username: str, role: str) -> tuple[str, int]:
    expire_minutes = settings.access_token_expire_minutes
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": expire,
    }
    token = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expire_minutes * 60


class AuthService:
    @staticmethod
    async def register(db: AsyncSession, payload: RegisterRequest) -> User:
        existing = await db.execute(select(User).where(User.username == payload.username))
        if existing.scalar_one_or_none() is not None:
            raise ValueError("Username already registered")

        user = User(
            username=payload.username,
            password_hash=hash_password(payload.password),
            role=payload.role.value,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def login(db: AsyncSession, username: str, password: str) -> TokenResponse:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if user is None or not verify_password(password, user.password_hash):
            raise ValueError("Invalid username or password")

        token, ttl = create_access_token(user_id=user.id, username=user.username, role=user.role)
        return TokenResponse(
            access_token=token,
            expires_in=ttl,
            role=user.role,
            user_id=user.id,
        )
