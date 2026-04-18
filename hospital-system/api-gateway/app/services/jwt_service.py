from jose import JWTError, jwt

from app.config.settings import settings


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def decode_token_safe(token: str) -> dict:
    try:
        return decode_token(token)
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
