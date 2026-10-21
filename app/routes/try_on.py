
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image, UnidentifiedImageError
from pathlib import Path
import mediapipe as mp
import numpy as np
import io
import math

router = APIRouter(prefix="/try-on", tags=["Virtual Try-On"])

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

# Titik landmark MediaPipe di sekitar sudut luar kedua mata.
LEFT_EYE_OUTER = 33
RIGHT_EYE_OUTER = 263


def get_eye_points(image_rgb):
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


@router.post("")
async def try_on(
    file: UploadFile = File(...),
    glasses_style: str = Form(...),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File harus berupa gambar.")

    if glasses_style not in GLASSES_FILES:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Model kacamata tidak valid.",
                "available_styles": list(GLASSES_FILES.keys()),
            },
        )

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

    # Pangkas area transparan agar ukuran bingkai lebih akurat.
    alpha = glasses.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        raise HTTPException(status_code=500, detail="Aset kacamata kosong.")

    glasses = glasses.crop(bbox)

    # Lebar bingkai awal sekitar 2,3 kali jarak sudut luar mata.
    target_width = int(eye_distance * 2.3)
    target_height = max(1, int(glasses.height * target_width / glasses.width))
    glasses = glasses.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # Putar mengikuti kemiringan garis mata.
    glasses = glasses.rotate(
        angle,
        resample=Image.Resampling.BICUBIC,
        expand=True,
    )

    center_x = (p1[0] + p2[0]) / 2
    center_y = (p1[1] + p2[1]) / 2

    # Letakkan bagian tengah bingkai sedikit di bawah garis sudut luar mata.
    x = int(center_x - glasses.width / 2)
    y = int(center_y - glasses.height * 0.42)

    result = face.convert("RGBA")
    result.alpha_composite(glasses, (x, y))

    output = io.BytesIO()
    result.convert("RGB").save(output, format="PNG")
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="image/png",
        headers={"Content-Disposition": 'inline; filename="framefit-try-on.png"'},
    )
