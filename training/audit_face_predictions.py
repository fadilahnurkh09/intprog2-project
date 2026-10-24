
from pathlib import Path
import csv
import numpy as np
import tensorflow as tf

LABELS = ["Heart", "Oblong", "Oval", "Round", "Square"]

DATA_DIR = Path("datasets/processed/faces/val")

MODEL_PATH = Path(
    "models/training_results/faces/"
    "faceshape_mobilenetv2_best.keras"
)

OUTPUT = Path(
    "models/training_results/faces/"
    "validation_prediction_audit.csv"
)

def main():
    print("Memulai audit prediksi wajah...", flush=True)

    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Dataset tidak ada: {DATA_DIR}")

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model tidak ada: {MODEL_PATH}")

    files = []
    true_labels = []

    for label_index, label in enumerate(LABELS):
        folder = DATA_DIR / label

        if not folder.exists():
            raise FileNotFoundError(f"Folder label tidak ada: {folder}")

        for file in sorted(folder.iterdir()):
            if file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                files.append(file)
                true_labels.append(label_index)

    print(f"Jumlah gambar validation: {len(files)}", flush=True)

    print("Memuat model MobileNetV2...", flush=True)
    model = tf.keras.models.load_model(MODEL_PATH)

    rows = []

    for start in range(0, len(files), 32):
        batch_files = files[start:start + 32]
        images = []

        for file in batch_files:
            image = tf.keras.utils.load_img(
                file,
                target_size=(224, 224),
                color_mode="rgb"
            )
            images.append(tf.keras.utils.img_to_array(image))

        batch = np.stack(images)
        predictions = model.predict(batch, verbose=0)

        for i, probabilities in enumerate(predictions):
            file_index = start + i
            predicted = int(np.argmax(probabilities))
            actual = true_labels[file_index]

            rows.append({
                "filename": str(files[file_index]),
                "actual": LABELS[actual],
                "predicted": LABELS[predicted],
                "confidence": round(float(probabilities[predicted]), 4),
                "correct": actual == predicted,
            })

        print(
            f"Sudah diproses: {min(start + 32, len(files))}/{len(files)}",
            flush=True
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "filename", "actual", "predicted",
                "confidence", "correct"
            ]
        )
        writer.writeheader()
        writer.writerows(rows)

    wrong = [r for r in rows if not r["correct"]]

    print("\n===== HASIL AUDIT =====")
    print("Jumlah gambar:", len(rows))
    print("Prediksi benar:", len(rows) - len(wrong))
    print("Prediksi salah:", len(wrong))
    print("Accuracy:", round((len(rows) - len(wrong)) / len(rows) * 100, 2), "%")
    print("Laporan tersimpan:", OUTPUT)


if __name__ == "__main__":
    main()
