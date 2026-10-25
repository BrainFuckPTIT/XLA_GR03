"""Real, opt-in model and reference checks. Run: pytest -m integration."""

from pathlib import Path

import numpy as np
import pytest

from xla_gr03.geometry import normalized_edt, star_distances
from xla_gr03.metrics import evaluate_instances
from xla_gr03.preprocessing import percentile_normalize
from xla_gr03.stardist_pipeline import segment_stardist

pytestmark = pytest.mark.integration


def test_real_model_inference_and_reference_metrics():
    from stardist.data import test_image_nuclei_2d
    from stardist.matching import matching

    image, truth = test_image_nuclei_2d(return_mask=True)
    # Use the distributed real microscopy image, rather than an arbitrary synthetic signal.
    image, truth = image[:128, :128], truth[:128, :128]
    result = segment_stardist(image)
    assert result.labels.shape == image.shape
    assert result.object_count > 0
    ours = evaluate_instances(truth, result.labels)
    official = matching(truth, result.labels, thresh=0.5)
    assert (ours.true_positives, ours.false_positives, ours.false_negatives) == (
        official.tp,
        official.fp,
        official.fn,
    )
    assert ours.panoptic_quality == pytest.approx(official.panoptic_quality)
    assert result.metadata["clip"] is False


def test_reference_normalization_and_geometry():
    from csbdeep.utils import normalize
    from stardist.geometry import star_dist
    from stardist.utils import edt_prob

    image = np.arange(100, dtype=np.float32).reshape(10, 10)
    np.testing.assert_allclose(
        percentile_normalize(image), normalize(image, 1, 99.8, axis=(0, 1), clip=False), atol=2e-7
    )
    labels = np.zeros((12, 13), np.uint16)
    labels[:5, :5] = 1
    labels[6:11, 7:12] = 2
    np.testing.assert_allclose(normalized_edt(labels), edt_prob(labels), atol=1e-6)
    ours, official = star_distances(labels, n_rays=8), star_dist(labels, n_rays=8)
    # Educational sampling reports the first outside sample, within two pixel steps.
    assert np.max(np.abs(ours - official)) <= 2


def test_official_matching_on_real_saved_labels():
    from stardist.matching import matching
    from tifffile import imread

    root = Path(__file__).resolve().parents[1]
    for tag in ("low", "median", "high"):
        base = root / f"results/dsb2018_benchmark/selected_labels/{tag}"
        truth = imread(base / "ground_truth.tif")
        for method in ("otsu", "watershed", "stardist_python"):
            pred = imread(base / f"{method}.tif")
            for threshold in (0.5, 0.75, 0.9):
                ours, ref = (
                    evaluate_instances(truth, pred, threshold),
                    matching(truth, pred, thresh=threshold),
                )
                assert ours.accuracy == pytest.approx(ref.accuracy)
                assert ours.panoptic_quality == pytest.approx(ref.panoptic_quality)
