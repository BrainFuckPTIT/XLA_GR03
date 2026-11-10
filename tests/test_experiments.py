import csv

import numpy as np
import pytest
import run_experiment
from compare_fiji_python import compare_labels
from tifffile import imwrite

from xla_gr03.experiments import dataset_manifest, paired_images, sha256


def test_missing_ground_truth_is_an_error(tmp_path):
    imwrite(tmp_path / "a.tif", np.zeros((4, 4), np.uint8))
    with pytest.raises(ValueError, match="a.tif"):
        paired_images(tmp_path, tmp_path / "masks")


def test_imported_labels_never_measure_disk_read_as_inference(tmp_path, monkeypatch):
    for name in ("images", "masks", "labels"):
        (tmp_path / name).mkdir()
    image = np.zeros((24, 24), np.uint16)
    image[4:15, 4:15] = 1
    for folder in ("images", "masks", "labels"):
        imwrite(tmp_path / folder / "a.tif", image)
    imwrite(tmp_path / "images/b.tif", image)
    imwrite(tmp_path / "masks/b.tif", image)
    argv = [
        "run_experiment",
        "--images",
        str(tmp_path / "images"),
        "--ground-truth",
        str(tmp_path / "masks"),
        "--stardist-labels",
        str(tmp_path / "labels"),
        "--output",
        str(tmp_path / "output"),
        "--iou",
        "0.75",
    ]
    monkeypatch.setattr("sys.argv", argv)
    with pytest.raises(ValueError, match="b.tif"):
        run_experiment.main()
    monkeypatch.setattr("sys.argv", argv + ["--allow-missing-stardist"])
    run_experiment.main()
    rows = list(csv.DictReader((tmp_path / "output/metrics.csv").open()))
    imported = [r for r in rows if r["method"] == "stardist_imported"]
    assert imported[0]["runtime_s"] == ""
    assert imported[0]["threshold"] == "0.75"
    assert imported[1]["status"] == "missing_prediction"
    assert len(rows) == 6
    log = tmp_path / "log.csv"
    log.write_text("image,runtime_s\na.tif,1.234\n", encoding="utf-8")
    monkeypatch.setattr("sys.argv", argv + ["--allow-missing-stardist", "--run-log", str(log)])
    run_experiment.main()
    rows = list(csv.DictReader((tmp_path / "output/metrics.csv").open()))
    assert next(r for r in rows if r["method"] == "stardist_imported")["runtime_s"] == "1.234"


def test_manifest_checks_shape_and_records_content_hash(tmp_path):
    image, mask = tmp_path / "image.tif", tmp_path / "mask.tif"
    imwrite(image, np.zeros((8, 9), np.uint8))
    imwrite(mask, np.zeros((8, 9), np.uint16))
    row = dataset_manifest([(image, mask)], "test")[0]
    assert row["image_sha256"] == sha256(image)
    assert row["width"] == 9
    imwrite(mask, np.zeros((9, 8), np.uint16))
    with pytest.raises(ValueError, match="matching 2D"):
        dataset_manifest([(image, mask)], "test")


def test_comparison_is_invariant_to_instance_id_permutation():
    true = np.zeros((8, 8), np.int32)
    true[1:3, 1:3], true[4:7, 4:7] = 1, 2
    pred = np.where(true == 1, 70, np.where(true == 2, 10, 0))
    scores, errors = compare_labels(true, pred)
    assert scores["matched_pixel_agreement_foreground"] == 1
    assert scores["criterion_f1_095_dice_095"]
    assert not errors.any()
