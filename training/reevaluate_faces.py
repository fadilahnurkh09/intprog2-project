
import argparse
import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)

LABELS = ["Heart", "Oblong", "Oval", "Round", "Square"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument(
        "--data",
        default="datasets/processed/faces/val"
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    print("Memuat dataset validation...")

    ds = tf.keras.utils.image_dataset_from_directory(
        args.data,
        labels="inferred",
        class_names=LABELS,
        label_mode="categorical",
        image_size=(224, 224),
        batch_size=32,
        shuffle=False,
    )

    print("Memuat model:", args.model)

    model = tf.keras.models.load_model(args.model)

    loss, keras_accuracy = model.evaluate(ds, verbose=1)

    y_true = np.concatenate([
        np.argmax(y.numpy(), axis=1)
        for _, y in ds
    ])

    probabilities = model.predict(ds, verbose=1)
    y_pred = np.argmax(probabilities, axis=1)

    accuracy = accuracy_score(y_true, y_pred)

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=list(range(5)),
        average="macro",
        zero_division=0,
    )

    report = classification_report(
        y_true,
        y_pred,
        labels=list(range(5)),
        target_names=LABELS,
        digits=4,
        zero_division=0,
    )

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=list(range(5)),
    )

    results = {
        "loss": float(loss),
        "accuracy": float(accuracy),
        "keras_accuracy": float(keras_accuracy),
        "macro_precision": float(precision),
        "macro_recall": float(recall),
        "macro_f1": float(f1),
    }

    (output / "metrics.json").write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )

    (output / "classification_report.txt").write_text(
        report,
        encoding="utf-8",
    )

    np.savetxt(
        output / "confusion_matrix.csv",
        cm,
        delimiter=",",
        fmt="%d",
    )

    print("\nHASIL EVALUASI:")
    print(json.dumps(results, indent=2))
    print("\n", report)
    print("\nHasil tersimpan di:", output)


if __name__ == "__main__":
    main()
