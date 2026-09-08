"""Thin, explicit wrapper around the official StarDist 2D inference API."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from numpy.typing import ArrayLike

from .preprocessing import percentile_normalize
from .result import SegmentationResult

PRETRAINED_MODELS = {
    "2D_versatile_fluo",
    "2D_versatile_he",
    "2D_paper_dsb2018",
}


def _load_model(model_name: str, custom_model_dir: str | Path | None):
    try:
        from stardist.models import StarDist2D
    except ImportError as error:
        raise RuntimeError(
            "StarDist is not installed. Run: python -m pip install -e \".[stardist]\""
        ) from error

    if custom_model_dir is None:
        if model_name not in PRETRAINED_MODELS:
            supported = ", ".join(sorted(PRETRAINED_MODELS))
            raise ValueError(f"Unknown pretrained model '{model_name}'. Choose one of: {supported}")
        return StarDist2D.from_pretrained(model_name)

    model_path = Path(custom_model_dir).resolve()
    config_path = model_path / "config.json"
    if not config_path.is_file():
        raise FileNotFoundError(f"Custom model is missing config.json: {model_path}")
    return StarDist2D(config=None, name=model_path.name, basedir=model_path.parent)


def segment_stardist(
    image: ArrayLike,
    *,
    model_name: str = "2D_versatile_fluo",
    custom_model_dir: str | Path | None = None,
    pmin: float = 1.0,
    pmax: float = 99.8,
    prob_thresh: float | None = None,
    nms_thresh: float | None = None,
    n_tiles: tuple[int, int] | None = None,
) -> SegmentationResult:
    """Normalize an image and perform StarDist 2D instance segmentation."""

    array = np.asarray(image)
    if array.ndim == 2:
        axes = "YX"
        normalization_axes = (0, 1)
    elif array.ndim == 3 and array.shape[-1] in (1, 3):
        axes = "YXC"
        normalization_axes = (0, 1)
    else:
        raise ValueError("StarDist 2D expects a YX or YXC image.")
    if prob_thresh is not None and not 0 <= prob_thresh <= 1:
        raise ValueError("prob_thresh must be in [0, 1].")
    if nms_thresh is not None and not 0 <= nms_thresh <= 1:
        raise ValueError("nms_thresh must be in [0, 1].")
    if n_tiles is not None and (len(n_tiles) != 2 or any(value < 1 for value in n_tiles)):
        raise ValueError("n_tiles must contain two positive integers.")

    model = _load_model(model_name, custom_model_dir)
    normalized = percentile_normalize(
        array,
        pmin=pmin,
        pmax=pmax,
        axes=normalization_axes,
    )
    predict_options: dict[str, object] = {"axes": axes}
    if prob_thresh is not None:
        predict_options["prob_thresh"] = prob_thresh
    if nms_thresh is not None:
        predict_options["nms_thresh"] = nms_thresh
    if n_tiles is not None:
        predict_options["n_tiles"] = n_tiles

    labels, details = model.predict_instances(normalized, **predict_options)
    effective_prob = prob_thresh if prob_thresh is not None else float(model.thresholds.prob)
    effective_nms = nms_thresh if nms_thresh is not None else float(model.thresholds.nms)
    metadata = {
        "model": str(Path(custom_model_dir).resolve()) if custom_model_dir else model_name,
        "pmin": pmin,
        "pmax": pmax,
        "prob_thresh": effective_prob,
        "nms_thresh": effective_nms,
        "n_tiles": n_tiles,
        "candidate_details": sorted(details.keys()),
    }
    return SegmentationResult(
        labels=np.asarray(labels, dtype=np.int32),
        method="stardist",
        metadata=metadata,
    )
