"""Run a real, reproducible StarDist demonstration on its DSB2018 sample.

The official StarDist package distributes this fluorescence image and instance
mask as a sample from the 2018 Data Science Bowl. This script materializes the
sample locally, runs the three methods, exports TIFF labels/CSV/figures, and
marks the output as a one-image demonstration rather than a benchmark.
"""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from stardist.data import test_image_nuclei_2d
from stardist.models import StarDist2D
from tifffile import imwrite

from xla_gr03.baselines import segment_otsu, segment_watershed
from xla_gr03.io import save_labels
from xla_gr03.metrics import evaluate_at_thresholds, evaluate_instances
from xla_gr03.preprocessing import percentile_normalize

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "dsb2018_stardist_sample.tif"
GT = ROOT / "data" / "ground_truth" / "dsb2018_stardist_sample.tif"
OUT = ROOT / "results" / "real_demo"
LABELS = OUT / "labels"
FIGURES = OUT / "figures"
THRESHOLDS = (0.5, 0.75, 0.9)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def save_panel(image: np.ndarray, truth: np.ndarray, predictions: dict[str, np.ndarray]) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    panels = [("Input fluorescence", image), ("Ground truth", truth), *predictions.items()]
    figure, axes = plt.subplots(1, len(panels), figsize=(4 * len(panels), 4))
    for axis, (name, data) in zip(axes, panels, strict=True):
        axis.imshow(data, cmap="gray" if name == "Input fluorescence" else "nipy_spectral")
        axis.set_title(name)
        axis.axis("off")
    figure.tight_layout()
    figure.savefig(FIGURES / "qualitative_comparison.png", dpi=200, bbox_inches="tight")
    plt.close(figure)


def save_sweep_plot(rows: list[dict[str, object]], value: str, filename: str) -> None:
    figure, axis = plt.subplots(figsize=(6, 4))
    for method, marker in (("probability_sweep", "o"), ("nms_sweep", "s")):
        subset = [row for row in rows if row["sweep"] == method]
        x_key = "probability_threshold" if method == "probability_sweep" else "nms_threshold"
        axis.plot(
            [float(row[x_key]) for row in subset],
            [float(row[value]) for row in subset],
            marker=marker,
            label=method.replace("_", " "),
        )
    axis.set_xlabel("Threshold")
    axis.set_ylabel(value.replace("_", " "))
    axis.grid(alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(FIGURES / filename, dpi=200)
    plt.close(figure)


def predict(
    model: StarDist2D,
    image: np.ndarray,
    probability_threshold: float,
    nms_threshold: float,
) -> tuple[np.ndarray, float]:
    normalized = percentile_normalize(image, pmin=1.0, pmax=99.8, axes=(0, 1))
    start = time.perf_counter()
    labels, _ = model.predict_instances(
        normalized,
        axes="YX",
        prob_thresh=probability_threshold,
        nms_thresh=nms_threshold,
    )
    return np.asarray(labels, dtype=np.int32), time.perf_counter() - start


def main() -> None:
    np.random.seed(42)
    image, truth = test_image_nuclei_2d(return_mask=True)
    RAW.parent.mkdir(parents=True, exist_ok=True)
    GT.parent.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    imwrite(RAW, image)
    imwrite(GT, truth.astype(np.uint16))

    methods: dict[str, tuple[np.ndarray, float, dict[str, object]]] = {}
    for name, method in (
        ("otsu", lambda: segment_otsu(image, foreground="bright", min_size=20)),
        (
            "watershed",
            lambda: segment_watershed(
                image, foreground="bright", min_size=20, min_distance=7
            ),
        ),
    ):
        start = time.perf_counter()
        result = method()
        methods[name] = (result.labels, time.perf_counter() - start, result.metadata)

    model = StarDist2D.from_pretrained("2D_versatile_fluo")
    # Warm-up downloads/builds the model before the recorded inference.
    predict(model, image, probability_threshold=0.5, nms_threshold=0.3)
    labels, elapsed = predict(model, image, probability_threshold=0.5, nms_threshold=0.3)
    methods["stardist_python"] = (
        labels,
        elapsed,
        {
            "model": "2D_versatile_fluo",
            "pmin": 1.0,
            "pmax": 99.8,
            "probability_threshold": 0.5,
            "nms_threshold": 0.3,
            "device": "CPU",
        },
    )

    rows: list[dict[str, object]] = []
    panels: dict[str, np.ndarray] = {}
    for name, (prediction, elapsed, metadata) in methods.items():
        save_labels(LABELS / f"{name}.tif", prediction)
        panels[name] = prediction
        for metric in evaluate_at_thresholds(truth, prediction, THRESHOLDS):
            rows.append(
                {
                    "method": name,
                    "runtime_s": round(elapsed, 6),
                    "source": "official StarDist DSB2018 sample",
                    **metadata,
                    **metric.to_dict(),
                }
            )
    write_csv(OUT / "metrics_per_threshold.csv", rows)
    save_panel(image, truth, panels)

    sweep_rows: list[dict[str, object]] = []
    for probability_threshold in (0.3, 0.4, 0.5, 0.6, 0.7):
        prediction, elapsed = predict(model, image, probability_threshold, 0.3)
        metric = evaluate_instances(truth, prediction, threshold=0.5)
        sweep_rows.append(
            {
                "sweep": "probability_sweep",
                "probability_threshold": probability_threshold,
                "nms_threshold": 0.3,
                "runtime_s": round(elapsed, 6),
                **metric.to_dict(),
            }
        )
    for nms_threshold in (0.1, 0.2, 0.3, 0.4, 0.5):
        prediction, elapsed = predict(model, image, 0.5, nms_threshold)
        metric = evaluate_instances(truth, prediction, threshold=0.5)
        sweep_rows.append(
            {
                "sweep": "nms_sweep",
                "probability_threshold": 0.5,
                "nms_threshold": nms_threshold,
                "runtime_s": round(elapsed, 6),
                **metric.to_dict(),
            }
        )
    write_csv(OUT / "stardist_threshold_sweep.csv", sweep_rows)
    save_sweep_plot(sweep_rows, "accuracy", "threshold_vs_ap050.png")
    save_sweep_plot(sweep_rows, "predicted_objects", "threshold_vs_object_count.png")
    (OUT / "provenance.json").write_text(
        json.dumps(
            {
                "dataset": "StarDist distributed DSB2018 fluorescence sample",
                "source": "https://github.com/stardist/stardist",
                "sample_count": 1,
                "caveat": "Demonstration only. This single image is not an independent test set.",
                "model": "2D_versatile_fluo",
                "random_seed": 42,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
