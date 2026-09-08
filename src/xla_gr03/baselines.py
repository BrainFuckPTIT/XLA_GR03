"""Classical instance-segmentation baselines: Otsu and Watershed."""

from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy import ndimage as ndi
from skimage import filters, measure, morphology, segmentation
from skimage.feature import peak_local_max

from .preprocessing import to_grayscale
from .result import SegmentationResult

ForegroundMode = Literal["bright", "dark"]


def _otsu_mask(
    image: ArrayLike,
    *,
    foreground: ForegroundMode,
    gaussian_sigma: float,
    min_size: int,
    closing_radius: int,
) -> tuple[NDArray[np.bool_], float]:
    gray = to_grayscale(image)
    if gaussian_sigma < 0:
        raise ValueError("gaussian_sigma must be non-negative.")
    if min_size < 0 or closing_radius < 0:
        raise ValueError("min_size and closing_radius must be non-negative.")
    if foreground not in {"bright", "dark"}:
        raise ValueError("foreground must be 'bright' or 'dark'.")

    filtered = filters.gaussian(gray, sigma=gaussian_sigma, preserve_range=True)
    threshold = float(filters.threshold_otsu(filtered))
    mask = filtered > threshold if foreground == "bright" else filtered < threshold
    if closing_radius:
        mask = morphology.binary_closing(mask, morphology.disk(closing_radius))
    if min_size:
        try:
            # scikit-image >= 0.26 renamed the threshold and changed it to inclusive.
            mask = morphology.remove_small_objects(mask, max_size=min_size - 1)
        except TypeError:
            # Compatibility with scikit-image 0.22--0.25.
            mask = morphology.remove_small_objects(mask, min_size=min_size)
    mask = ndi.binary_fill_holes(mask)
    return np.asarray(mask, dtype=bool), threshold


def segment_otsu(
    image: ArrayLike,
    *,
    foreground: ForegroundMode = "bright",
    gaussian_sigma: float = 1.0,
    min_size: int = 20,
    closing_radius: int = 1,
) -> SegmentationResult:
    """Segment foreground with global Otsu and label connected components."""

    mask, threshold = _otsu_mask(
        image,
        foreground=foreground,
        gaussian_sigma=gaussian_sigma,
        min_size=min_size,
        closing_radius=closing_radius,
    )
    labels = measure.label(mask, connectivity=1).astype(np.int32, copy=False)
    return SegmentationResult(
        labels=labels,
        method="otsu",
        metadata={
            "threshold": threshold,
            "foreground": foreground,
            "gaussian_sigma": gaussian_sigma,
            "min_size": min_size,
            "closing_radius": closing_radius,
        },
    )


def segment_watershed(
    image: ArrayLike,
    *,
    foreground: ForegroundMode = "bright",
    gaussian_sigma: float = 1.0,
    min_size: int = 20,
    closing_radius: int = 1,
    min_distance: int = 5,
    watershed_line: bool = False,
) -> SegmentationResult:
    """Run marker-controlled Watershed on the Otsu foreground distance map."""

    if min_distance < 1:
        raise ValueError("min_distance must be at least 1.")
    mask, threshold = _otsu_mask(
        image,
        foreground=foreground,
        gaussian_sigma=gaussian_sigma,
        min_size=min_size,
        closing_radius=closing_radius,
    )
    distance = ndi.distance_transform_edt(mask)
    coordinates = peak_local_max(
        distance,
        labels=mask,
        min_distance=min_distance,
        exclude_border=False,
    )
    marker_mask = np.zeros(mask.shape, dtype=bool)
    if coordinates.size:
        marker_mask[tuple(coordinates.T)] = True
    markers = measure.label(marker_mask, connectivity=1)
    if not markers.max(initial=0) and np.any(mask):
        markers = measure.label(mask, connectivity=1)
    labels = segmentation.watershed(
        -distance,
        markers=markers,
        mask=mask,
        watershed_line=watershed_line,
    ).astype(np.int32, copy=False)
    return SegmentationResult(
        labels=labels,
        method="watershed",
        metadata={
            "threshold": threshold,
            "foreground": foreground,
            "gaussian_sigma": gaussian_sigma,
            "min_size": min_size,
            "closing_radius": closing_radius,
            "min_distance": min_distance,
            "marker_count": int(markers.max(initial=0)),
            "watershed_line": watershed_line,
        },
    )
