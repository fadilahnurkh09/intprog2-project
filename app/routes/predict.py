from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io
import numpy as np

from app.model import model, CLASS_NAMES

router = APIRouter()


@router.post("/predict")
async def predict(file: UploadFile = File(...)):

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File yang diupload harus berupa gambar."
        )

    try:
        image_bytes = await file.read()

        image = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGB")

        # Resize sesuai input MobileNetV2
        image = image.resize((224, 224))

        # Ubah gambar menjadi array
        image_array = np.array(image, dtype=np.float32)

        # Tambahkan dimensi batch
        image_array = np.expand_dims(image_array, axis=0)

        # Preprocessing MobileNetV2
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

        image_array = preprocess_input(image_array)

        # Prediksi
        predictions = model.predict(image_array, verbose=0)

        predicted_index = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][predicted_index])

        face_shape = CLASS_NAMES[predicted_index]

        return {
            "success": True,
            "face_shape": face_shape,
            "confidence": round(confidence, 4)
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Gagal melakukan prediksi: {str(e)}"
        )