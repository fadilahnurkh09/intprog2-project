
import csv
from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image

CSV_PATH = Path(
    "models/training_results/faces/"
    "validation_prediction_audit.csv"
)

OUTPUT = Path(
    "models/training_results/faces/"
    "top20_validation_errors.png"
)

def main():
    with CSV_PATH.open(
        newline="", encoding="utf-8"
    ) as f:
        rows = list(csv.DictReader(f))

    wrong = [
        row for row in rows
        if row["correct"].lower() == "false"
    ]

    wrong.sort(
        key=lambda x: float(x["confidence"]),
        reverse=True
    )

    samples = wrong[:20]

    fig, axes = plt.subplots(
        4, 5, figsize=(16, 15)
    )

    for ax, row in zip(axes.flat, samples):
        path = Path(row["filename"])

        with Image.open(path) as image:
            ax.imshow(image.convert("RGB"))

        ax.set_title(
            f"Asli: {row['actual']}\n"
            f"Prediksi: {row['predicted']}\n"
            f"Confidence: {float(row['confidence']):.1%}",
            fontsize=9
        )
        ax.axis("off")

    for ax in list(axes.flat)[len(samples):]:
        ax.axis("off")

    plt.tight_layout()
    plt.savefig(OUTPUT, dpi=180)
    plt.show()

    print("Visualisasi tersimpan:", OUTPUT)

if __name__ == "__main__":
    main()
