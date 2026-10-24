
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import random

root = Path("datasets/processed/faces/train")
classes = ["Heart", "Oblong", "Oval", "Round", "Square"]

random.seed(42)
fig, axes = plt.subplots(5, 5, figsize=(12, 12))

for row, label in enumerate(classes):
    files = [
        p for p in (root / label).iterdir()
        if p.suffix.lower() in (".jpg", ".jpeg", ".png")
    ]
    samples = random.sample(files, min(5, len(files)))

    for col in range(5):
        ax = axes[row, col]
        ax.axis("off")
        if col < len(samples):
            with Image.open(samples[col]) as im:
                ax.imshow(im.convert("RGB"))
            ax.set_title(label, fontsize=10)

plt.tight_layout()
plt.savefig("face_crop_review.png", dpi=180)
plt.show()
