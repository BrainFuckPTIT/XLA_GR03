import numpy as np
import pytest

from xla_gr03.metrics import evaluate_instances, intersection_over_union_matrix


def _two_objects() -> np.ndarray:
    labels = np.zeros((12, 12), dtype=np.int32)
    labels[1:4, 1:4] = 4
    labels[7:11, 7:10] = 9
    return labels


def test_iou_matrix_relabels_arbitrary_ids() -> None:
    labels = _two_objects()
    matrix = intersection_over_union_matrix(labels, labels)

    np.testing.assert_allclose(matrix, np.eye(2))


def test_identical_instances_have_perfect_metrics() -> None:
    labels = _two_objects()
    metrics = evaluate_instances(labels, labels, threshold=0.5)

    assert metrics.true_positives == 2
    assert metrics.false_positives == 0
    assert metrics.false_negatives == 0
    assert metrics.f1 == pytest.approx(1.0)
    assert metrics.accuracy == pytest.approx(1.0)
    assert metrics.panoptic_quality == pytest.approx(1.0)
    assert metrics.foreground_dice == pytest.approx(1.0)


def test_extra_prediction_is_false_positive() -> None:
    true = _two_objects()
    pred = true.copy()
    pred[5, 5] = 20

    metrics = evaluate_instances(true, pred, threshold=0.5)

    assert metrics.true_positives == 2
    assert metrics.false_positives == 1
    assert metrics.false_negatives == 0
    assert metrics.precision == pytest.approx(2 / 3)
    assert metrics.count_absolute_error == 1


def test_empty_pair_is_well_defined() -> None:
    empty = np.zeros((5, 5), dtype=np.int32)
    metrics = evaluate_instances(empty, empty)

    assert metrics.true_objects == 0
    assert metrics.predicted_objects == 0
    assert metrics.panoptic_quality == 0.0
