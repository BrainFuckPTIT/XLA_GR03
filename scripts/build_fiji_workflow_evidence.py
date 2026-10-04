"""Render a visual audit trail from real Fiji/ImageJ StarDist artefacts.

The figure intentionally reads the input TIFF, the plugin's saved Label Image,
the ground truth TIFF and the CSV run log.  It never invents a segmentation for
the report; regenerating it therefore verifies that all visual claims point to
the same median case used by the quantitative evaluator.
"""

from __future__ import annotations

import csv
from collections.abc import Callable
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tifffile
from skimage.segmentation import find_boundaries

ROOT = Path(__file__).resolve().parents[1]
MEDIAN_IMAGE = "b61d3fb0d0ebbee018346e0adeff9e9178f33aa95262779b3c196f93b4ace895.tif"
IMAGE_PATH = ROOT / "data" / "dsb2018" / "dsb2018" / "test" / "images" / MEDIAN_IMAGE
GROUND_TRUTH_PATH = ROOT / "data" / "dsb2018" / "dsb2018" / "test" / "masks" / MEDIAN_IMAGE
PREDICTION_PATH = ROOT / "results" / "fiji_labels" / MEDIAN_IMAGE
RUN_LOG_PATH = ROOT / "fiji" / "run_log_dsb2018_reference.csv"
METRICS_PATH = ROOT / "results" / "fiji_reference" / "per_image_metrics.csv"
OUTPUT_PATH = ROOT / "results" / "fiji_reference" / "fiji_workflow_evidence.png"


def read_row(path: Path, predicate: Callable[[dict[str, str]], bool]) -> dict[str, str]:
    """Return exactly one CSV row accepted by ``predicate``."""
    with path.open(newline="", encoding="utf-8") as stream:
        rows = [row for row in csv.DictReader(stream) if predicate(row)]
    if len(rows) != 1:
        raise ValueError(f"Expected one matching row in {path}, found {len(rows)}")
    return rows[0]


def normalize_percentile(image: np.ndarray, low: float, high: float) -> np.ndarray:
    """Match the percentile clipping recorded for the Fiji plugin run."""
    lower, upper = np.percentile(image, (low, high))
    return np.clip((image.astype(np.float32) - lower) / (upper - lower + 1e-8), 0, 1)


def label_rgb(labels: np.ndarray) -> np.ndarray:
    """Make a deterministic colour view while keeping label zero black."""
    rgb = plt.get_cmap("tab20")((labels.astype(np.int64) * 7) % 20)[..., :3]
    rgb[labels == 0] = 0
    return rgb


def overlay_boundaries(
    image: np.ndarray,
    ground_truth: np.ndarray,
    prediction: np.ndarray,
) -> np.ndarray:
    """Show GT in green, Fiji prediction in magenta and agreeing edges in yellow."""
    overlay = np.repeat(image[..., None], 3, axis=2)
    gt_edges = find_boundaries(ground_truth, mode="outer")
    prediction_edges = find_boundaries(prediction, mode="outer")
    overlay[gt_edges] = (0.1, 1.0, 0.2)
    overlay[prediction_edges] = (1.0, 0.1, 0.9)
    overlay[gt_edges & prediction_edges] = (1.0, 0.9, 0.1)
    return overlay


def hide_axis(axis: plt.Axes) -> None:
    axis.set_xticks([])
    axis.set_yticks([])
    for spine in axis.spines.values():
        spine.set_visible(False)


def main() -> None:
    required = (IMAGE_PATH, GROUND_TRUTH_PATH, PREDICTION_PATH, RUN_LOG_PATH, METRICS_PATH)
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required Fiji evidence: " + ", ".join(missing))

    run = read_row(RUN_LOG_PATH, lambda row: row["tag"] == "median")
    metric = read_row(
        METRICS_PATH,
        lambda row: row["tag"] == "median" and float(row["threshold"]) == 0.5,
    )
    image = tifffile.imread(IMAGE_PATH)
    ground_truth = tifffile.imread(GROUND_TRUTH_PATH)
    prediction = tifffile.imread(PREDICTION_PATH)
    normalized = normalize_percentile(
        image,
        float(run["percentile_low"]),
        float(run["percentile_high"]),
    )

    figure = plt.figure(figsize=(15.5, 8.6), constrained_layout=True)
    grid = figure.add_gridspec(2, 3, height_ratios=(1.0, 0.92))
    axes = [figure.add_subplot(grid[0, column]) for column in range(3)]
    axes.extend(figure.add_subplot(grid[1, column]) for column in range(3))

    axes[0].imshow(image, cmap="gray")
    axes[0].set_title("Bước 1 - TIFF input", fontweight="bold")
    axes[1].imshow(normalized, cmap="gray", vmin=0, vmax=1)
    axes[1].set_title("Bước 2 - Normalize 1/99.8", fontweight="bold")
    axes[2].imshow(label_rgb(prediction))
    axes[2].set_title("Bước 3 - Label Image Fiji", fontweight="bold")
    axes[3].imshow(overlay_boundaries(normalized, ground_truth, prediction))
    axes[3].set_title("Bước 4 - Overlay để đối chiếu", fontweight="bold")
    for axis in axes[:4]:
        hide_axis(axis)

    axes[4].axis("off")
    axes[4].set_title("Bước 5 - Metric instance (IoU = 0.50)", fontweight="bold", loc="left")
    metric_lines = [
        f"GT / prediction: {metric['true_objects']} / {metric['predicted_objects']}",
        "TP / FP / FN: "
        f"{metric['true_positives']} / {metric['false_positives']} / {metric['false_negatives']}",
        f"AP: {float(metric['accuracy']):.4f}",
        f"PQ: {float(metric['panoptic_quality']):.4f}",
        f"Dice foreground: {float(metric['foreground_dice']):.4f}",
        f"Count absolute error: {metric['count_absolute_error']}",
    ]
    axes[4].text(0.02, 0.95, "\n".join(metric_lines), va="top", fontsize=11, family="monospace")

    axes[5].axis("off")
    axes[5].set_title("Log plugin thực tế", fontweight="bold", loc="left")
    parameter_lines = [
        f"Artifact: {run['plugin_artifact']}",
        f"Model: {run['model']}",
        f"Probability / NMS: {run['probability_threshold']} / {run['nms_overlap_threshold']}",
        f"Tiles / boundary: {run['n_tiles']} / {run['boundary_exclusion']} px",
        f"Runtime: {float(run['runtime_s']):.3f} s ({run['status']})",
        "Edge colour: green=GT, magenta=Fiji, yellow=both",
    ]
    axes[5].text(
        0.02,
        0.95,
        "\n".join(parameter_lines),
        va="top",
        fontsize=10.2,
        family="monospace",
        wrap=True,
    )

    figure.suptitle(
        "Chuỗi bằng chứng tái lập Fiji/ImageJ - ca median DSB2018",
        fontsize=16,
        fontweight="bold",
    )
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT_PATH, dpi=220, bbox_inches="tight")
    plt.close(figure)
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
