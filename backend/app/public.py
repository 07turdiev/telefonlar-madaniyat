"""Ochiq ma'lumotnoma va kirish/chiqish: /api/directory, /api/auth/*."""

import time

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.auth import MIN_PASSWORD_LENGTH, hash_password, verify_password
from app.db import directory, last_updated, log
from app.deps import current_user, get_db, user_out

router = APIRouter(prefix="/api")

# Parolni tanlab topishni sekinlashtirish: bir login uchun 10 daqiqada 5 ta xato urinish.
MAX_FAILURES, FAILURE_WINDOW = 5, 600
_failures: dict[str, list[float]] = {}


class LoginIn(BaseModel):
    username: str
    password: str


class PasswordChangeIn(BaseModel):
    current: str
    password: str


def _is_locked(key: str) -> bool:
    cutoff = time.monotonic() - FAILURE_WINDOW
    recent = [t for t in _failures.get(key, []) if t > cutoff]
    _failures[key] = recent
    return len(recent) >= MAX_FAILURES


@router.get("/directory")
def get_directory(request: Request, db=Depends(get_db)):
    settings = request.app.state.settings
    return {
        "org_name": settings.org_name,
        "site_title": settings.site_title,
        "updated": last_updated(db),
        "sections": directory(db),
    }


@router.post("/auth/login")
def login(data: LoginIn, request: Request, db=Depends(get_db)):
    key = data.username.strip().lower()
    if _is_locked(key):
        raise HTTPException(429, "Juda ko'p xato urinish. 10 daqiqadan keyin qayta urinib ko'ring.")
    user = db.execute("SELECT * FROM users WHERE username = ?", (data.username.strip(),)).fetchone()
    if user is None or not verify_password(data.password, user["password_hash"]):
        _failures.setdefault(key, []).append(time.monotonic())
        raise HTTPException(400, "Login yoki parol noto'g'ri.")
    _failures.pop(key, None)
    request.session.clear()
    request.session["user_id"] = user["id"]
    return user_out(user)


@router.post("/auth/logout")
def logout(request: Request):
    request.session.clear()
    return {"ok": True}


@router.get("/auth/me")
def me(user=Depends(current_user)):
    return user_out(user)


@router.post("/auth/password")
def change_password(data: PasswordChangeIn, db=Depends(get_db), user=Depends(current_user)):
    if not verify_password(data.current, user["password_hash"]):
        raise HTTPException(400, detail={"errors": {"current": "Joriy parol noto'g'ri."}})
    if len(data.password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            400,
            detail={"errors": {"password": f"Parol kamida {MIN_PASSWORD_LENGTH} belgidan iborat bo'lsin."}},
        )
    db.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(data.password), user["id"])
    )
    log(db, user["username"], "parol almashtirildi", user["username"])
    db.commit()
    return {"ok": True}
