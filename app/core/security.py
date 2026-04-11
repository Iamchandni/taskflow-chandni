"""
app/core/security.py
────────────────────
Pure security utilities — bcrypt hashing and JWT token creation/verification.
These are plain functions with no framework or DB dependencies, used by the
application service layer.
"""

from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext
from jose import jwt, JWTError

from app.core.config import settings

# ── Bcrypt context ──────────────────────────────────────────────
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS,
)


def hash_password(plain: str) -> str:
    """Hash a plain-text password with bcrypt (cost ≥ 12)."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Check a plain-text password against a bcrypt hash."""
    return pwd_context.verify(plain, hashed)


# ── JWT helpers ─────────────────────────────────────────────────
def create_access_token(user_id: str, email: str) -> str:
    """Create a signed JWT with user_id and email in claims. Expires in 24h."""
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRY_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT. Returns the payload dict.
    Raises JWTError on invalid/expired tokens.
    """
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise
