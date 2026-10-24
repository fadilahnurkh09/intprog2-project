
from pathlib import Path
import io

import numpy as np
from PIL import Image, UnidentifiedImageError
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from app.auth import get_current_user

from app.model import model, CLASS_NAMES
from app.routes.recommend import GLASSES_CATALOG
from training.prepare_faces import Landmarker, crop_then_resize

import base64

from app.routes.try_on import (
    GLASSES_FILES,
    apply_glasses_to_face,
    pil_image_to_png_bytes,
)
router = APIRouter(dependencies=[Depends(get_current_user)])

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

BASE_DIR = Path(__file__).resolve().parents[2]
FACE_LANDMARKER_PATH = (
    BASE_DIR / "models" / "face_landmarker.task"
)


@router.post("/predict")
async def predict(file: UploadFile = File(...)):

    # 1. Validasi tipe file
    if (
        not file.content_type
        or not file.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=400,
            detail="File yang diupload harus berupa gambar."
        )

    try:
        # 2. Baca file
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

        # 3. Buka dan validasi gambar
        try:
            with Image.open(io.BytesIO(image_bytes)) as image:
                image.verify()

            with Image.open(io.BytesIO(image_bytes)) as image:
                image = image.convert("RGB")
                original_image = image.copy()

        except (
            UnidentifiedImageError,
            OSError,
            Image.DecompressionBombError
        ):
            raise HTTPException(
                status_code=400,
                detail="File bukan gambar yang valid atau gambar rusak."
            )

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

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Terjadi kesalahan saat memproses file."
        )

    # 6. Prediksi bentuk wajah
    try:
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

    # Menggunakan fungsi prediksi yang sama
    result = await predict(file)

    face_shape = result["face_shape"]

    # Rekomendasi berdasarkan bentuk wajah
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
