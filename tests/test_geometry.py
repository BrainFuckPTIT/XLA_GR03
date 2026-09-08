import numpy as np
import pytest

from xla_gr03.geometry import (
    decode_polygon,
    greedy_polygon_nms,
    normalized_edt,
    polygon_area,
    polygon_overlap_ratio,
    star_distances,
)


def test_normalized_edt_is_normalized_per_instance() -> None:
    labels = np.zeros((9, 12), dtype=np.int32)
    labels[1:4, 1:4] = 1
    labels[2:8, 6:11] = 2

    probability = normalized_edt(labels)

    assert np.all(probability[labels == 0] == 0)
    assert probability[labels == 1].max() == pytest.approx(1.0)
    assert probability[labels == 2].max() == pytest.approx(1.0)
    assert np.all(probability[labels > 0] > 0)


def test_cardinal_star_distances_for_square_center() -> None:
    labels = np.zeros((9, 9), dtype=np.int32)
    labels[2:7, 2:7] = 1

    distances = star_distances(labels, n_rays=4)

    np.testing.assert_allclose(distances[4, 4], [3.0, 3.0, 3.0, 3.0])


def test_decode_polygon_and_shoelace_area() -> None:
    polygon = decode_polygon((5, 8), [2, 2, 2, 2])

    assert polygon.shape == (4, 2)
    assert polygon_area(polygon) == pytest.approx(8.0)


def test_polygon_overlap_and_nms() -> None:
    square_a = np.array([[0, 0], [4, 0], [4, 4], [0, 4]], dtype=float)
    square_b = square_a.copy()
    square_c = square_a + 10

    assert polygon_overlap_ratio(square_a, square_b) == pytest.approx(1.0)
    assert polygon_overlap_ratio(square_a, square_c) == pytest.approx(0.0)
    kept = greedy_polygon_nms([square_a, square_b, square_c], [0.9, 0.7, 0.6], threshold=0.3)
    np.testing.assert_array_equal(kept, [0, 2])
