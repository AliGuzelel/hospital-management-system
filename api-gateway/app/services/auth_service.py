from jose import JWTError, jwt

from app.config.settings import settings


class GatewayAuthService:
    @staticmethod
    def decode_token(token: str) -> dict:
        t = (token or "").strip()
        if t.lower().startswith("bearer "):
            t = t[7:].strip()
        if len(t) >= 2 and t[0] == '"' and t[-1] == '"':
            t = t[1:-1].strip()
        try:
            return jwt.decode(t, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        except JWTError as exc:
            raise ValueError("Invalid token") from exc
