"""Generate report tables/macros and slide data from measured CSVs, never hand-entered scores."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from xla_gr03.experiments import write_csv

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report/generated"


def read(relative: str) -> list[dict]:
    with (ROOT / relative).open(newline="", encoding="utf-8") as stream:
        return [
            {
                k: float(v)
                if k not in {"method", "image", "sweep", "tag"}
                and v.replace(".", "", 1).replace("-", "", 1).isdigit()
                else v
                for k, v in row.items()
            }
            for row in csv.DictReader(stream)
        ]


def pm(row: dict, metric: str, digits: int = 3) -> str:
    return f"${row[metric + '_mean']:.{digits}f}\\pm{row[metric + '_sd']:.{digits}f}$"


def main() -> None:
    summary = read("results/dsb2018_benchmark/summary_metrics.csv")
    fiji = read("results/fiji_reference/summary_metrics.csv")
    cross = read("results/cross_platform/comparison.csv")
    ablation = read("results/validation_ablation/summary_metrics.csv")
    watershed = read("results/dsb2018_benchmark/watershed_validation_sweep.csv")
    methods = ("Otsu", "Watershed", "StarDist Python")
    lookup = {(r["method"], r["threshold"]): r for r in summary}
    OUT.mkdir(parents=True, exist_ok=True)
    main_rows, secondary, final = [], [], []
    macros = []
    for method, prefix in zip(methods, ("Otsu", "Water", "Star"), strict=True):
        r = lookup[method, 0.5]
        values = [pm(lookup[method, t], "accuracy") for t in (0.5, 0.75, 0.9)]
        main_rows.append(" & ".join([method, *values, pm(r, "panoptic_quality")]) + r"\\")
        secondary.append(
            " & ".join(
                [
                    method,
                    pm(r, "foreground_dice"),
                    pm(r, "count_absolute_error", 2),
                    pm(r, "runtime_s", 4),
                ]
            )
            + r"\\"
        )
        for suffix, metric in (
            ("AP", "accuracy"),
            ("PQ", "panoptic_quality"),
            ("Dice", "foreground_dice"),
        ):
            macros.append(f"\\newcommand{{\\{prefix}{suffix}}}{{{pm(r, metric)}}}")
        macros.append(f"\\newcommand{{\\{prefix}MAE}}{{{r['count_absolute_error_mean']:.2f}}}")
        macros.append(f"\\newcommand{{\\{prefix}Time}}{{{r['runtime_s_mean']:.4f}}}")
        final.append(
            {
                "method": method,
                "n_test": int(r["n_test"]),
                **{
                    f"ap_iou_{int(t * 100):03}_mean": lookup[method, t]["accuracy_mean"]
                    for t in (0.5, 0.75, 0.9)
                },
                "pq_iou_050_mean": r["panoptic_quality_mean"],
                "foreground_dice_mean": r["foreground_dice_mean"],
                "count_mae_mean": r["count_absolute_error_mean"],
                "runtime_s_mean": r["runtime_s_mean"],
                "hardware": "CPU; see benchmark provenance",
                "notes": "n=50; warm preprocessing+inference+postprocessing; no I/O",
            }
        )
    for name, rows in (
        ("benchmark_rows.tex", main_rows),
        ("secondary_rows.tex", secondary),
        ("metrics.tex", macros),
    ):
        (OUT / name).write_text("\n".join(rows) + "\n", encoding="utf-8")
    cross_rows = [
        f"{r['tag']} & {int(r['python_objects'])} & {int(r['fiji_objects'])} & "
        f"{r['f1_iou_050']:.4f} & {r['mean_matched_iou']:.4f} & "
        f"{r['foreground_dice']:.4f}\\\\"
        for r in cross
    ]
    (OUT / "cross_rows.tex").write_text("\n".join(cross_rows) + "\n", encoding="utf-8")
    # Expand rows as macros inside alignments; LaTeX's protected \input adds a token there.
    with (OUT / "metrics.tex").open("a", encoding="utf-8") as stream:
        for name, rows in (
            ("BenchmarkRows", main_rows),
            ("SecondaryRows", secondary),
            ("CrossRows", cross_rows),
        ):
            stream.write("\\newcommand{\\" + name + "}{%\n" + "\n".join(rows) + "\n}\n")
    (OUT / "slide_data.json").write_text(
        json.dumps(
            {
                "summary": summary,
                "fiji": fiji,
                "cross": cross,
                "ablation": ablation,
                "watershed": watershed,
            },
            indent=2,
        )
        + "\n"
    )
    write_csv(ROOT / "results/tables/final_metrics_template.csv", final)


if __name__ == "__main__":
    main()
