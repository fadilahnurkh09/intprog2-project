"""Autentikasi FrameFit: penyimpanan user (SQLite), hash password, dan token JWT."""
import base64
import hashlib
import hmac
import os
import secrets
import sqlite3
import time
from pathlib import Path

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = Path(os.getenv("FRAMEFIT_DB_PATH", DATA_DIR / "framefit.db"))

JWT_ALGORITHM = "HS256"
TOKEN_TTL_SECONDS = int(os.getenv("FRAMEFIT_TOKEN_TTL_HOURS", "24")) * 3600
PBKDF2_ITERATIONS = 390_000


# --------------------------------------------------------------------------
# Secret key: dari env FRAMEFIT_SECRET_KEY, atau dibuat otomatis & disimpan
# di data/.secret_key (tidak ikut git) supaya token tetap valid saat reload.
# --------------------------------------------------------------------------
def _load_secret() -> str:
    env = os.getenv("FRAMEFIT_SECRET_KEY")
    if env:
        return env
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    key_file = DB_PATH.parent / ".secret_key"
    if key_file.exists():
        return key_file.read_text().strip()
    key = secrets.token_urlsafe(48)
    key_file.write_text(key)
    return key


SECRET_KEY = _load_secret()


# --------------------------------------------------------------------------
# Database
# --------------------------------------------------------------------------
def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                email         TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                created_at    INTEGER NOT NULL
            )
            """
        )


# --------------------------------------------------------------------------
# Password hashing (PBKDF2-HMAC-SHA256 + salt acak)
# --------------------------------------------------------------------------
def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        PBKDF2_ITERATIONS,
        base64.b64encode(salt).decode(),
        base64.b64encode(digest).decode(),
    )


def verify_password(password: str, stored: str) -> bool:
    try:
        _, iters, salt_b64, hash_b64 = stored.split("$")
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(iters))
        return hmac.compare_digest(digest, expected)
    except Exception:
        return False


# Hash palsu agar waktu respons login tidak membocorkan apakah email terdaftar.
_DUMMY_HASH = hash_password("dummy-password-for-timing")


# --------------------------------------------------------------------------
# User & token
# --------------------------------------------------------------------------
def public_user(row: sqlite3.Row) -> dict:
    return {"id": row["id"], "name": row["name"], "email": row["email"]}


def create_user(name: str, email: str, password: str) -> dict:
    try:
        with get_db() as conn:
            cur = conn.execute(
                "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (name, email, hash_password(password), int(time.time())),
            )
            row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email sudah terdaftar. Silakan masuk.")
    return public_user(row)


def authenticate(email: str, password: str) -> dict:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    ok = verify_password(password, row["password_hash"] if row else _DUMMY_HASH)
    if not row or not ok:
        raise HTTPException(
            status_code=401,
            detail="Email atau kata sandi salah.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return public_user(row)


def create_token(user: dict) -> str:
    now = int(time.time())
    payload = {"sub": str(user["id"]), "iat": now, "exp": now + TOKEN_TTL_SECONDS}
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesi tidak valid atau sudah berakhir. Silakan masuk lagi.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise unauthorized

    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        raise unauthorized
    return public_user(row)
