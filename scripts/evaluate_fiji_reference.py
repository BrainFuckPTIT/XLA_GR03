"""Evaluate real ImageJ/Fiji StarDist label images against DSB2018 masks.

The Java runner in ``fiji/scripts/FijiStarDistRunner.java`` creates the label
TIFFs. This script deliberately only measures already-produced labels, keeping
the ImageJ/Fiji execution and the team's Python metric implementation separate.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from skimage.color import label2rgb
from tifffile import imread

from xla_gr03.metrics import evaluate_at_thresholds

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SELECTED = ROOT / "results" / "dsb2018_benchmark" / "selected_cases.csv"
DEFAULT_LABELS = ROOT / "results" / "fiji_labels"
DEFAULT_MASKS = ROOT / "data" / "dsb2018" / "dsb2018" / "test" / "masks"
DEFAULT_IMAGES = ROOT / "data" / "dsb2018" / "dsb2018" / "test" / "images"
DEFAULT_RUN_LOG = ROOT / "fiji" / "run_log_dsb2018_reference.csv"
DEFAULT_OUTPUT = ROOT / "results" / "fiji_reference"
THRESHOLDS = (0.5, 0.75, 0.9)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def evaluate_reference(
    selected: list[dict[str, str]],
    run_log: list[dict[str, str]],
    labels_dir: Path,
    masks_dir: Path,
) -> list[dict[str, object]]:
    """Return one row per selected case and IoU threshold."""

    runtimes = {row["image"]: row for row in run_log}
    rows: list[dict[str, object]] = []
    for case in selected:
        image_name = case["image"]
        prediction_path = labels_dir / image_name
        truth_path = masks_dir / image_name
        if not prediction_path.is_file():
            raise FileNotFoundError(f"Missing ImageJ/Fiji label image: {prediction_path}")
        prediction = imread(prediction_path)
        truth = imread(truth_path)
        if prediction.shape != truth.shape:
            raise ValueError(
                f"Shape mismatch for {image_name}: {prediction.shape} vs {truth.shape}"
            )
        log = runtimes.get(image_name)
        if log is None:
            raise ValueError(f"No matching runtime row for {image_name} in {DEFAULT_RUN_LOG}")
        for metric in evaluate_at_thresholds(truth, prediction, THRESHOLDS):
            rows.append(
                {
                    "tag": case["tag"],
                    "image": image_name,
                    "method": "StarDist Fiji/ImageJ plugin",
                    "runtime_s": float(log["runtime_s"]),
                    **metric.to_dict(),
                }
            )
    return rows


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Compute mean and sample standard deviation on the three fixed cases."""

    result: list[dict[str, object]] = []
    for threshold in THRESHOLDS:
        group = [row for row in rows if float(row["threshold"]) == threshold]
        summary: dict[str, object] = {
            "method": "StarDist Fiji/ImageJ plugin",
            "threshold": threshold,
            "n_images": len(group),
        }
        metric_names = (
            "accuracy",
            "panoptic_quality",
            "foreground_dice",
            "count_absolute_error",
            "runtime_s",
        )
        for name in metric_names:
            values = [float(row[name]) for row in group]
            summary[f"{name}_mean"] = statistics.mean(values)
            summary[f"{name}_sd"] = statistics.stdev(values) if len(values) > 1 else 0.0
        result.append(summary)
    return result


def _label_overlay(image: np.ndarray, labels: np.ndarray) -> np.ndarray:
    normalized = image.astype(np.float32)
    lower, upper = np.percentile(normalized, (1, 99.8))
    scaled = np.clip((normalized - lower) / max(upper - lower, 1e-6), 0, 1)
    return label2rgb(labels.astype(np.int32), image=scaled, bg_label=0, alpha=0.38)


def make_figure(
    selected: list[dict[str, str]],
    labels_dir: Path,
    masks_dir: Path,
    images_dir: Path,
    output: Path,
) -> None:
    """Save a three-case qualitative panel made from actual plugin outputs."""

    figure, axes = plt.subplots(
        len(selected), 3, figsize=(11, 3.5 * len(selected)), constrained_layout=True
    )
    if len(selected) == 1:
        axes = np.asarray([axes])
    headings = ("Input", "Ground truth", "StarDist Fiji/ImageJ output")
    for row_index, case in enumerate(selected):
        name = case["image"]
        image = imread(images_dir / name)
        truth = imread(masks_dir / name)
        prediction = imread(labels_dir / name)
        panels = (image, _label_overlay(image, truth), _label_overlay(image, prediction))
        for col_index, panel in enumerate(panels):
            axis = axes[row_index, col_index]
            axis.imshow(panel, cmap="gray" if col_index == 0 else None)
            axis.set_axis_off()
            if row_index == 0:
                axis.set_title(headings[col_index], fontsize=11, weight="bold")
        axes[row_index, 0].set_ylabel(
            f"{case['tag']}\n{Path(name).stem[:8]}",
            rotation=0,
            ha="right",
            va="center",
            fontsize=10,
        )
    figure.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selected", type=Path, default=DEFAULT_SELECTED)
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--masks", type=Path, default=DEFAULT_MASKS)
    parser.add_argument("--images", type=Path, default=DEFAULT_IMAGES)
    parser.add_argument("--run-log", type=Path, default=DEFAULT_RUN_LOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    selected = read_csv(args.selected)
    run_log = read_csv(args.run_log)
    rows = evaluate_reference(selected, run_log, args.labels, args.masks)
    summary_rows = summarize(rows)
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "per_image_metrics.csv", rows)
    write_csv(args.output / "summary_metrics.csv", summary_rows)
    make_figure(
        selected,
        args.labels,
        args.masks,
        args.images,
        args.output / "fiji_reference_panels.png",
    )
    provenance = {
        "n_selected_images": len(selected),
        "iou_thresholds": list(THRESHOLDS),
        "labels_source": (
            "Actual outputs of FijiStarDistRunner.java using "
            "de.csbdresden:StarDist_:0.3.0-scijava"
        ),
        "evaluation": "Python xla_gr03.metrics one-to-one IoU matching",
    }
    provenance_path = args.output / "provenance.json"
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} metric rows to {args.output}")


if __name__ == "__main__":
    main()
