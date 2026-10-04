"""Reproduce a multi-image DSB2018 benchmark for StarDist and two baselines.

The archive is the official split distributed by the StarDist project. The
training partition selects the marker spacing for Watershed; the separate test
partition reports the final metrics. The pretrained StarDist model runs with
its published default thresholds, without tuning on this benchmark's test set.
"""

from __future__ import annotations

import csv
import json
import statistics
import time
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from stardist.models import StarDist2D
from tifffile import imread

from xla_gr03.baselines import segment_otsu, segment_watershed
from xla_gr03.io import save_labels
from xla_gr03.metrics import evaluate_at_thresholds, evaluate_instances
from xla_gr03.preprocessing import percentile_normalize

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dsb2018"
ARCHIVE = DATA / "dsb2018.zip"
DATASET_ROOT = DATA / "dsb2018"
RESULTS = ROOT / "results" / "dsb2018_benchmark"
URL = "https://github.com/stardist/stardist/releases/download/0.1.0/dsb2018.zip"
IOU_THRESHOLDS = (0.5, 0.75, 0.9)
VALIDATION_MIN_DISTANCE = (3, 5, 7, 9, 11)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def ensure_dataset() -> None:
    test_dir = DATASET_ROOT / "test" / "images"
    if test_dir.is_dir() and any(test_dir.glob("*.tif")):
        return
    DATA.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE.exists():
        print(f"Downloading {URL}")
        urllib.request.urlretrieve(URL, ARCHIVE)
    with zipfile.ZipFile(ARCHIVE) as archive:
        archive.extractall(DATA)
    if not test_dir.is_dir() or not any(test_dir.glob("*.tif")):
        raise RuntimeError("The official archive did not contain test image TIFF files.")


def paired_files(split: str) -> list[tuple[Path, Path]]:
    image_dir = DATASET_ROOT / split / "images"
    mask_dir = DATASET_ROOT / split / "masks"
    pairs = [(path, mask_dir / path.name) for path in sorted(image_dir.glob("*.tif"))]
    missing = [mask for _, mask in pairs if not mask.is_file()]
    if missing:
        raise RuntimeError(f"Missing {len(missing)} masks in {mask_dir}")
    if not pairs:
        raise RuntimeError(f"No TIFF pairs found in {image_dir}")
    return pairs


def choose_watershed_distance(
    validation: list[tuple[Path, Path]],
) -> tuple[int, list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    for distance in VALIDATION_MIN_DISTANCE:
        scores: list[float] = []
        for image_path, mask_path in validation:
            prediction = segment_watershed(
                imread(image_path), foreground="bright", min_size=20, min_distance=distance
            ).labels
            scores.append(evaluate_instances(imread(mask_path), prediction, threshold=0.5).accuracy)
        rows.append(
            {
                "min_distance": distance,
                "n_validation": len(scores),
                "ap_iou_050_mean": float(statistics.mean(scores)),
                "ap_iou_050_sd": float(statistics.stdev(scores)) if len(scores) > 1 else 0.0,
            }
        )
    best = max(rows, key=lambda row: (float(row["ap_iou_050_mean"]), -int(row["min_distance"])))
    return int(best["min_distance"]), rows


def predict_stardist(
    model: StarDist2D, image: np.ndarray
) -> tuple[np.ndarray, float, float, float]:
    normalized = percentile_normalize(image, pmin=1.0, pmax=99.8, axes=(0, 1))
    probability_threshold = float(model.thresholds.prob)
    nms_threshold = float(model.thresholds.nms)
    start = time.perf_counter()
    labels, _ = model.predict_instances(
        normalized,
        axes="YX",
        prob_thresh=probability_threshold,
        nms_thresh=nms_threshold,
    )
    return (
        np.asarray(labels, dtype=np.int32),
        time.perf_counter() - start,
        probability_threshold,
        nms_threshold,
    )


def make_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, float], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["method"]), float(row["threshold"]))].append(row)
    summary: list[dict[str, object]] = []
    for (method, threshold), values in sorted(grouped.items()):
        numbers_by_metric = {
            key: [float(value[key]) for value in values]
            for key in (
                "accuracy",
                "panoptic_quality",
                "foreground_dice",
                "count_absolute_error",
                "runtime_s",
            )
        }

        def avg(key: str, numbers=numbers_by_metric) -> float:
            return float(statistics.mean(numbers[key]))

        def sd(key: str, numbers=numbers_by_metric) -> float:
            return float(statistics.stdev(numbers[key])) if len(numbers[key]) > 1 else 0.0

        summary.append(
            {
                "method": method,
                "threshold": threshold,
                "n_test": len(values),
                "accuracy_mean": avg("accuracy"),
                "accuracy_sd": sd("accuracy"),
                "panoptic_quality_mean": avg("panoptic_quality"),
                "panoptic_quality_sd": sd("panoptic_quality"),
                "foreground_dice_mean": avg("foreground_dice"),
                "foreground_dice_sd": sd("foreground_dice"),
                "count_absolute_error_mean": avg("count_absolute_error"),
                "runtime_s_mean": avg("runtime_s"),
            }
        )
    return summary


def make_figure(summary: list[dict[str, object]]) -> None:
    rows_at_threshold = {
        str(row["method"]): row for row in summary if float(row["threshold"]) == 0.5
    }
    subset = [rows_at_threshold[method] for method in ("Otsu", "Watershed", "StarDist Python")]
    labels = [str(row["method"]) for row in subset]
    ap = [float(row["accuracy_mean"]) for row in subset]
    pq = [float(row["panoptic_quality_mean"]) for row in subset]
    x = np.arange(len(labels))
    figure, axis = plt.subplots(figsize=(7, 4.5))
    width = 0.36
    axis.bar(x - width / 2, ap, width, label="AP@0.50")
    axis.bar(x + width / 2, pq, width, label="PQ@0.50")
    axis.set_ylabel("Mean score on official test split")
    axis.set_ylim(0, 1)
    axis.set_xticks(x, labels)
    axis.legend()
    axis.grid(axis="y", alpha=0.25)
    figure.tight_layout()
    figure.savefig(RESULTS / "figures" / "benchmark_ap_pq.png", dpi=200)
    plt.close(figure)


