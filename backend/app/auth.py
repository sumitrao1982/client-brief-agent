"""Very small JWT auth layer with in-memory demo users (sample app only)."""
import hashlib
import hmac
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import JWT_EXPIRE_MINUTES, JWT_SECRET

ALGORITHM = "HS256"
_SALT = b"client-brief-demo-salt"


def _hash(password: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), _SALT, 100_000).hex()


# Demo users — replace with your IdP / SSO (e.g. Azure AD, Okta) in a real deployment.
USERS = {
    "banker": {"full_name": "Alex Morgan", "role": "Managing Director, Coverage", "password_hash": _hash("demo123")},
    "analyst": {"full_name": "Jordan Lee", "role": "Associate, Coverage", "password_hash": _hash("demo123")},
}

bearer = HTTPBearer(auto_error=False)


def authenticate(username: str, password: str) -> dict | None:
    user = USERS.get(username.lower().strip())
    if not user or not hmac.compare_digest(user["password_hash"], _hash(password)):
        return None
    return {"username": username.lower().strip(), "full_name": user["full_name"], "role": user["role"]}


def create_token(user: dict) -> str:
    payload = {**user, "sub": user["username"],
               "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)}
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def _decode(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return {"username": payload["sub"], "full_name": payload.get("full_name"), "role": payload.get("role")}


def current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return _decode(creds.credentials)


def current_user_header_or_query(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    token: str | None = Query(default=None),
) -> dict:
    """Allows ?token=... so PDFs can be opened in a new browser tab."""
    if creds:
        return _decode(creds.credentials)
    if token:
        return _decode(token)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
