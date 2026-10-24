
from app.auth import get_current_user
from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/recommendations", tags=["Recommendations"], dependencies=[Depends(get_current_user)])

# Katalog awal untuk pengembangan API.
# Data frame dan URL gambar bisa disesuaikan dengan katalog proyek.
GLASSES_CATALOG = [
    {
        "id": 1,
        "name": "Rectangular Frame",
        "style": "rectangular",
        "suitable_for": ["Oval", "Round"],
        "description": "Bingkai bersudut untuk memberi kesan wajah lebih tegas.",
    },
    {
        "id": 2,
        "name": "Round Frame",
        "style": "round",
        "suitable_for": ["Square", "Oblong"],
        "description": "Bingkai membulat untuk memberi kesan lebih lembut.",
    },
    {
        "id": 3,
        "name": "Cat-Eye Frame",
        "style": "cat-eye",
        "suitable_for": ["Round", "Square", "Heart"],
        "description": "Sudut bingkai terangkat untuk tampilan yang lebih tegas.",
    },
    {
        "id": 4,
        "name": "Aviator Frame",
        "style": "aviator",
        "suitable_for": ["Heart", "Oblong"],
        "description": "Bingkai bergaya aviator dengan bentuk lensa khas.",
    },
    {
        "id": 5,
        "name": "Oval Frame",
        "style": "oval",
        "suitable_for": ["Square", "Oblong"],
        "description": "Bingkai oval dengan garis yang lebih lembut.",
    },
]


class RecommendationRequest(BaseModel):
    face_shape: str


@router.post("")
def get_recommendations(request: RecommendationRequest):
    face_shape = request.face_shape.strip().title()

    valid_shapes = {"Heart", "Oblong", "Oval", "Round", "Square"}

    if face_shape not in valid_shapes:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Bentuk wajah tidak valid.",
                "valid_face_shapes": sorted(valid_shapes),
            },
        )

    recommendations = [
        {
            "id": item["id"],
            "name": item["name"],
            "style": item["style"],
            "description": item["description"],
        }
        for item in GLASSES_CATALOG
        if face_shape in item["suitable_for"]
    ]

    return {
        "success": True,
        "face_shape": face_shape,
        "recommendations": recommendations,
    }
