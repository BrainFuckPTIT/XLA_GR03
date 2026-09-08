import json

import numpy as np
import tifffile

from xla_gr03.cli import main
from xla_gr03.io import read_image, save_labels


def test_label_tiff_round_trip(tmp_path) -> None:
    labels = np.zeros((7, 8), dtype=np.int32)
    labels[1:4, 2:6] = 70000
    output = tmp_path / "labels.tif"

    save_labels(output, labels)
    restored = read_image(output)

    assert restored.dtype == np.uint32
    np.testing.assert_array_equal(restored, labels)


def test_cli_evaluate_writes_json(tmp_path, capsys) -> None:
    labels = np.zeros((8, 8), dtype=np.uint16)
    labels[2:6, 2:6] = 1
    true_path = tmp_path / "true.tif"
    pred_path = tmp_path / "pred.tif"
    json_path = tmp_path / "metrics.json"
    tifffile.imwrite(true_path, labels)
    tifffile.imwrite(pred_path, labels)

    status = main(
        [
            "evaluate",
            str(true_path),
            str(pred_path),
            "--thresholds",
            "0.5",
            "0.75",
            "--output-json",
            str(json_path),
        ]
    )
    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert status == 0
    assert len(payload["metrics"]) == 2
    assert payload["metrics"][0]["panoptic_quality"] == 1.0
    assert '"panoptic_quality": 1.0' in capsys.readouterr().out


def test_cli_segments_with_otsu(tmp_path) -> None:
    image = np.zeros((32, 32), dtype=np.uint8)
    image[5:12, 5:12] = 255
    image[20:28, 21:29] = 255
    input_path = tmp_path / "input.tif"
    output_path = tmp_path / "prediction.tif"
    tifffile.imwrite(input_path, image)

    status = main(
        [
            "segment",
            str(input_path),
            str(output_path),
            "--method",
            "otsu",
            "--gaussian-sigma",
            "0",
            "--min-size",
            "1",
            "--closing-radius",
            "0",
        ]
    )
    labels = read_image(output_path)

    assert status == 0
    assert np.unique(labels[labels > 0]).size == 2
