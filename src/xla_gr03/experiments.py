"""Shared file pairing, CSV and provenance for the experiment entry points."""

from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import platform
import subprocess
import sys
from pathlib import Path

import numpy as np
from tifffile import imread


def paired_images(images: Path, masks: Path) -> list[tuple[Path, Path]]:
    paths = sorted(p for p in images.glob("*") if p.suffix.lower() in {".tif", ".tiff"})
    if not paths:
        raise ValueError(f"No TIFF images found in {images}")
    missing = [p.name for p in paths if not (masks / p.name).is_file()]
    if missing:
        raise ValueError(f"Missing {len(missing)} ground-truth masks: {', '.join(missing)}")
    return [(p, masks / p.name) for p in paths]


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"Cannot write an empty experiment table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dataset_manifest(pairs: list[tuple[Path, Path]], split: str) -> list[dict]:
    rows = []
    for image_path, mask_path in pairs:
        image, mask = imread(image_path), imread(mask_path)
        if image.shape != mask.shape or mask.ndim != 2:
            raise ValueError(f"Expected matching 2D image/mask: {image_path.name}")
        if not np.issubdtype(mask.dtype, np.integer) or np.any(mask < 0):
            raise ValueError(f"Invalid instance mask: {mask_path}")
        rows.append(
            {
                "image": image_path.name,
                "split": split,
                "height": image.shape[0],
                "width": image.shape[1],
                "image_dtype": str(image.dtype),
                "mask_dtype": str(mask.dtype),
                "image_sha256": sha256(image_path),
                "mask_sha256": sha256(mask_path),
            }
        )
    return rows


def runtime_provenance(model=None) -> dict:
    packages = {}
    for name in (
        "numpy",
        "scipy",
        "scikit-image",
        "tifffile",
        "tensorflow",
        "stardist",
        "csbdeep",
        "keras",
        "matplotlib",
    ):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    cpu = platform.processor()
    if sys.platform == "darwin":
        cpu = subprocess.check_output(
            ["sysctl", "-n", "machdep.cpu.brand_string"], text=True
        ).strip()
    result = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu": cpu,
        "packages": packages,
    }
    if model is not None:
        import tensorflow as tf

        result["tensorflow_devices"] = [d.name for d in tf.config.get_visible_devices()]
        result["model_files_sha256"] = {
            p.name: sha256(p)
            for p in sorted(Path(model.logdir).glob("*"))
            if p.is_file() and p.suffix in {".h5", ".json"}
        }
    return result
