import pytest
from fastapi.testclient import TestClient

from app.auth import hash_password
from app.config import Settings
from app.db import connect, init_db, now
from app.main import create_app
from app import public

PASSWORD = "kadrlar-parol"


@pytest.fixture
def settings(tmp_path):
    return Settings(
        db_path=tmp_path / "test.db",
        secret_key="test-secret",
        org_name="Test vazirligi",
        site_title="Telefonlar",
        cookie_secure=False,
    )


@pytest.fixture
def db(settings):
    init_db(settings.db_path)
    conn = connect(settings.db_path)
    yield conn
    conn.close()


def add_user(db, username, is_admin=False):
    db.execute(
        "INSERT INTO users (username, full_name, password_hash, is_admin, created_at)"
        " VALUES (?, ?, ?, ?, ?)",
        (username, username.title(), hash_password(PASSWORD), int(is_admin), now()),
    )
    db.commit()


@pytest.fixture
def client(settings, db):
    public._failures.clear()
    with TestClient(create_app(settings), headers={"X-Requested-With": "XMLHttpRequest"}) as c:
        yield c


def login(client, username):
    response = client.post("/api/auth/login", json={"username": username, "password": PASSWORD})
    assert response.status_code == 200, response.text
    return response.json()


@pytest.fixture
def hr(client, db):
    """Kadrlar bo'limi xodimi sifatida kirgan klient."""
    add_user(db, "kadrlar")
    login(client, "kadrlar")
    return client


@pytest.fixture
def admin(client, db):
    add_user(db, "admin", is_admin=True)
    login(client, "admin")
    return client
