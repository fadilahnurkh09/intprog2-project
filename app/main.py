import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.auth import init_db
from app.routes.auth import router as auth_router
from app.routes.predict import router as predict_router
from app.routes.recommend import router as recommend_router
from app.routes.try_on import router as try_on_router

BASE_DIR = Path(__file__).resolve().parents[1]

app = FastAPI(
    title="FrameFit API",
    description="Backend API untuk aplikasi FrameFit",
    version="1.1.0"
)

# Daftar origin frontend yang boleh memanggil API ini.
# Saat deploy, set env FRAMEFIT_CORS_ORIGINS, contoh:
#   FRAMEFIT_CORS_ORIGINS="https://framefit.example.com,https://www.framefit.example.com"
DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]
extra_origins = [
    o.strip() for o in os.getenv("FRAMEFIT_CORS_ORIGINS", "").split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=DEFAULT_ORIGINS + extra_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"message": "FrameFit API is running"}


# Gambar kacamata (PNG transparan) untuk thumbnail katalog di frontend.
app.mount(
    "/assets",
    StaticFiles(directory=BASE_DIR / "assets"),
    name="assets",
)

app.include_router(auth_router)
app.include_router(predict_router)
app.include_router(recommend_router)
app.include_router(try_on_router)
