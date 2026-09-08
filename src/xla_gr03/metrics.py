"""Quantitative metrics for 2D instance segmentation."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.optimize import linear_sum_assignment


@dataclass(frozen=True)
class InstanceMetrics:
    """Detection and segmentation statistics at one IoU threshold."""

    threshold: float
    true_objects: int
    predicted_objects: int
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1: float
    accuracy: float
    mean_matched_iou: float
    panoptic_quality: float
    foreground_dice: float
    foreground_iou: float
    count_absolute_error: int

    def to_dict(self) -> dict[str, float | int]:
        """Return a JSON-serializable representation."""

        return asdict(self)


def _validate_label_pair(
    ground_truth: ArrayLike,
    prediction: ArrayLike,
) -> tuple[NDArray[np.integer], NDArray[np.integer]]:
    true = np.asarray(ground_truth)
    pred = np.asarray(prediction)
    if true.shape != pred.shape or true.ndim != 2:
        raise ValueError("Ground truth and prediction must be 2D arrays with identical shape.")
    for name, array in (("ground truth", true), ("prediction", pred)):
        if not np.issubdtype(array.dtype, np.integer) or np.any(array < 0):
            raise ValueError(f"{name} must contain non-negative integer labels.")
    return true, pred


def relabel_sequential(labels: ArrayLike) -> NDArray[np.int32]:
    """Map arbitrary positive label IDs to the sequence 1..N."""

    array = np.asarray(labels)
    output = np.zeros(array.shape, dtype=np.int32)
    for new_id, old_id in enumerate(np.unique(array[array > 0]), start=1):
        output[array == old_id] = new_id
    return output


def intersection_over_union_matrix(
    ground_truth: ArrayLike,
    prediction: ArrayLike,
) -> NDArray[np.float64]:
    """Return pairwise IoU for all positive ground-truth/prediction instances."""

    true, pred = _validate_label_pair(ground_truth, prediction)
    true = relabel_sequential(true)
    pred = relabel_sequential(pred)
    n_true = int(true.max(initial=0))
    n_pred = int(pred.max(initial=0))
    if n_true == 0 or n_pred == 0:
        return np.zeros((n_true, n_pred), dtype=np.float64)

    flat_true = true.ravel()
    flat_pred = pred.ravel()
    overlap = np.zeros((n_true + 1, n_pred + 1), dtype=np.int64)
    np.add.at(overlap, (flat_true, flat_pred), 1)
    intersection = overlap[1:, 1:].astype(np.float64)
    true_area = overlap[1:, :].sum(axis=1, keepdims=True)
    pred_area = overlap[:, 1:].sum(axis=0, keepdims=True)
    union = true_area + pred_area - intersection
    return np.divide(intersection, union, out=np.zeros_like(intersection), where=union > 0)


def _safe_ratio(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def evaluate_instances(
    ground_truth: ArrayLike,
    prediction: ArrayLike,
    threshold: float = 0.5,
) -> InstanceMetrics:
    """Evaluate a prediction using one-to-one IoU matching.

    The assignment maximizes the number of pairs at or above ``threshold`` and
    uses IoU as a tie-breaker, following the StarDist matching implementation.
    """

    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be in [0, 1].")
    true, pred = _validate_label_pair(ground_truth, prediction)
    iou = intersection_over_union_matrix(true, pred)
    n_true, n_pred = iou.shape
    matched_ious = np.array([], dtype=np.float64)

    if n_true and n_pred:
        n_possible = min(n_true, n_pred)
        cost = -(iou >= threshold).astype(np.float64) - iou / (2.0 * n_possible)
        true_indices, pred_indices = linear_sum_assignment(cost)
        assigned_ious = iou[true_indices, pred_indices]
        matched_ious = assigned_ious[assigned_ious >= threshold]

    true_positives = int(matched_ious.size)
    false_positives = n_pred - true_positives
    false_negatives = n_true - true_positives
    precision = _safe_ratio(true_positives, true_positives + false_positives)
    recall = _safe_ratio(true_positives, true_positives + false_negatives)
    f1 = _safe_ratio(2 * true_positives, 2 * true_positives + false_positives + false_negatives)
    accuracy = _safe_ratio(
        true_positives, true_positives + false_positives + false_negatives
    )
    mean_matched_iou = float(matched_ious.mean()) if true_positives else 0.0
    pq_denominator = true_positives + 0.5 * false_positives + 0.5 * false_negatives
    panoptic_quality = _safe_ratio(float(matched_ious.sum()), pq_denominator)

    true_foreground = true > 0
    pred_foreground = pred > 0
    intersection = int(np.logical_and(true_foreground, pred_foreground).sum())
    true_area = int(true_foreground.sum())
    pred_area = int(pred_foreground.sum())
    foreground_dice = _safe_ratio(2 * intersection, true_area + pred_area)
    foreground_iou = _safe_ratio(intersection, true_area + pred_area - intersection)

    return InstanceMetrics(
        threshold=float(threshold),
        true_objects=n_true,
        predicted_objects=n_pred,
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
        precision=precision,
        recall=recall,
        f1=f1,
        accuracy=accuracy,
        mean_matched_iou=mean_matched_iou,
        panoptic_quality=panoptic_quality,
        foreground_dice=foreground_dice,
        foreground_iou=foreground_iou,
        count_absolute_error=abs(n_pred - n_true),
    )


def evaluate_at_thresholds(
    ground_truth: ArrayLike,
    prediction: ArrayLike,
    thresholds: list[float] | tuple[float, ...],
) -> list[InstanceMetrics]:
    """Evaluate the same label pair at multiple IoU thresholds."""

    if not thresholds:
        raise ValueError("At least one threshold is required.")
    return [evaluate_instances(ground_truth, prediction, value) for value in thresholds]
