<<<<<<< HEAD

from pathlib import Path
import io

import numpy as np
from PIL import Image, UnidentifiedImageError
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.model import model, CLASS_NAMES
from app.routes.recommend import GLASSES_CATALOG
from training.prepare_faces import Landmarker, crop_then_resize

import base64

from app.routes.try_on import (
    GLASSES_FILES,
    apply_glasses_to_face,
    pil_image_to_png_bytes,
)
=======
from app.routes.recommend import GLASSES_CATALOG
from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image, UnidentifiedImageError
from pathlib import Path
import mediapipe as mp
import io
import numpy as np

from app.model import model, CLASS_NAMES

>>>>>>> origin/main
router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

<<<<<<< HEAD
BASE_DIR = Path(__file__).resolve().parents[2]
FACE_LANDMARKER_PATH = (
    BASE_DIR / "models" / "face_landmarker.task"
)
=======
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
>>>>>>> origin/main


@router.post("/predict")
async def predict(file: UploadFile = File(...)):

    # 1. Validasi tipe file
<<<<<<< HEAD
    if (
        not file.content_type
        or not file.content_type.startswith("image/")
    ):
=======
    if not file.content_type or not file.content_type.startswith("image/"):
>>>>>>> origin/main
        raise HTTPException(
            status_code=400,
            detail="File yang diupload harus berupa gambar."
        )

    try:
<<<<<<< HEAD
        # 2. Baca file
=======
        # 2. Baca file dan batasi ukurannya
>>>>>>> origin/main
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

<<<<<<< HEAD
        # 3. Buka dan validasi gambar
=======
        # 3. Validasi dan buka gambar
>>>>>>> origin/main
        try:
            with Image.open(io.BytesIO(image_bytes)) as image:
                image.verify()

            with Image.open(io.BytesIO(image_bytes)) as image:
                image = image.convert("RGB")
<<<<<<< HEAD
                original_image = image.copy()
=======
                original_image = np.array(image, dtype=np.uint8)
>>>>>>> origin/main

        except (
            UnidentifiedImageError,
            OSError,
            Image.DecompressionBombError
        ):
            raise HTTPException(
                status_code=400,
                detail="File bukan gambar yang valid atau gambar rusak."
            )

<<<<<<< HEAD
        # 4. Deteksi dan crop wajah
        try:
            detector = Landmarker(FACE_LANDMARKER_PATH)

            try:
                face_box = detector.detect_box(original_image)
            finally:
                detector.close()

            if face_box is None:
                raise HTTPException(
                    status_code=400,
                    detail="Tidak ada wajah terdeteksi pada gambar."
                )

            # Sama dengan preprocessing dataset training
            face_crop = crop_then_resize(
                original_image,
                face_box,
                size=224
            )

        except HTTPException:
            raise

        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Area wajah tidak valid untuk cropping."
            )

        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Terjadi kesalahan saat mendeteksi atau crop wajah."
            )

        # 5. Siapkan input MobileNetV2
        image_array = np.asarray(
            face_crop,
            dtype=np.float32
        )

        image_array = np.expand_dims(
            image_array,
            axis=0
        )
=======
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
>>>>>>> origin/main

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Terjadi kesalahan saat memproses file."
        )

    # 6. Prediksi bentuk wajah
    try:
<<<<<<< HEAD
        predictions = model.predict(
            image_array,
            verbose=0
        )

        predicted_index = int(
            np.argmax(predictions[0])
        )

        confidence = float(
            predictions[0][predicted_index]
        )

=======
        predictions = model.predict(image_array, verbose=0)

        predicted_index = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][predicted_index])
>>>>>>> origin/main
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
<<<<<<< HEAD

    # Menggunakan fungsi prediksi yang sama
=======
    # Jalankan prediksi menggunakan validasi dan model yang sudah ada
>>>>>>> origin/main
    result = await predict(file)

    face_shape = result["face_shape"]

<<<<<<< HEAD
    # Rekomendasi berdasarkan bentuk wajah
=======
    # Ambil rekomendasi sesuai bentuk wajah
>>>>>>> origin/main
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

<<<<<<< HEAD

@router.post("/analyze-full")
async def analyze_full(file: UploadFile = File(...)):
    # 1. Prediksi bentuk wajah + rekomendasi
    # Menggunakan fungsi yang sudah berhasil diuji
    analysis = await analyze(file)

    # 2. Samakan nama style rekomendasi
    # dengan aset Virtual Try-On backend
    style_aliases = {
        "cat-eye": "cateye",
    }

    # 3. Pilih rekomendasi pertama
    # yang aset kacamatanya tersedia
    selected_frame = None
    selected_style = None

    for recommendation in analysis["recommendations"]:
        style = recommendation["style"]
        style = style_aliases.get(style, style)

        if style in GLASSES_FILES:
            selected_frame = recommendation
            selected_style = style
            break

    if selected_frame is None:
        raise HTTPException(
            status_code=500,
            detail="Tidak ada aset kacamata untuk rekomendasi."
        )

    # 4. Baca kembali foto yang sama
    # tanpa meminta pengguna upload ulang
    await file.seek(0)
    image_bytes = await file.read()

    try:
        with Image.open(io.BytesIO(image_bytes)) as source:
            original_photo = source.convert("RGB")
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="Gambar tidak dapat dibuka."
        )

    # 5. Deteksi landmark dan pasang kacamata
    # menggunakan fungsi dari try_on.py
    tryon_result = apply_glasses_to_face(
        original_photo,
        selected_style
    )

    # 6. Ubah gambar hasil menjadi Base64
    # supaya dapat dikirim bersama JSON
    output = pil_image_to_png_bytes(tryon_result)

    image_base64 = base64.b64encode(
        output.getvalue()
    ).decode("ascii")

    # 7. Kirim semua hasil dalam satu respons
    return {
        "success": True,
        "face_shape": analysis["face_shape"],
        "confidence": analysis["confidence"],
        "recommendations": analysis["recommendations"],
        "selected_frame": {
            **selected_frame,
            "try_on_style": selected_style,
        },
        "tryon_image": (
            "data:image/png;base64," + image_base64
        ),
    }
=======
>>>>>>> origin/main
