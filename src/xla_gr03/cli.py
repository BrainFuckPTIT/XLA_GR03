"""Command-line interface for segmentation and quantitative evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .baselines import segment_otsu, segment_watershed
from .io import read_image, save_labels
from .metrics import evaluate_at_thresholds
from .stardist_pipeline import PRETRAINED_MODELS, segment_stardist


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="xla-gr03", description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    segment = subparsers.add_parser("segment", help="Segment one 2D image.")
    segment.add_argument("input", type=Path)
    segment.add_argument("output", type=Path)
    segment.add_argument("--method", choices=("otsu", "watershed", "stardist"), required=True)
    segment.add_argument("--foreground", choices=("bright", "dark"), default="bright")
    segment.add_argument("--gaussian-sigma", type=float, default=1.0)
    segment.add_argument("--min-size", type=int, default=20)
    segment.add_argument("--closing-radius", type=int, default=1)
    segment.add_argument("--min-distance", type=int, default=5)
    segment.add_argument("--watershed-line", action="store_true")
    segment.add_argument("--model", choices=sorted(PRETRAINED_MODELS), default="2D_versatile_fluo")
    segment.add_argument("--custom-model-dir", type=Path)
    segment.add_argument("--pmin", type=float, default=1.0)
    segment.add_argument("--pmax", type=float, default=99.8)
    segment.add_argument("--prob-thresh", type=float)
    segment.add_argument("--nms-thresh", type=float)
    segment.add_argument("--n-tiles", type=int, nargs=2, metavar=("Y", "X"))

    evaluate = subparsers.add_parser("evaluate", help="Compare two instance label images.")
    evaluate.add_argument("ground_truth", type=Path)
    evaluate.add_argument("prediction", type=Path)
    evaluate.add_argument("--thresholds", type=float, nargs="+", default=[0.5])
    evaluate.add_argument("--output-json", type=Path)
    return parser


def _segment(args: argparse.Namespace) -> int:
    image = read_image(args.input)
    if args.method == "otsu":
        result = segment_otsu(
            image,
            foreground=args.foreground,
            gaussian_sigma=args.gaussian_sigma,
            min_size=args.min_size,
            closing_radius=args.closing_radius,
        )
    elif args.method == "watershed":
        result = segment_watershed(
            image,
            foreground=args.foreground,
            gaussian_sigma=args.gaussian_sigma,
            min_size=args.min_size,
            closing_radius=args.closing_radius,
            min_distance=args.min_distance,
            watershed_line=args.watershed_line,
        )
    else:
        result = segment_stardist(
            image,
            model_name=args.model,
            custom_model_dir=args.custom_model_dir,
            pmin=args.pmin,
            pmax=args.pmax,
            prob_thresh=args.prob_thresh,
            nms_thresh=args.nms_thresh,
            n_tiles=tuple(args.n_tiles) if args.n_tiles else None,
        )

    output_path = save_labels(args.output, result.labels)
    payload = {
        "input": str(args.input),
        "output": str(output_path),
        "method": result.method,
        "object_count": result.object_count,
        "parameters": result.metadata,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def _evaluate(args: argparse.Namespace) -> int:
    ground_truth = read_image(args.ground_truth)
    prediction = read_image(args.prediction)
    results = evaluate_at_thresholds(ground_truth, prediction, args.thresholds)
    payload = {
        "ground_truth": str(args.ground_truth),
        "prediction": str(args.prediction),
        "metrics": [result.to_dict() for result in results],
    }
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    print(serialized)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(serialized + "\n", encoding="utf-8")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the command-line interface."""

    args = _build_parser().parse_args(argv)
    if args.command == "segment":
        return _segment(args)
    return _evaluate(args)


if __name__ == "__main__":
    raise SystemExit(main())
