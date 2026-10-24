"""Fail if committed experiment tables, labels and submission artifacts disagree."""

from __future__ import annotations

import csv
import statistics
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import numpy as np
from tifffile import imread

from xla_gr03.experiments import sha256

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> list[dict]:
    with (ROOT / path).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    rows = read("results/dsb2018_benchmark/per_image_metrics.csv")
    assert len(rows) == 450 and len({r["image"] for r in rows}) == 50
    assert len({(r["image"], r["method"], r["threshold"]) for r in rows}) == 450
    for summary in read("results/dsb2018_benchmark/summary_metrics.csv"):
        group = [
            r
            for r in rows
            if r["method"] == summary["method"] and r["threshold"] == summary["threshold"]
        ]
        assert len(group) == int(summary["n_test"]) == 50
        for name in (
            "accuracy",
            "panoptic_quality",
            "foreground_dice",
            "count_absolute_error",
            "runtime_s",
        ):
            numbers = [float(r[name]) for r in group]
            assert abs(statistics.mean(numbers) - float(summary[name + "_mean"])) < 1e-10
            assert abs(statistics.stdev(numbers) - float(summary[name + "_sd"])) < 1e-10
    manifest = read("results/dsb2018_benchmark/dataset_manifest.csv")
    assert len(manifest) == 497
    for row in manifest:
        base = ROOT / "data/dsb2018/dsb2018" / row["split"]
        assert sha256(base / "images" / row["image"]) == row["image_sha256"]
        assert sha256(base / "masks" / row["image"]) == row["mask_sha256"]
    validation = {r["image"] for r in read("results/dsb2018_benchmark/validation_images.csv")}
    test = {r["image"] for r in rows}
    sweep = read("results/validation_ablation/per_image_metrics.csv")
    assert len(validation) == 30 and not validation & test
    assert len(sweep) == 300 and {r["image"] for r in sweep} == validation
    for case in read("results/cross_platform/comparison.csv"):
        python_path = ROOT / f"results/dsb2018_benchmark/selected_labels/{case['tag']}"
        assert sha256(python_path / "stardist_python.tif") == case["python_sha256"]
        assert sha256(ROOT / "results/fiji_labels" / case["image"]) == case["fiji_sha256"]
        np.testing.assert_array_equal(
            imread(ROOT / "results/fiji_rerun" / case["image"]),
            imread(ROOT / "results/fiji_labels" / case["image"]),
        )
    assert (ROOT / "report/report.pdf").read_bytes().startswith(b"%PDF-")
    beamer = ROOT / "slides/latex"
    pdf = (beamer / "main.pdf").read_bytes()
    assert pdf.startswith(b"%PDF-")
    assert (beamer / "main.tex").read_text().count(r"\begin{frame}") == 27
    assert (beamer / "generated/metrics.tex").is_file()
    with zipfile.ZipFile(ROOT / "slides/stardist_beamer_source.zip") as archive:
        for path in beamer.rglob("*"):
            if path.is_file() and path.suffix in {".tex", ".dat", ".png", ".jpg", ".json", ".md"}:
                assert archive.read(path.relative_to(beamer).as_posix()) == path.read_bytes()
    with zipfile.ZipFile(ROOT / "slides/stardist_presentation_completed.pptx") as archive:
        xml = ElementTree.fromstring(archive.read("ppt/presentation.xml"))
        namespace = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
        assert len(xml.findall("p:sldIdLst/p:sldId", namespace)) == 27
    print(
        "Verified: 450 benchmark rows, 497 hashed pairs, 300 validation rows, "
        "3 Fiji reproductions, report PDF, 27-slide Beamer/source ZIP and optional PPTX."
    )


if __name__ == "__main__":
    main()
