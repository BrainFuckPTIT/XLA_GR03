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


@pytest.mark.parametrize("merge", [False, True])
def test_split_and_merge_require_one_to_one_matching(merge):
    whole = np.ones((4, 4), dtype=np.int32)
    halves = whole.copy()
    halves[:, 2:] = 2
    true, pred = (halves, whole) if merge else (whole, halves)
    metric = evaluate_instances(true, pred, 0.5)
    assert metric.true_positives == 1
    assert metric.false_negatives == int(merge)
    assert metric.false_positives == int(not merge)
    assert evaluate_instances(true, pred, 0.50001).true_positives == 0


def test_assignment_prioritizes_valid_pairs_over_total_iou(monkeypatch):
    # Diagonal IoU has larger sum but only one accepted match. Off-diagonal has two.
    monkeypatch.setattr(
        "xla_gr03.metrics.intersection_over_union_matrix",
        lambda *_: np.array([[0.99, 0.5], [0.5, 0.49]]),
    )
    metric = evaluate_instances(_two_objects(), _two_objects(), 0.5)
    assert metric.true_positives == 2
    assert metric.mean_matched_iou == 0.5


def test_zero_iou_threshold_does_not_match_disjoint_objects():
    with pytest.raises(ValueError, match="threshold"):
        evaluate_instances(_two_objects(), _two_objects(), 0)
