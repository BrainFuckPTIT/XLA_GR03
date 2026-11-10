"""Sweep probability/NMS on the fixed validation split, without tuning on test."""

from __future__ import annotations

import csv
import json
import statistics

import matplotlib.pyplot as plt
import tensorflow as tf
from run_dsb2018_benchmark import DATASET_ROOT, RESULTS, predict_stardist
from stardist.models import StarDist2D
from tifffile import imread

from xla_gr03.experiments import runtime_provenance, write_csv
from xla_gr03.metrics import evaluate_instances
from xla_gr03.preprocessing import percentile_normalize

OUT = RESULTS.parent / "validation_ablation"
SWEEPS = {"probability": (0.3, 0.4, 0.5, 0.6, 0.7), "nms": (0.1, 0.2, 0.3, 0.4, 0.5)}


def main() -> None:
    tf.config.set_visible_devices([], "GPU")
    with (RESULTS / "validation_images.csv").open(newline="", encoding="utf-8") as stream:
        images = [row["image"] for row in csv.DictReader(stream)]
    if not images:
        raise ValueError("Run the benchmark first to fix the validation split.")
    model = StarDist2D.from_pretrained("2D_versatile_fluo")
    predict_stardist(model, imread(DATASET_ROOT / "train" / "images" / images[0]))
    rows = []
    for name in images:
        print(f"Validation sweep {name}", flush=True)
        image = percentile_normalize(
            imread(DATASET_ROOT / "train" / "images" / name), axes=(0, 1), clip=False
        )
        truth = imread(DATASET_ROOT / "train" / "masks" / name)
        examples = [("Normalized input", image), ("Ground truth", truth)]
        # Reuse the CNN prediction: this sweep studies only postprocessing thresholds.
        probability, distances = model.predict(image, axes="YX", verbose=0)
        for sweep, values in SWEEPS.items():
            for value in values:
                prob = value if sweep == "probability" else float(model.thresholds.prob)
                nms = value if sweep == "nms" else float(model.thresholds.nms)
                labels, _ = model._instances_from_prediction(
                    image.shape, probability, distances, prob_thresh=prob, nms_thresh=nms
                )
                metric = evaluate_instances(truth, labels)
                if name == images[0] and value in (values[0], values[-1]):
                    examples.append(
                        (
                            f"{sweep}={value}\nFP/FN={metric.false_positives}/{metric.false_negatives}",
                            labels,
                        )
                    )
                rows.append(
                    {
                        "image": name,
                        "sweep": sweep,
                        "value": value,
                        "probability_threshold": prob,
                        "nms_threshold": nms,
                        **metric.to_dict(),
                    }
                )
        if name == images[0]:
            OUT.mkdir(parents=True, exist_ok=True)
            fig, axes = plt.subplots(2, 3, figsize=(12, 8), constrained_layout=True)
            for index, (axis, (title, array)) in enumerate(zip(axes.flat, examples, strict=True)):
                axis.imshow(array, cmap="gray" if index == 0 else "nipy_spectral")
                axis.set_title(title, fontsize=10)
                axis.axis("off")
            fig.suptitle(f"First fixed validation ID: {name[:12]} (not selected by score)")
            fig.savefig(OUT / "threshold_examples.png", dpi=180)
            plt.close(fig)
    summary = []
    for sweep, values in SWEEPS.items():
        for value in values:
            group = [r for r in rows if r["sweep"] == sweep and r["value"] == value]
            result = {"sweep": sweep, "value": value, "n_validation": len(group)}
            for key in (
                "accuracy",
                "f1",
                "panoptic_quality",
                "predicted_objects",
                "count_absolute_error",
                "false_positives",
                "false_negatives",
            ):
                numbers = [r[key] for r in group]
                result[f"{key}_mean"] = statistics.mean(numbers)
                result[f"{key}_sd"] = statistics.stdev(numbers) if len(numbers) > 1 else 0.0
            summary.append(result)
    write_csv(OUT / "per_image_metrics.csv", rows)
    write_csv(OUT / "summary_metrics.csv", summary)
    for sweep in SWEEPS:
        group = [r for r in summary if r["sweep"] == sweep]
        fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
        for axis, key, label in zip(
            axes, ("accuracy", "predicted_objects"), ("AP@0.50", "Mean object count"), strict=True
        ):
            axis.errorbar(
                [r["value"] for r in group],
                [r[f"{key}_mean"] for r in group],
                yerr=[r[f"{key}_sd"] for r in group],
                marker="o",
                capsize=4,
            )
            axis.set(xlabel=f"{sweep} threshold", ylabel=label)
            axis.grid(alpha=0.25)
        fig.savefig(OUT / f"{sweep}_sweep.png", dpi=200)
        plt.close(fig)
    (OUT / "provenance.json").write_text(
        json.dumps(
            {
                "split": "30 fixed train-validation images; no test images",
                "images": images,
                "sweeps": SWEEPS,
                "normalization_clip": False,
                "fixed_probability": float(model.thresholds.prob),
                "fixed_nms": float(model.thresholds.nms),
                "test_parameter_policy": "model defaults retained; descriptive sweep only",
                "execution": "CNN maps cached per image; no inference runtime in sweep",
                "environment": runtime_provenance(model),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
