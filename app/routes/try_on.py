from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException

from app.auth import get_current_user
from fastapi.responses import StreamingResponse
from PIL import Image, UnidentifiedImageError
from pathlib import Path
import mediapipe as mp
import numpy as np
import io
import math

router = APIRouter(
    prefix="/try-on",
    tags=["Virtual Try-On"],
    dependencies=[Depends(get_current_user)],
)

BASE_DIR = Path(__file__).resolve().parents[2]
LANDMARKER_PATH = BASE_DIR / "models" / "face_landmarker.task"
GLASSES_DIR = BASE_DIR / "assets" / "glasses"
MAX_FILE_SIZE = 5 * 1024 * 1024

GLASSES_FILES = {
    "rectangular": "rectangular_test.png",
    "round": "round_test.png",
    "cateye": "cateye_test.png",
    "aviator": "aviator_test.png",
}

# Aturan pemasangan — HARUS SAMA dengan frontend/src/data/fit.js agar hasil mode
# "Otomatis" (server) dan "Atur manual" (browser) identik.
FIT_WIDTH_RATIO = 1.6       # lebar bingkai = jarak sudut luar mata x nilai ini
FIT_VERTICAL_ANCHOR = 0.5   # posisi garis mata di dalam tinggi bingkai (0.5 = tengah)

LEFT_EYE_OUTER = 33
RIGHT_EYE_OUTER = 263


def get_eye_points(image_rgb: Image.Image):
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=np.asarray(image_rgb, dtype=np.uint8),
    )

    options = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(
            model_asset_path=str(LANDMARKER_PATH)
        ),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_faces=1,
    )

    with mp.tasks.vision.FaceLandmarker.create_from_options(options) as detector:
        result = detector.detect(mp_image)

    if not result.face_landmarks:
        raise HTTPException(
            status_code=400,
            detail="Wajah tidak terdeteksi. Gunakan foto wajah dari depan.",
        )

    landmarks = result.face_landmarks[0]
    width, height = image_rgb.size

    p1 = (
        landmarks[LEFT_EYE_OUTER].x * width,
        landmarks[LEFT_EYE_OUTER].y * height,
    )
    p2 = (
        landmarks[RIGHT_EYE_OUTER].x * width,
        landmarks[RIGHT_EYE_OUTER].y * height,
    )

    return p1, p2


def apply_glasses_to_face(face: Image.Image, glasses_style: str) -> Image.Image:
    if glasses_style not in GLASSES_FILES:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Model kacamata tidak valid.",
                "available_styles": list(GLASSES_FILES.keys()),
            },
        )

    p1, p2 = get_eye_points(face)

    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    eye_distance = math.hypot(dx, dy)

    if eye_distance < 10:
        raise HTTPException(status_code=400, detail="Posisi mata tidak valid.")

    angle = math.degrees(math.atan2(dy, dx))

    glasses_path = GLASSES_DIR / GLASSES_FILES[glasses_style]
    if not glasses_path.is_file():
        raise HTTPException(
            status_code=500,
            detail=f"Aset kacamata tidak ditemukan: {glasses_path.name}",
        )

    with Image.open(glasses_path) as asset:
        glasses = asset.convert("RGBA")

    alpha = glasses.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        raise HTTPException(status_code=500, detail="Aset kacamata kosong.")

    glasses = glasses.crop(bbox)

    # ukuran frame
    target_width = int(eye_distance * FIT_WIDTH_RATIO)
    target_height = max(1, int(glasses.height * target_width / glasses.width))
    glasses = glasses.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # Rotasi mengikuti mata. Sumbu Y gambar mengarah ke bawah, sedangkan PIL memutar
    # berlawanan arah jarum jam, jadi sudutnya dibalik.
    glasses = glasses.rotate(
        -angle,
        resample=Image.Resampling.BICUBIC,
        expand=True,
    )

    center_x = (p1[0] + p2[0]) / 2
    center_y = (p1[1] + p2[1]) / 2

    x = int(center_x - glasses.width / 2)
    y = int(center_y - glasses.height * FIT_VERTICAL_ANCHOR)

    result = face.convert("RGBA")
    result.alpha_composite(glasses, (x, y))

    return result


def pil_image_to_png_bytes(image: Image.Image) -> io.BytesIO:
    output = io.BytesIO()
    image.convert("RGB").save(output, format="PNG")
    output.seek(0)
    return output


@router.post("")
async def try_on(
    file: UploadFile = File(...),
    glasses_style: str = Form(...),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File harus berupa gambar.")

    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(status_code=400, detail="File gambar kosong.")

    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Ukuran maksimal 5 MB.")

    try:
        with Image.open(io.BytesIO(image_bytes)) as source:
            source.verify()

        with Image.open(io.BytesIO(image_bytes)) as source:
            face = source.convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(status_code=400, detail="Gambar tidak valid.")

    result = apply_glasses_to_face(face, glasses_style)
    output = pil_image_to_png_bytes(result)

    return StreamingResponse(
        output,
        media_type="image/png",
        headers={"Content-Disposition": 'inline; filename="framefit-try-on.png"'},
    )
