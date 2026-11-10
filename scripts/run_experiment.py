"""Run Otsu/Watershed on paired TIFF data and evaluate instance metrics.

StarDist outputs can be supplied as TIFF labels exported by Fiji or by the
Python StarDist CLI. The script never fabricates StarDist predictions: missing
files are reported as NA in the output table.
"""

from __future__ import annotations

import argparse
import csv
import math
import time
from pathlib import Path

from xla_gr03.baselines import segment_otsu, segment_watershed
from xla_gr03.experiments import paired_images, write_csv
from xla_gr03.io import read_image, save_labels
from xla_gr03.metrics import evaluate_instances


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, default=Path("data/raw"))
    parser.add_argument("--ground-truth", type=Path, default=Path("data/ground_truth"))
    parser.add_argument("--output", type=Path, default=Path("results/experiment"))
    parser.add_argument("--stardist-labels", type=Path, default=Path("results/fiji_labels"))
    parser.add_argument("--foreground", choices=("bright", "dark"), default="bright")
    parser.add_argument("--iou", type=float, default=0.5)
    parser.add_argument(
        "--run-log", type=Path, help="CSV with image,runtime_s for imported labels."
    )
    parser.add_argument("--allow-missing-stardist", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not 0 < args.iou <= 1:
        raise ValueError("IoU threshold must be in (0, 1].")
    rows: list[dict[str, object]] = []
    pairs = paired_images(args.images, args.ground_truth)
    missing = [p.name for p, _ in pairs if not (args.stardist_labels / p.name).is_file()]
    if missing and not args.allow_missing_stardist:
        raise ValueError(
            f"Missing {len(missing)} StarDist predictions: {', '.join(missing)}. "
            "Use --allow-missing-stardist to record explicit missing rows."
        )
    runtimes = {}
    if args.run_log:
        with args.run_log.open(newline="", encoding="utf-8") as stream:
            runtimes = {r["image"]: float(r["runtime_s"]) for r in csv.DictReader(stream)}
        if any(value < 0 or not math.isfinite(value) for value in runtimes.values()):
            raise ValueError("Runtime log must contain finite non-negative seconds.")
    for image_path, truth_path in pairs:
        image = read_image(image_path)
        truth = read_image(truth_path)
        methods = {
            "otsu": lambda image=image: segment_otsu(image, foreground=args.foreground),
            "watershed": lambda image=image: segment_watershed(image, foreground=args.foreground),
        }
        for name, run in methods.items():
            start = time.perf_counter()
            result = run()
            elapsed = time.perf_counter() - start
            save_labels(args.output / "labels" / name / image_path.name, result.labels)
            metric = evaluate_instances(truth, result.labels, threshold=args.iou)
            rows.append(
                {
                    "image": image_path.name,
                    "method": name,
                    "runtime_s": round(elapsed, 6),
                    "runtime_source": "preprocessing+segmentation; excludes file I/O",
                    "status": "ok",
                    **metric.to_dict(),
                }
            )
        stardist_path = args.stardist_labels / image_path.name
        row = {
            "image": image_path.name,
            "method": "stardist_imported",
            "runtime_s": runtimes.get(image_path.name),
            "runtime_source": "run log" if image_path.name in runtimes else "unavailable",
            "status": "ok" if stardist_path.is_file() else "missing_prediction",
        }
        if stardist_path.is_file():
            row.update(evaluate_instances(truth, read_image(stardist_path), args.iou).to_dict())
        rows.append(row)
    write_csv(args.output / "metrics.csv", rows)
    print(f"Evaluated {len(pairs)} image pairs; {len(missing)} missing StarDist predictions.")


if __name__ == "__main__":
    main()
