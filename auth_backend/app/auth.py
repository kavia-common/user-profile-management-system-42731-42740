import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from werkzeug.security import check_password_hash, generate_password_hash


def _get_secret() -> str:
    """Return JWT secret with a safe fallback for local dev.

    NOTE: For production, set SECRET_KEY in the environment.
    """
    return os.getenv("SECRET_KEY", "dev-secret-change-me")


def _get_jwt_expiry_minutes() -> int:
    """Return JWT expiry duration in minutes."""
    raw = os.getenv("JWT_EXPIRY_MINUTES", "60")
    try:
        value = int(raw)
        return max(1, value)
    except ValueError:
        return 60


# PUBLIC_INTERFACE
def hash_password(password: str) -> str:
    """Hash a plaintext password using Werkzeug's PBKDF2 implementation."""
    return generate_password_hash(password)


# PUBLIC_INTERFACE
def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a stored hash."""
    return check_password_hash(password_hash, password)


# PUBLIC_INTERFACE
def create_access_token(user_id: int) -> str:
    """Create a signed JWT access token for the provided user_id."""
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=_get_jwt_expiry_minutes())
    payload = {"sub": str(user_id), "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(payload, _get_secret(), algorithm="HS256")


# PUBLIC_INTERFACE
def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token (raises on invalid token)."""
    return jwt.decode(token, _get_secret(), algorithms=["HS256"])


def get_bearer_token(auth_header: Optional[str]) -> Optional[str]:
    """Extract bearer token from Authorization header."""
    if not auth_header:
        return None
    parts = auth_header.split(" ", 1)
    if len(parts) != 2:
        return None
    scheme, token = parts[0].strip(), parts[1].strip()
    if scheme.lower() != "bearer" or not token:
        return None
    return token
