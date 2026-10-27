"""Sozlamalar: muhit o'zgaruvchilari va loyiha ildizidagi .env fayli."""

import os
import secrets
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env_file(path: Path) -> None:
    """Oddiy KEY=VALUE qatorlarni o'qiydi. Muhitda bor qiymat ustun turadi."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _secret_key(data_dir: Path) -> str:
    """SECRET_KEY berilmagan bo'lsa, data/ ichida bir marta yaratib saqlaydi."""
    key = os.environ.get("SECRET_KEY", "")
    if key:
        return key
    path = data_dir / "secret.key"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    data_dir.mkdir(parents=True, exist_ok=True)
    key = secrets.token_urlsafe(48)
    path.write_text(key, encoding="utf-8")
    return key


@dataclass(frozen=True)
class Settings:
    db_path: Path
    secret_key: str
    org_name: str
    site_title: str
    cookie_secure: bool


def load_settings() -> Settings:
    _load_env_file(BASE_DIR / ".env")
    data_dir = BASE_DIR / "data"
    db_path = Path(os.environ.get("DATABASE_PATH", data_dir / "telefonlar.db"))
    return Settings(
        db_path=db_path,
        secret_key=_secret_key(db_path.parent),
        org_name=os.environ.get("ORG_NAME", "O'zbekiston Respublikasi Madaniyat vazirligi"),
        site_title=os.environ.get("SITE_TITLE", "Telefon ma'lumotnomasi"),
        cookie_secure=os.environ.get("COOKIE_SECURE", "0") == "1",
    )
