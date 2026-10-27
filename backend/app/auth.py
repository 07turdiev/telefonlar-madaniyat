"""Parol xeshi va kadrlar bo'limi foydalanuvchisini buyruq qatoridan yaratish.

Foydalanish:
    python -m app.auth create-user <login> [--admin] [--name "F.I.Sh."]
    python -m app.auth set-password <login>
"""

import argparse
import getpass
import hashlib
import hmac
import secrets
import sys

# Format: scrypt.<salt hex>.<hash hex>. Ichida "$" yo'q, shell'da buzilmaydi.
_N, _R, _P = 2**14, 8, 1


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=_N, r=_R, p=_P)
    return f"scrypt.{salt.hex()}.{digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt_hex, digest_hex = stored.split(".")
    except ValueError:
        return False
    if scheme != "scrypt":
        return False
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=_N, r=_R, p=_P)
    return hmac.compare_digest(digest.hex(), digest_hex)


MIN_PASSWORD_LENGTH = 8


def _ask_password() -> str:
    while True:
        first = getpass.getpass("Parol: ")
        if len(first) < MIN_PASSWORD_LENGTH:
            print(f"Parol kamida {MIN_PASSWORD_LENGTH} belgidan iborat bo'lsin.")
            continue
        if first != getpass.getpass("Parolni takrorlang: "):
            print("Parollar mos kelmadi.")
            continue
        return first


def main(argv: list[str] | None = None) -> int:
    from app.config import load_settings
    from app.db import connect, init_db, log, now

    parser = argparse.ArgumentParser(prog="python -m app.auth")
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create-user", help="yangi foydalanuvchi")
    create.add_argument("username")
    create.add_argument("--name", default="")
    create.add_argument("--admin", action="store_true", help="foydalanuvchilarni boshqara oladi")
    reset = sub.add_parser("set-password", help="parolni almashtirish")
    reset.add_argument("username")
    args = parser.parse_args(argv)

    settings = load_settings()
    init_db(settings.db_path)
    conn = connect(settings.db_path)
    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?", (args.username,)
        ).fetchone()
        if args.command == "create-user":
            if existing:
                print(f"'{args.username}' allaqachon bor.", file=sys.stderr)
                return 1
            conn.execute(
                "INSERT INTO users (username, full_name, password_hash, is_admin, created_at)"
                " VALUES (?, ?, ?, ?, ?)",
                (args.username, args.name, hash_password(_ask_password()), int(args.admin), now()),
            )
            log(conn, "konsol", "foydalanuvchi qo'shildi", args.username)
            print(f"'{args.username}' yaratildi.")
        else:
            if not existing:
                print(f"'{args.username}' topilmadi.", file=sys.stderr)
                return 1
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (hash_password(_ask_password()), existing["id"]),
            )
            log(conn, "konsol", "parol almashtirildi", args.username)
            print("Parol almashtirildi.")
        conn.commit()
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
