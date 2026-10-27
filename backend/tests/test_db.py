import sqlite3

from app.db import init_db

# is_vacant ustunidan oldingi versiyadagi jadval
OLD_EMPLOYEES = """
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    department_id INTEGER NOT NULL,
    full_name TEXT NOT NULL,
    position TEXT NOT NULL DEFAULT '',
    room TEXT NOT NULL DEFAULT '',
    internal_phone TEXT NOT NULL DEFAULT '',
    city_phone TEXT NOT NULL DEFAULT '',
    mobile_phone TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    sort_order INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);
INSERT INTO employees (department_id, full_name, updated_at) VALUES (1, 'Ali', '2026-01-01T00:00:00');
"""


def test_init_db_adds_is_vacant_to_existing_database(tmp_path):
    path = tmp_path / "old.db"
    conn = sqlite3.connect(path)
    conn.executescript(OLD_EMPLOYEES)
    conn.close()

    init_db(path)
    init_db(path)  # ikkinchi marta ham xatosiz

    conn = sqlite3.connect(path)
    assert conn.execute("SELECT full_name, is_vacant FROM employees").fetchall() == [("Ali", 0)]
    conn.close()