def save_qualitative_panel(
    image_path: Path,
    min_distance: int,
    model: StarDist2D,
    tag: str,
) -> None:
    """Save raw/GT/predictions and TIFF labels for one selected test image."""

    image = imread(image_path)
    truth = imread(DATASET_ROOT / "test" / "masks" / image_path.name)
    otsu = segment_otsu(image, foreground="bright", min_size=20).labels
    watershed = segment_watershed(
        image, foreground="bright", min_size=20, min_distance=min_distance
    ).labels
    stardist, _, _, _ = predict_stardist(model, image)
    predictions = {
        "Otsu": otsu,
        "Watershed": watershed,
        "StarDist Python": stardist,
    }
    label_dir = RESULTS / "selected_labels" / tag
    for method, labels in predictions.items():
        save_labels(label_dir / f"{method.lower().replace(' ', '_')}.tif", labels)
    save_labels(label_dir / "ground_truth.tif", truth)
    figure, axes = plt.subplots(1, 5, figsize=(18, 4))
    panels = [("Input", image), ("Ground truth", truth), *predictions.items()]
    for axis, (title, array) in zip(axes, panels, strict=True):
        axis.imshow(array, cmap="gray" if title == "Input" else "nipy_spectral")
        axis.set_title(title)
        axis.axis("off")
    figure.suptitle(f"Representative {tag} case selected by StarDist AP@0.50", y=1.02)
    figure.tight_layout()
    figure.savefig(RESULTS / "figures" / f"qualitative_{tag}.png", dpi=200, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    ensure_dataset()
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "figures").mkdir(exist_ok=True)
    all_train = paired_files("train")
    validation_indices = np.random.default_rng(42).choice(
        len(all_train), size=min(30, len(all_train)), replace=False
    )
    validation = [all_train[index] for index in sorted(validation_indices)]
    test = paired_files("test")
    selected_distance, validation_rows = choose_watershed_distance(validation)
    write_csv(RESULTS / "watershed_validation_sweep.csv", validation_rows)

    model = StarDist2D.from_pretrained("2D_versatile_fluo")
    # Build the TensorFlow graph before recording inference times.
    predict_stardist(model, imread(test[0][0]))
    rows: list[dict[str, object]] = []
    for image_path, mask_path in test:
        image = imread(image_path)
        truth = imread(mask_path)
        runs: list[tuple[str, np.ndarray, float, dict[str, object]]] = []
        start = time.perf_counter()
        otsu = segment_otsu(image, foreground="bright", min_size=20)
        runs.append(("Otsu", otsu.labels, time.perf_counter() - start, otsu.metadata))
        start = time.perf_counter()
        watershed = segment_watershed(
            image, foreground="bright", min_size=20, min_distance=selected_distance
        )
        runs.append(
            ("Watershed", watershed.labels, time.perf_counter() - start, watershed.metadata)
        )
        stardist, elapsed, probability_threshold, nms_threshold = predict_stardist(model, image)
        runs.append(
            (
                "StarDist Python",
                stardist,
                elapsed,
                {
                    "model": "2D_versatile_fluo",
                    "pmin": 1.0,
                    "pmax": 99.8,
                    "probability_threshold": probability_threshold,
                    "nms_threshold": nms_threshold,
                },
            )
        )
        for method, prediction, elapsed, metadata in runs:
            for metric in evaluate_at_thresholds(truth, prediction, IOU_THRESHOLDS):
                rows.append(
                    {
                        "image": image_path.name,
                        "method": method,
                        "runtime_s": elapsed,
                        **metadata,
                        **metric.to_dict(),
                    }
                )
    write_csv(RESULTS / "per_image_metrics.csv", rows)
    summary = make_summary(rows)
    write_csv(RESULTS / "summary_metrics.csv", summary)
    make_figure(summary)
    stardist_ap = sorted(
        (
            row
            for row in rows
            if row["method"] == "StarDist Python" and float(row["threshold"]) == 0.5
        ),
        key=lambda row: float(row["accuracy"]),
    )
    selected_positions = {"low": 0, "median": len(stardist_ap) // 2, "high": -1}
    image_index = {path.name: path for path, _ in test}
    selected_rows: list[dict[str, object]] = []
    for tag, position in selected_positions.items():
        row = stardist_ap[position]
        image_path = image_index[str(row["image"])]
        save_qualitative_panel(image_path, selected_distance, model, tag)
        selected_rows.append(
            {
                "tag": tag,
                "image": image_path.name,
                "stardist_ap_iou_050": row["accuracy"],
                "selection_rule": (
                    "min, median, or max StarDist AP@0.50 over the complete test split"
                ),
            }
        )
    write_csv(RESULTS / "selected_cases.csv", selected_rows)
    (RESULTS / "provenance.json").write_text(
        json.dumps(
            {
                "dataset": "Official StarDist DSB2018 archive",
                "archive_url": URL,
                "train_images_for_validation": len(validation),
                "test_images": len(test),
                "watershed_min_distance_selected_on_train": selected_distance,
                "stardist_model": "2D_versatile_fluo",
                "stardist_threshold_policy": "model default thresholds; no test-set tuning",
                "device": "CPU",
                "qualitative_selection": "min/median/max StarDist AP@0.50 over all test images",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
