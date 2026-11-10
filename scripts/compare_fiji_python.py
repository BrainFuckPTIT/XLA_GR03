"""Compare fixed Fiji labels directly against rerun Python labels, with error overlays."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from tifffile import imread

from xla_gr03.experiments import sha256, write_csv
from xla_gr03.metrics import evaluate_instances, matched_label_pairs
from xla_gr03.preprocessing import percentile_normalize

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/cross_platform"


def compare_labels(python: np.ndarray, fiji: np.ndarray) -> tuple[dict, np.ndarray]:
    metric = evaluate_instances(python, fiji)
    pairs = matched_label_pairs(python, fiji)
    paired_python = [a for a, _, _ in pairs]
    paired_fiji = [b for _, b, _ in pairs]
    # ID-invariant pixel agreement on foreground union; background does not dominate.
    same = np.zeros(python.shape, dtype=bool)
    for a, b, _ in pairs:
        same |= (python == a) & (fiji == b)
    union = (python > 0) | (fiji > 0)
    error = np.zeros((*python.shape, 3), dtype=np.float32)
    error[(python > 0) & ~np.isin(python, paired_python)] = (0, 1, 0)
    error[(fiji > 0) & ~np.isin(fiji, paired_fiji)] = (1, 0, 1)
    error[union & ~same & ~np.any(error > 0, axis=-1)] = (1, 0.7, 0)
    return {
        "python_objects": metric.true_objects,
        "fiji_objects": metric.predicted_objects,
        "matched_objects": metric.true_positives,
        "unmatched_python": metric.false_negatives,
        "unmatched_fiji": metric.false_positives,
        "f1_iou_050": metric.f1,
        "mean_matched_iou": metric.mean_matched_iou,
        "foreground_dice": metric.foreground_dice,
        "matched_pixel_agreement_foreground": float(same.sum() / union.sum()) if union.any() else 1,
        "criterion_f1_095_dice_095": metric.f1 >= 0.95 and metric.foreground_dice >= 0.95,
    }, error


def main() -> None:
    with (ROOT / "fiji/run_log_dsb2018_reference.csv").open(newline="", encoding="utf-8") as stream:
        cases = list(csv.DictReader(stream))
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    fig, axes = plt.subplots(len(cases), 3, figsize=(12, 10), constrained_layout=True)
    for index, case in enumerate(cases):
        name, tag = case["image"], case["tag"]
        py_path = ROOT / f"results/dsb2018_benchmark/selected_labels/{tag}/stardist_python.tif"
        fj_path = ROOT / "results/fiji_labels" / name
        py, fj = imread(py_path), imread(fj_path)
        scores, errors = compare_labels(py, fj)
        rows.append(
            {
                "tag": tag,
                "image": name,
                **scores,
                "python_sha256": sha256(py_path),
                "fiji_sha256": sha256(fj_path),
                "model": "versatile fluorescent nuclei",
                "prob_thresh": float(case["probability_threshold"]),
                "nms_thresh": float(case["nms_overlap_threshold"]),
                "python_normalization": "numpy linear percentile; clip=False",
                "fiji_normalization": "CSBDeep Java histogram percentile; clip=False",
                "python_boundary": "official model default",
                "fiji_boundary": case["boundary_exclusion"],
            }
        )
        image = imread(ROOT / "data/dsb2018/dsb2018/test/images" / name)
        background = np.repeat(np.clip(percentile_normalize(image), 0, 1)[..., None], 3, axis=2)
        overlay = background.copy()
        active = np.any(errors > 0, axis=-1)
        overlay[active] = errors[active]
        for axis, array, title in zip(
            axes[index],
            (py, fj, overlay),
            ("Python", "Fiji", "Unmatched objects / boundaries"),
            strict=True,
        ):
            axis.imshow(array, cmap="nipy_spectral" if array.ndim == 2 else None)
            axis.set_title(f"{tag}: {title}")
            axis.axis("off")
    fig.suptitle("Green: Python unmatched; magenta: Fiji unmatched; amber: pixel disagreement")
    fig.savefig(OUT / "error_overlays.png", dpi=200)
    plt.close(fig)
    write_csv(OUT / "comparison.csv", rows)
    (OUT / "provenance.json").write_text(
        json.dumps(
            {
                "comparison": "Python labels used as reference, not as biological ground truth",
                "criterion": "F1 matching@0.50 >= 0.95 AND foreground Dice >= 0.95",
                "criterion_scope": "descriptive acceptance threshold, not statistical equivalence",
                "cases": "historical test-derived fixed cases; not a random sample",
                "normalization_limit": "numpy linear and Java histogram percentiles differ",
                "runtime_limit": "Fiji cold command vs Python warm segmentation; no speed ranking",
                "label_id_policy": "pixel agreement after matching; foreground union only",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
