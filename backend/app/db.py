"""SQLite ulanishi, sxema va umumiy so'rovlar."""

import os
import sqlite3
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

SCHEMA = """
CREATE TABLE IF NOT EXISTS departments (
    id          INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    parent_id   INTEGER REFERENCES departments(id) ON DELETE RESTRICT,
    sort_order  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS employees (
    id             INTEGER PRIMARY KEY,
    department_id  INTEGER NOT NULL REFERENCES departments(id) ON DELETE RESTRICT,
    full_name      TEXT    NOT NULL,
    position       TEXT    NOT NULL DEFAULT '',
    room           TEXT    NOT NULL DEFAULT '',
    internal_phone TEXT    NOT NULL DEFAULT '',
    city_phone     TEXT    NOT NULL DEFAULT '',
    mobile_phone   TEXT    NOT NULL DEFAULT '',
    email          TEXT    NOT NULL DEFAULT '',
    sort_order     INTEGER NOT NULL DEFAULT 0,
    updated_at     TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS employees_department ON employees(department_id, sort_order);

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY,
    username      TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    full_name     TEXT    NOT NULL DEFAULT '',
    password_hash TEXT    NOT NULL,
    is_admin      INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
    id       INTEGER PRIMARY KEY,
    at       TEXT    NOT NULL,
    username TEXT    NOT NULL,
    action   TEXT    NOT NULL,
    details  TEXT    NOT NULL
);
"""

ACCOUNT_ACTIONS = ("foydalanuvchi qo'shildi", "foydalanuvchi o'chirildi", "parol almashtirildi")

EMPLOYEE_FIELDS = (
    "full_name",
    "position",
    "room",
    "internal_phone",
    "city_phone",
    "mobile_phone",
    "email",
)


@lru_cache
def _timezone() -> ZoneInfo:
    # Server UTC'da bo'lsa ham vaqt Toshkent bo'yicha yoziladi (TIMEZONE bilan o'zgartirish mumkin).
    return ZoneInfo(os.environ.get("TIMEZONE", "Asia/Tashkent"))


def now() -> str:
    return datetime.now(_timezone()).replace(tzinfo=None).isoformat(timespec="seconds")


def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def init_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = connect(path)
    try:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def log(conn: sqlite3.Connection, username: str, action: str, details: str) -> None:
    conn.execute(
        "INSERT INTO audit_log (at, username, action, details) VALUES (?, ?, ?, ?)",
        (now(), username, action, details),
    )


def department_tree(conn: sqlite3.Connection) -> list[dict]:
    """Bo'limlarni ko'rsatish tartibida qaytaradi: yuqori bo'lim, keyin uning ichidagilar."""
    rows = conn.execute(
        "SELECT id, name, parent_id, sort_order FROM departments ORDER BY sort_order, id"
    ).fetchall()
    children: dict[int | None, list[sqlite3.Row]] = {}
    for row in rows:
        children.setdefault(row["parent_id"], []).append(row)
    result = []
    for top in children.get(None, []):
        result.append({**dict(top), "level": 0})
        for child in children.get(top["id"], []):
            result.append({**dict(child), "level": 1})
    return result


def directory(conn: sqlite3.Connection, include_empty: bool = False) -> list[dict]:
    """Bo'limlar ko'rsatish tartibida, har birida hodimlar ro'yxati."""
    employees: dict[int, list[dict]] = {}
    for row in conn.execute(
        "SELECT * FROM employees ORDER BY department_id, sort_order, id"
    ):
        employees.setdefault(row["department_id"], []).append(dict(row))
    tree = department_tree(conn)
    sections = [{**dept, "employees": employees.get(dept["id"], [])} for dept in tree]
    if include_empty:
        return sections
    # Ichida hodimi ham, hodimli kichik bo'limi ham bo'lmagan bo'limni ko'rsatmaymiz.
    visible = {s["id"] for s in sections if s["employees"]}
    visible |= {s["parent_id"] for s in sections if s["id"] in visible and s["parent_id"]}
    return [s for s in sections if s["id"] in visible]


def last_updated(conn: sqlite3.Connection) -> str | None:
    """Ma'lumotnoma oxirgi marta qachon o'zgargan. Foydalanuvchi va parol amallari hisobga olinmaydi."""
    placeholders = ", ".join("?" * len(ACCOUNT_ACTIONS))
    row = conn.execute(
        f"SELECT MAX(at) FROM audit_log WHERE action NOT IN ({placeholders})", ACCOUNT_ACTIONS
    ).fetchone()
    return row[0] if row else None


def next_sort_order(conn: sqlite3.Connection, table: str, column: str, value) -> int:
    op = "IS" if value is None else "="
    row = conn.execute(
        f"SELECT COALESCE(MAX(sort_order), 0) + 1 FROM {table} WHERE {column} {op} ?",
        (value,),
    ).fetchone()
    return row[0]


def move(conn: sqlite3.Connection, table: str, group_column: str, item_id: int, direction: str) -> bool:
    """Elementni o'z guruhi ichida bir pog'ona yuqoriga yoki pastga suradi."""
    item = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (item_id,)).fetchone()
    if item is None:
        return False
    group = item[group_column]
    op = "IS" if group is None else "="
    siblings = [
        r["id"]
        for r in conn.execute(
            f"SELECT id FROM {table} WHERE {group_column} {op} ? ORDER BY sort_order, id",
            (group,),
        )
    ]
    index = siblings.index(item_id)
    target = index - 1 if direction == "up" else index + 1
    if target < 0 or target >= len(siblings):
        return False
    siblings[index], siblings[target] = siblings[target], siblings[index]
    conn.executemany(
        f"UPDATE {table} SET sort_order = ? WHERE id = ?",
        [(pos, sid) for pos, sid in enumerate(siblings, start=1)],
    )
    return True
