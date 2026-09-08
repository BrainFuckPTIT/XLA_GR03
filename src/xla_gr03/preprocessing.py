"""Image conversion and normalization shared by all pipelines."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray


def to_grayscale(image: ArrayLike) -> NDArray[np.float32]:
    """Convert a 2D grayscale or RGB/RGBA image to float32 grayscale.

    RGB conversion uses ITU-R BT.709 luminance coefficients. Alpha, if present,
    is ignored because microscopy alpha channels normally carry no image signal.
    """

    array = np.asarray(image)
    if array.ndim == 2:
        return array.astype(np.float32, copy=False)
    if array.ndim == 3 and array.shape[-1] in (3, 4):
        rgb = array[..., :3].astype(np.float32, copy=False)
        return np.tensordot(rgb, np.array([0.2126, 0.7152, 0.0722], np.float32), axes=1)
    raise ValueError("Expected a 2D grayscale image or a YXC RGB/RGBA image.")


def percentile_normalize(
    image: ArrayLike,
    pmin: float = 1.0,
    pmax: float = 99.8,
    axes: Sequence[int] | None = None,
    clip: bool = True,
) -> NDArray[np.float32]:
    """Normalize an image using robust percentiles.

    By default all axes are normalized jointly. For a YXC RGB image, pass
    ``axes=(0, 1)`` to normalize every channel independently, matching the usual
    StarDist/CSBDeep convention.
    """

    if not 0 <= pmin < pmax <= 100:
        raise ValueError("Require 0 <= pmin < pmax <= 100.")

    array = np.asarray(image, dtype=np.float32)
    reduce_axes = tuple(range(array.ndim)) if axes is None else tuple(axes)
    low = np.percentile(array, pmin, axis=reduce_axes, keepdims=True)
    high = np.percentile(array, pmax, axis=reduce_axes, keepdims=True)
    normalized = (array - low) / np.maximum(high - low, np.finfo(np.float32).eps)
    if clip:
        normalized = np.clip(normalized, 0.0, 1.0)
    return normalized.astype(np.float32, copy=False)
