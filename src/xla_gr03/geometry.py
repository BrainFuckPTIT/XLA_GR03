"""Reference implementations of StarDist geometric building blocks.

These functions prioritize readability and verifiability over raw speed. They are
intended for coursework demonstrations and unit tests, not full model training.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy import ndimage as ndi
from skimage.draw import polygon as rasterize_polygon


def _validate_labels(labels: ArrayLike) -> NDArray[np.integer]:
    array = np.asarray(labels)
    if array.ndim != 2 or not np.issubdtype(array.dtype, np.integer):
        raise ValueError("Instance labels must be a 2D integer array.")
    if np.any(array < 0):
        raise ValueError("Instance labels must be non-negative.")
    return array


def normalized_edt(labels: ArrayLike) -> NDArray[np.float32]:
    """Compute an Euclidean distance target normalized per object instance.

    Background is zero. Every positive object is transformed independently and
    divided by its own maximum, matching the definition used by StarDist.
    """

    label_array = _validate_labels(labels)
    probability = np.zeros(label_array.shape, dtype=np.float32)
    for object_id in np.unique(label_array):
        if object_id == 0:
            continue
        mask = label_array == object_id
        padded = np.pad(mask, 1, mode="constant", constant_values=False)
        distance = ndi.distance_transform_edt(padded)[1:-1, 1:-1]
        maximum = float(distance[mask].max(initial=0.0))
        if maximum > 0:
            probability[mask] = distance[mask] / maximum
    return probability


def ray_angles(n_rays: int) -> NDArray[np.float64]:
    """Return ``n_rays`` equally spaced angles in ``[0, 2*pi)``."""

    if n_rays < 3:
        raise ValueError("n_rays must be at least 3.")
    return np.linspace(0.0, 2.0 * np.pi, n_rays, endpoint=False)


def star_distances(
    labels: ArrayLike,
    n_rays: int = 32,
    step: float = 1.0,
) -> NDArray[np.float32]:
    """Estimate radial distances from every foreground pixel to its boundary.

    The implementation walks along equally spaced rays until the nearest sampled
    pixel no longer has the same instance ID. It is intentionally simple and slow,
    so use small masks to explain or validate the StarDist target representation.
    """

    label_array = _validate_labels(labels)
    if step <= 0:
        raise ValueError("step must be positive.")

    height, width = label_array.shape
    max_distance = float(np.hypot(height, width) + step)
    angles = ray_angles(n_rays)
    directions = np.column_stack((np.sin(angles), np.cos(angles)))
    distances = np.zeros((height, width, n_rays), dtype=np.float32)

    for y0, x0 in np.argwhere(label_array > 0):
        object_id = label_array[y0, x0]
        for ray_index, (dy, dx) in enumerate(directions):
            distance = step
            while distance <= max_distance:
                y = int(np.rint(y0 + distance * dy))
                x = int(np.rint(x0 + distance * dx))
                if y < 0 or y >= height or x < 0 or x >= width:
                    break
                if label_array[y, x] != object_id:
                    break
                distance += step
            distances[y0, x0, ray_index] = distance
    return distances


def decode_polygon(
    center_yx: Sequence[float],
    distances: ArrayLike,
) -> NDArray[np.float64]:
    """Decode radial distances into polygon vertices in ``(x, y)`` order."""

    center = np.asarray(center_yx, dtype=np.float64)
    radii = np.asarray(distances, dtype=np.float64)
    if center.shape != (2,) or radii.ndim != 1 or radii.size < 3:
        raise ValueError("Expected center_yx=(y, x) and a 1D vector with at least 3 radii.")
    if np.any(radii < 0):
        raise ValueError("Polygon radii must be non-negative.")

    y0, x0 = center
    angles = ray_angles(radii.size)
    x = x0 + radii * np.cos(angles)
    y = y0 + radii * np.sin(angles)
    return np.column_stack((x, y))


def polygon_area(polygon_xy: ArrayLike) -> float:
    """Calculate polygon area with the shoelace formula."""

    polygon = np.asarray(polygon_xy, dtype=np.float64)
    if polygon.ndim != 2 or polygon.shape[1] != 2 or polygon.shape[0] < 3:
        raise ValueError("A polygon must have shape (N, 2) with N >= 3.")
    x, y = polygon[:, 0], polygon[:, 1]
    return float(0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def polygon_overlap_ratio(
    polygon_a_xy: ArrayLike,
    polygon_b_xy: ArrayLike,
    mode: str = "smaller",
) -> float:
    """Estimate polygon overlap after rasterization on a shared local canvas.

    ``mode='smaller'`` returns intersection divided by the smaller polygon area,
    which mirrors StarDist 2D NMS. ``mode='iou'`` returns the standard IoU.
    """

    polygon_a = np.asarray(polygon_a_xy, dtype=np.float64)
    polygon_b = np.asarray(polygon_b_xy, dtype=np.float64)
    if mode not in {"smaller", "iou"}:
        raise ValueError("mode must be either 'smaller' or 'iou'.")
    for polygon in (polygon_a, polygon_b):
        if polygon.ndim != 2 or polygon.shape[1] != 2 or polygon.shape[0] < 3:
            raise ValueError("Every polygon must have shape (N, 2) with N >= 3.")

    all_points = np.vstack((polygon_a, polygon_b))
    min_x, min_y = np.floor(all_points.min(axis=0)).astype(int) - 1
    max_x, max_y = np.ceil(all_points.max(axis=0)).astype(int) + 1
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    if width <= 0 or height <= 0:
        return 0.0

    masks: list[NDArray[np.bool_]] = []
    for polygon in (polygon_a, polygon_b):
        shifted_x = polygon[:, 0] - min_x
        shifted_y = polygon[:, 1] - min_y
        rows, cols = rasterize_polygon(shifted_y, shifted_x, shape=(height, width))
        mask = np.zeros((height, width), dtype=bool)
        mask[rows, cols] = True
        masks.append(mask)

    area_a = int(masks[0].sum())
    area_b = int(masks[1].sum())
    intersection = int(np.logical_and(masks[0], masks[1]).sum())
    if mode == "smaller":
        denominator = min(area_a, area_b)
    else:
        denominator = area_a + area_b - intersection
    return intersection / denominator if denominator else 0.0


def greedy_polygon_nms(
    polygons_xy: Sequence[ArrayLike],
    scores: ArrayLike,
    threshold: float = 0.3,
    overlap_mode: str = "smaller",
) -> NDArray[np.int64]:
    """Return indices retained by score-sorted greedy polygon NMS."""

    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be in [0, 1].")
    score_array = np.asarray(scores, dtype=np.float64)
    if score_array.ndim != 1 or score_array.size != len(polygons_xy):
        raise ValueError("scores must contain one value for every polygon.")

    order = np.argsort(-score_array, kind="stable")
    kept: list[int] = []
    for candidate in order:
        if all(
            polygon_overlap_ratio(
                polygons_xy[int(candidate)], polygons_xy[selected], mode=overlap_mode
            )
            <= threshold
            for selected in kept
        ):
            kept.append(int(candidate))
    return np.asarray(kept, dtype=np.int64)
