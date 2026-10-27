"""Endpointlar uchun umumiy bog'liqliklar: baza ulanishi va joriy foydalanuvchi."""

import sqlite3
from collections.abc import Iterator

from fastapi import Depends, HTTPException, Request

from app.db import connect


def get_db(request: Request) -> Iterator[sqlite3.Connection]:
    conn = connect(request.app.state.settings.db_path)
    try:
        yield conn
    finally:
        conn.close()


def current_user(request: Request, db=Depends(get_db)) -> sqlite3.Row:
    user_id = request.session.get("user_id")
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone() if user_id else None
    if user is None:
        raise HTTPException(401, "Tizimga kiring.")
    return user


def admin_user(user=Depends(current_user)) -> sqlite3.Row:
    if not user["is_admin"]:
        raise HTTPException(403, "Bu bo'lim faqat administrator uchun.")
    return user


def user_out(user: sqlite3.Row) -> dict:
    """Foydalanuvchini parol xeshisiz qaytaradi."""
    return {
        "id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "is_admin": bool(user["is_admin"]),
        "created_at": user["created_at"],
    }
