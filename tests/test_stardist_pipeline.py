import sys
import types

import numpy as np
import pytest

from xla_gr03.stardist_pipeline import _load_model, segment_stardist


class _Thresholds:
    prob = 0.41
    nms = 0.27


class _FakeModel:
    thresholds = _Thresholds()

    def predict_instances(self, image, **kwargs):
        assert image.shape == (8, 8)
        assert kwargs["axes"] == "YX"
        labels = np.zeros((8, 8), dtype=np.int32)
        labels[2:6, 2:6] = 1
        return labels, {"points": np.array([[4, 4]])}


def test_segment_stardist_records_effective_default_thresholds(monkeypatch) -> None:
    monkeypatch.setattr("xla_gr03.stardist_pipeline._load_model", lambda *_: _FakeModel())

    result = segment_stardist(np.arange(64, dtype=np.float32).reshape(8, 8))

    assert result.method == "stardist"
    assert result.object_count == 1
    assert result.metadata["prob_thresh"] == 0.41
    assert result.metadata["nms_thresh"] == 0.27
    assert result.metadata["candidate_details"] == ["points"]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"prob_thresh": -0.01}, "prob_thresh"),
        ({"nms_thresh": 1.01}, "nms_thresh"),
        ({"n_tiles": (1,)}, "n_tiles"),
    ],
)
def test_segment_stardist_validates_options_before_model_load(kwargs, message) -> None:
    with pytest.raises(ValueError, match=message):
        segment_stardist(np.zeros((8, 8), dtype=np.float32), **kwargs)


def test_segment_stardist_rejects_non_image_shape() -> None:
    with pytest.raises(ValueError, match="YX or YXC"):
        segment_stardist(np.zeros((2, 8, 8), dtype=np.float32))


def test_load_model_pretrained_and_custom_directory(monkeypatch, tmp_path) -> None:
    calls: list[tuple[object, ...]] = []

    class FakeStarDist2D:
        @staticmethod
        def from_pretrained(name):
            calls.append(("pretrained", name))
            return "pretrained-model"

        def __init__(self, *, config, name, basedir):
            calls.append(("custom", config, name, basedir))

    fake_models = types.ModuleType("stardist.models")
    fake_models.StarDist2D = FakeStarDist2D
    monkeypatch.setitem(sys.modules, "stardist.models", fake_models)

    assert _load_model("2D_versatile_fluo", None) == "pretrained-model"
    custom = tmp_path / "custom-model"
    custom.mkdir()
    (custom / "config.json").write_text("{}", encoding="utf-8")
    _load_model("ignored-for-custom-model", custom)

    assert calls[0] == ("pretrained", "2D_versatile_fluo")
    assert calls[1] == ("custom", None, "custom-model", custom.parent)


def test_load_model_rejects_unknown_pretrained_name() -> None:
    with pytest.raises(ValueError, match="Unknown pretrained model"):
        _load_model("not-a-stardist-model", None)
