import numpy as np

from xla_gr03.baselines import segment_otsu, segment_watershed


def test_otsu_finds_two_disconnected_bright_objects() -> None:
    image = np.zeros((64, 64), dtype=np.float32)
    image[8:20, 8:20] = 1.0
    image[40:54, 42:57] = 1.0

    result = segment_otsu(image, gaussian_sigma=0, min_size=1, closing_radius=0)

    assert result.object_count == 2
    assert result.labels.dtype == np.int32


def test_watershed_splits_touching_round_objects() -> None:
    yy, xx = np.mgrid[:80, :80]
    image = (((yy - 40) ** 2 + (xx - 30) ** 2 <= 16**2) | (
        (yy - 40) ** 2 + (xx - 50) ** 2 <= 16**2
    )).astype(np.float32)

    result = segment_watershed(
        image,
        gaussian_sigma=0,
        min_size=1,
        closing_radius=0,
        min_distance=10,
    )

    assert result.object_count == 2
