from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.predict import router as predict_router
from app.routes.recommend import router as recommend_router
from app.routes.try_on import router as try_on_router

app = FastAPI(
    title="FrameFit API",
    description="Backend API untuk aplikasi FrameFit",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "FrameFit API is running"}


app.include_router(predict_router)
app.include_router(recommend_router)
app.include_router(try_on_router)