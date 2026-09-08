import numpy as np
import pytest

from xla_gr03.preprocessing import percentile_normalize, to_grayscale


def test_rgb_to_grayscale_shape() -> None:
    rgb = np.zeros((4, 5, 3), dtype=np.uint8)
    rgb[..., 1] = 100

    gray = to_grayscale(rgb)

    assert gray.shape == (4, 5)
    assert gray.dtype == np.float32


def test_percentile_normalize_rejects_invalid_range() -> None:
    with pytest.raises(ValueError):
        percentile_normalize(np.zeros((2, 2)), pmin=99, pmax=1)


def test_percentile_normalize_constant_image_is_finite() -> None:
    normalized = percentile_normalize(np.ones((3, 3), dtype=np.float32))

    assert np.all(np.isfinite(normalized))
    assert np.all(normalized == 0)
