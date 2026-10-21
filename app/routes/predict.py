from app.routes.recommend import GLASSES_CATALOG
from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image, UnidentifiedImageError
from pathlib import Path
import mediapipe as mp
import io
import numpy as np

from app.model import model, CLASS_NAMES

router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# Lokasi model Face Landmarker
BASE_DIR = Path(__file__).resolve().parents[2]
FACE_LANDMARKER_PATH = BASE_DIR / "models" / "face_landmarker.task"


def detect_face(image_array):
    """Mengembalikan True jika wajah terdeteksi."""
    try:
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=np.asarray(image_array, dtype=np.uint8)
        )

        options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=str(FACE_LANDMARKER_PATH)
            ),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_faces=1
        )

        with mp.tasks.vision.FaceLandmarker.create_from_options(
            options
        ) as detector:
            result = detector.detect(mp_image)

        return bool(result.face_landmarks)

    except Exception as exc:
        raise RuntimeError("Gagal menjalankan deteksi wajah.") from exc


@router.post("/predict")
async def predict(file: UploadFile = File(...)):

    # 1. Validasi tipe file
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File yang diupload harus berupa gambar."
        )

    try:
        # 2. Baca file dan batasi ukurannya
        image_bytes = await file.read()

        if not image_bytes:
            raise HTTPException(
                status_code=400,
                detail="File yang diupload kosong."
            )

        if len(image_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Ukuran file maksimal 5 MB."
            )

        # 3. Validasi dan buka gambar
        try:
            with Image.open(io.BytesIO(image_bytes)) as image:
                image.verify()

            with Image.open(io.BytesIO(image_bytes)) as image:
                image = image.convert("RGB")
                original_image = np.array(image, dtype=np.uint8)

        except (
            UnidentifiedImageError,
            OSError,
            Image.DecompressionBombError
        ):
            raise HTTPException(
                status_code=400,
                detail="File bukan gambar yang valid atau gambar rusak."
            )

        # 4. Deteksi wajah sebelum klasifikasi
        try:
            face_found = detect_face(original_image)
        except RuntimeError:
            raise HTTPException(
                status_code=500,
                detail="Terjadi kesalahan saat mendeteksi wajah."
            )

        if not face_found:
            raise HTTPException(
                status_code=400,
                detail="Tidak ada wajah terdeteksi pada gambar. Gunakan foto wajah yang terlihat jelas."
            )

        # 5. Siapkan gambar untuk MobileNetV2
        image = Image.fromarray(original_image)
        image = image.resize((224, 224))
        image_array = np.array(image, dtype=np.float32)
        image_array = np.expand_dims(image_array, axis=0)

        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
        image_array = preprocess_input(image_array)

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Terjadi kesalahan saat memproses file."
        )

    # 6. Prediksi bentuk wajah
    try:
        predictions = model.predict(image_array, verbose=0)

        predicted_index = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][predicted_index])
        face_shape = CLASS_NAMES[predicted_index]

        return {
            "success": True,
            "face_shape": face_shape,
            "confidence": round(confidence, 4)
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Terjadi kesalahan saat model melakukan prediksi."
        )


@router.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    # Jalankan prediksi menggunakan validasi dan model yang sudah ada
    result = await predict(file)

    face_shape = result["face_shape"]

    # Ambil rekomendasi sesuai bentuk wajah
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
        "confidence": result["confidence"],
        "recommendations": recommendations,
    }

