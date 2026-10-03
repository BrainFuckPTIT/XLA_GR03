"""Run Otsu/Watershed on paired TIFF data and evaluate instance metrics.

StarDist outputs can be supplied as TIFF labels exported by Fiji or by the
Python StarDist CLI. The script never fabricates StarDist predictions: missing
files are reported as NA in the output table.
"""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

from xla_gr03.baselines import segment_otsu, segment_watershed
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    files = sorted(
        path
        for path in args.images.glob("*.tif")
        if (args.ground_truth / path.name).is_file()
    )
    if not files:
        raise SystemExit(
            "No paired .tif files found. See data/README.md for the naming convention."
        )
    for image_path in files:
        image = read_image(image_path)
        truth = read_image(args.ground_truth / image_path.name)
        methods = {
            "otsu": lambda image=image: segment_otsu(
                image, foreground=args.foreground
            ),
            "watershed": lambda image=image: segment_watershed(
                image, foreground=args.foreground
            ),
        }
        stardist_path = args.stardist_labels / image_path.name
        if stardist_path.is_file():
            methods["stardist_fiji"] = lambda p=stardist_path: type(
                "Result", (), {"labels": read_image(p)}
            )()
        for name, run in methods.items():
            start = time.perf_counter()
            result = run()
            elapsed = time.perf_counter() - start
            if name != "stardist_fiji":
                save_labels(args.output / "labels" / name / image_path.name, result.labels)
            metric = evaluate_instances(truth, result.labels, threshold=args.iou)
            rows.append(
                {
                    "image": image_path.name,
                    "method": name,
                    "runtime_s": round(elapsed, 6),
                    **metric.to_dict(),
                }
            )
    fields = list(rows[0])
    with (args.output / "metrics_iou_050.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
