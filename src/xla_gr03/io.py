"""Input/output helpers with label-safe TIFF handling."""

from __future__ import annotations

from pathlib import Path

import imageio.v3 as iio
import numpy as np
import tifffile
from numpy.typing import NDArray


def read_image(path: str | Path) -> NDArray[np.generic]:
    """Read a TIFF or common image file into a NumPy array."""

    image_path = Path(path)
    if not image_path.is_file():
        raise FileNotFoundError(f"Image does not exist: {image_path}")
    if image_path.suffix.lower() in {".tif", ".tiff"}:
        return np.asarray(tifffile.imread(image_path))
    return np.asarray(iio.imread(image_path))


def save_labels(path: str | Path, labels: NDArray[np.integer]) -> Path:
    """Save a 2D non-negative instance label image without losing label IDs."""

    label_array = np.asarray(labels)
    if label_array.ndim != 2 or not np.issubdtype(label_array.dtype, np.integer):
        raise ValueError("Labels must be a 2D integer array.")
    if np.any(label_array < 0):
        raise ValueError("Labels must be non-negative.")

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dtype = np.uint16 if int(label_array.max(initial=0)) <= np.iinfo(np.uint16).max else np.uint32
    tifffile.imwrite(output_path, label_array.astype(dtype, copy=False), photometric="minisblack")
    return output_path
