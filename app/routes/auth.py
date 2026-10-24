import re

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, field_validator

from app.auth import authenticate, create_token, create_user, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _clean_email(value: str) -> str:
    value = value.strip().lower()
    if not EMAIL_RE.match(value) or len(value) > 254:
        raise ValueError("Format email tidak valid.")
    return value


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

    @field_validator("name")
    @classmethod
    def _name(cls, v: str) -> str:
        v = v.strip()
        if not 2 <= len(v) <= 60:
            raise ValueError("Nama harus 2–60 karakter.")
        return v

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return _clean_email(v)

    @field_validator("password")
    @classmethod
    def _password(cls, v: str) -> str:
        if not 8 <= len(v) <= 128:
            raise ValueError("Kata sandi harus 8–128 karakter.")
        return v


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return v.strip().lower()


def _session(user: dict) -> dict:
    return {"access_token": create_token(user), "token_type": "bearer", "user": user}


@router.post("/register", status_code=201)
def register(body: RegisterRequest):
    """Daftar akun baru; langsung mengembalikan token (otomatis masuk)."""
    user = create_user(body.name, body.email, body.password)
    return _session(user)


@router.post("/login")
def login(body: LoginRequest):
    """Masuk dengan email + kata sandi (dipakai frontend)."""
    return _session(authenticate(body.email, body.password))


@router.post("/token", include_in_schema=True)
def token(form: OAuth2PasswordRequestForm = Depends()):
    """Endpoint form OAuth2 agar tombol 'Authorize' di /docs berfungsi (username = email)."""
    return _session(authenticate(form.username.strip().lower(), form.password))


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return user
