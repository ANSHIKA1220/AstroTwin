import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User

COOKIE_NAME = "astrotwin_session"
SESSION_TTL_SECONDS = 60 * 60 * 24 * 14
PBKDF2_ITERATIONS = 310_000

def _secret() -> bytes:
    return os.getenv("SESSION_SECRET", "local-development-change-me").encode()

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${_b64(salt)}${_b64(digest)}"

def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), _unb64(salt), int(iterations))
        return hmac.compare_digest(_b64(digest), expected)
    except (TypeError, ValueError):
        return False

def create_session_token(user_id: int) -> str:
    payload = _b64(json.dumps({"uid": user_id, "exp": int(time.time()) + SESSION_TTL_SECONDS}, separators=(",", ":")).encode())
    signature = _b64(hmac.new(_secret(), payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{signature}"

def read_session_token(token: str | None) -> int | None:
    if not token:
        return None
    try:
        payload, signature = token.split(".", 1)
        expected = _b64(hmac.new(_secret(), payload.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            return None
        data = json.loads(_unb64(payload))
        if int(data["exp"]) < int(time.time()):
            return None
        return int(data["uid"])
    except (ValueError, KeyError, json.JSONDecodeError):
        return None

def set_session_cookie(response: Response, user_id: int) -> None:
    secure = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    response.set_cookie(
        COOKIE_NAME,
        create_session_token(user_id),
        max_age=SESSION_TTL_SECONDS,
        httponly=True,
        secure=secure,
        samesite="none" if secure else "lax",
        path="/",
    )

def clear_session_cookie(response: Response) -> None:
    secure = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    response.delete_cookie(COOKIE_NAME, httponly=True, secure=secure, samesite="none" if secure else "lax", path="/")

def require_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = read_session_token(request.cookies.get(COOKIE_NAME))
    user = db.get(User, user_id) if user_id else None
    if not user:
        raise HTTPException(401, "Sign in required")
    return user

def require_owner(requested_user_id: int, current_user: User) -> None:
    if requested_user_id != current_user.id:
        raise HTTPException(403, "This profile belongs to another account")
