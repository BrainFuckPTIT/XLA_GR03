"""Build Beamer figures and vector-chart data from the verified experiment outputs."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path

import matplotlib as mpl
import numpy as np
from matplotlib.colors import hsv_to_rgb
from PIL import Image
from tifffile import imread

from xla_gr03.geometry import normalized_edt
from xla_gr03.metrics import matched_label_pairs
from xla_gr03.preprocessing import percentile_normalize

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSETS, DATA = HERE / "assets", HERE / "generated"


def read(relative):
    with (ROOT / relative).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def png(name, image):
    array = np.asarray(image)
    if array.dtype != np.uint8:
        array = np.rint(np.clip(array, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(array).save(ASSETS / f"{name}.png")


def colors(labels, truth=None):
    result = np.zeros((*labels.shape, 3), dtype=np.float32)
    ids = np.unique(labels[labels > 0])
    mapping = {int(i): int(i) for i in ids}
    if truth is not None:
        mapping = {int(i): None for i in ids}
        mapping.update({b: a for a, b, _ in matched_label_pairs(truth, labels)})
    for label in ids:
        key = mapping[int(label)]
        color = (1, 0.2, 0.3) if key is None else hsv_to_rgb([(key * 0.618034) % 1, 0.72, 0.98])
        result[labels == label] = color
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-maps", action="store_true", help="Recompute actual CNN maps.")
    args = parser.parse_args()
    ASSETS.mkdir(exist_ok=True)
    DATA.mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "report/assets/ptit-logo.jpg", ASSETS / "ptit-logo.jpg")
    cases = {r["tag"]: r for r in read("results/dsb2018_benchmark/selected_cases.csv")}
    case = cases["median"]
    raw = imread(ROOT / "data/dsb2018/dsb2018/test/images" / case["image"])
    base = ROOT / "results/dsb2018_benchmark/selected_labels/median"
    truth = imread(base / "ground_truth.tif")
    y0, x0 = (s // 2 - 96 for s in raw.shape)
    # Grid is 2 pixels, so use an even crop origin for the actual CNN probability map.
    y0, x0 = 2 * (y0 // 2), 2 * (x0 // 2)
    crop = (slice(y0, y0 + 192), slice(x0, x0 + 192))
    normalized = percentile_normalize(raw, axes=(0, 1), clip=False)
    png("median_input", normalized)
    png("crop_input", normalized[crop])
    png("median_gt", colors(truth))
    png("crop_gt", colors(truth)[crop])
    png("crop_binary", (truth[crop] > 0).astype(float))
    png("crop_edt", mpl.colormaps["viridis"](normalized_edt(truth)[crop])[..., :3])
    for method in ("otsu", "watershed", "stardist_python"):
        labels = imread(base / f"{method}.tif")
        rgb = colors(labels, truth)
        png(f"median_{method}", rgb)
        png(f"crop_{method}", rgb[crop])
    fiji = imread(ROOT / "results/fiji_labels" / case["image"])
    png("median_fiji", colors(fiji, truth))
    png("crop_fiji", colors(fiji, truth)[crop])
    # Annotate the two unmatched Fiji objects on the actual low-case image.
    low = cases["low"]
    low_py = imread(ROOT / "results/dsb2018_benchmark/selected_labels/low/stardist_python.tif")
    low_fj = imread(ROOT / "results/fiji_labels" / low["image"])
    low_raw = imread(ROOT / "data/dsb2018/dsb2018/test/images" / low["image"])
    unmatched = set(np.unique(low_fj[low_fj > 0])) - {
        b for _, b, _ in matched_label_pairs(low_py, low_fj)
    }
    low_rgb = np.repeat(np.clip(percentile_normalize(low_raw), 0, 1)[..., None], 3, axis=2)
    from scipy.ndimage import binary_dilation

    mask = np.isin(low_fj, list(unmatched))
    ring = binary_dilation(mask, iterations=4) & ~binary_dilation(mask, iterations=1)
    low_rgb[ring] = (1, 0.28, 0.32)
    png("low_unmatched", low_rgb)
    assert len(unmatched) == 2
    if args.model_maps or not (ASSETS / "crop_probability.png").is_file():
        import tensorflow as tf
        from stardist.models import StarDist2D

        tf.config.set_visible_devices([], "GPU")
        model = StarDist2D.from_pretrained("2D_versatile_fluo")
        probability, distances = model.predict(normalized, axes="YX", verbose=0)
        grid = tuple(model.config.grid)
        roi = (
            slice(y0 // grid[0], (y0 + 192) // grid[0]),
            slice(x0 // grid[1], (x0 + 192) // grid[1]),
        )
        png("crop_probability", mpl.colormaps["viridis"](probability[roi])[..., :3])
        # One actual radial channel, displayed on its own scale for visual explanation.
        radial = distances[roi][..., 0]
        upper = float(np.percentile(radial, 99))
        png("crop_ray", mpl.colormaps["magma"](np.clip(radial / upper, 0, 1))[..., :3])
        (DATA / "model_map_provenance.json").write_text(
            json.dumps(
                {
                    "image": case["image"],
                    "crop_yx": [y0, x0, 192, 192],
                    "model": "2D_versatile_fluo",
                    "grid_yx": grid,
                    "normalization": "NumPy percentile 1/99.8; clip=False",
                    "ray_channel": 0,
                    "ray_display_max_px": upper,
                    "probability_range": [0, 1],
                    "maps": "actual model.predict output",
                    "target_edt": "xla_gr03.geometry.normalized_edt on the full ground truth",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    summary = read("results/dsb2018_benchmark/summary_metrics.csv")
    lookup = {(r["method"], float(r["threshold"])): r for r in summary}
    names = [("Otsu", "Otsu"), ("Watershed", "Water"), ("StarDist Python", "Star")]
    commands, bench_rows, threshold_rows, secondary = [], [], [], []
    plot = ["x ap ap_sd pq pq_sd"]
    for index, (method, prefix) in enumerate(names):
        r = lookup[method, 0.5]
        for suffix, key, digits in (
            ("AP", "accuracy", 3),
            ("PQ", "panoptic_quality", 3),
            ("Dice", "foreground_dice", 3),
            ("MAE", "count_absolute_error", 2),
            ("Time", "runtime_s", 4),
        ):
            mean, sd = float(r[key + "_mean"]), float(r[key + "_sd"])
            commands.append(f"\\newcommand{{\\{prefix}{suffix}}}{{{mean:.{digits}f}}}")
            commands.append(f"\\newcommand{{\\{prefix}{suffix}SD}}{{{sd:.{digits}f}}}")
        label = "StarDist" if prefix == "Star" else method

        def pm(key, row=r):
            return f"${float(row[key + '_mean']):.3f}\\pm{float(row[key + '_sd']):.3f}$"

        bench_rows.append(f"{label} & {pm('accuracy')} & {pm('panoptic_quality')}\\\\")
        threshold_rows.append(
            label
            + " & "
            + " & ".join(
                f"${float(lookup[method, t]['accuracy_mean']):.3f}\\pm"
                f"{float(lookup[method, t]['accuracy_sd']):.3f}$"
                for t in (0.5, 0.75, 0.9)
            )
            + "\\\\"
        )
        secondary.append(
            f"{label} & {float(r['foreground_dice_mean']):.3f} & "
            f"{float(r['count_absolute_error_mean']):.2f} & "
            f"${float(r['runtime_s_mean']):.4f}\\pm{float(r['runtime_s_sd']):.4f}$\\\\"
        )
        plot.append(
            " ".join(
                map(
                    str,
                    [
                        index,
                        r["accuracy_mean"],
                        r["accuracy_sd"],
                        r["panoptic_quality_mean"],
                        r["panoptic_quality_sd"],
                    ],
                )
            )
        )
    commands += [
        "\\newcommand{\\BenchmarkRows}{%\n" + "\n".join(bench_rows) + "\n}",
        "\\newcommand{\\ThresholdRows}{%\n" + "\n".join(threshold_rows) + "\n}",
        "\\newcommand{\\SecondaryRows}{%\n" + "\n".join(secondary) + "\n}",
    ]
    cross_rows = []
    for row in read("results/cross_platform/comparison.csv"):
        cross_rows.append(
            f"{row['tag']} & {row['python_objects']} / {row['fiji_objects']} & "
            f"{float(row['f1_iou_050']):.3f} & {float(row['foreground_dice']):.3f}\\\\"
        )
    commands.append("\\newcommand{\\CrossRows}{%\n" + "\n".join(cross_rows) + "\n}")
    (DATA / "metrics.tex").write_text("\n".join(commands) + "\n", encoding="utf-8")
    (DATA / "benchmark.dat").write_text("\n".join(plot) + "\n", encoding="utf-8")
    rows = read("results/dsb2018_benchmark/watershed_validation_sweep.csv")
    (DATA / "watershed.dat").write_text(
        "distance ap sd\n"
        + "\n".join(
            f"{r['min_distance']} {r['ap_iou_050_mean']} {r['ap_iou_050_sd']}" for r in rows
        )
        + "\n"
    )
    for sweep in ("probability", "nms"):
        rows = [
            r
            for r in read("results/validation_ablation/summary_metrics.csv")
            if r["sweep"] == sweep
        ]
        (DATA / f"{sweep}.dat").write_text(
            "value ap sd count fn\n"
            + "\n".join(
                f"{r['value']} {r['accuracy_mean']} {r['accuracy_sd']} "
                f"{r['predicted_objects_mean']} {r['false_negatives_mean']}"
                for r in rows
            )
            + "\n"
        )
    assert len(summary) == 9 and len(cross_rows) == 3
    print("Prepared real image assets, actual CNN maps, 3-method tables and vector-chart data.")


if __name__ == "__main__":
    main()
