
import csv
from pathlib import Path

source = Path(
    "models/training_results/faces/"
    "validation_prediction_audit.csv"
)

output = Path(
    "models/training_results/faces/"
    "manual_label_review.csv"
)

with source.open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

wrong = [
    row for row in rows
    if row["correct"].lower() == "false"
]

wrong.sort(
    key=lambda x: float(x["confidence"]),
    reverse=True
)

fields = [
    "filename",
    "actual",
    "predicted",
    "confidence",
    "review_status",
    "pose",
    "crop_quality",
    "notes"
]

output.parent.mkdir(parents=True, exist_ok=True)

with output.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()

    for row in wrong:
        writer.writerow({
            "filename": row["filename"],
            "actual": row["actual"],
            "predicted": row["predicted"],
            "confidence": row["confidence"],
            "review_status": "",
            "pose": "",
            "crop_quality": "",
            "notes": ""
        })

print("Jumlah gambar untuk audit:", len(wrong))
print("File hasil:", output)
