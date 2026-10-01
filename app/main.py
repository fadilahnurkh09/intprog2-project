from fastapi import FastAPI
from app.routes.predict import router as predict_router

app = FastAPI(
    title="FrameFit API",
    description="Backend API untuk aplikasi FrameFit",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "FrameFit API is running"
    }


app.include_router(predict_router)