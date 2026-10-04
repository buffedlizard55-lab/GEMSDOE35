import subprocess
import sys
from pathlib import Path

import numpy as np
import rasterio
from affine import Affine

ROOT = Path(__file__).resolve().parents[1]


def _write_raster(path, array, *, dtype, nodata, crs="EPSG:32611"):
    height, width = array.shape
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=width,
        height=height,
        count=1,
        dtype=dtype,
        crs=crs,
        transform=Affine(100, 0, 243350, 0, -100, 4508550),
        nodata=nodata,
    ) as dataset:
        dataset.write(array.astype(dtype), 1)


def _validate(submission, template, labels):
    return subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/validate_submission.py"),
            str(submission),
            "--template",
            str(template),
            "--labels",
            str(labels),
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_accepts_valid_probability_geotiff_and_nan_outside(tmp_path):
    template = tmp_path / "template.tif"
    labels = tmp_path / "labels.tif"
    submission = tmp_path / "submission.tif"
    template_values = np.full((8, 9), np.nan, dtype=np.float32)
    template_values[1:7, 1:8] = 0.0
    label_values = np.full((8, 9), -1, dtype=np.int8)
    label_values[1:7, 1:8] = 0
    label_values[3, 4] = 1
    prediction = np.full((8, 9), np.nan, dtype=np.float32)
    prediction[1:7, 1:8] = 0.0
    prediction[3, 4] = 1.0
    _write_raster(template, template_values, dtype="float32", nodata=np.nan)
    _write_raster(labels, label_values, dtype="int8", nodata=-1)
    _write_raster(submission, prediction, dtype="float32", nodata=np.nan)

    result = _validate(submission, template, labels)
    assert result.returncode == 0, result.stdout + result.stderr
    assert '"range_gate": "pass"' in result.stdout
    assert '"sha256"' in result.stdout


def test_cli_rejects_infinity_outside_footprint(tmp_path):
    template = tmp_path / "template.tif"
    labels = tmp_path / "labels.tif"
    submission = tmp_path / "submission.tif"
    template_values = np.full((8, 9), np.nan, dtype=np.float32)
    template_values[1:7, 1:8] = 0.0
    label_values = np.full((8, 9), -1, dtype=np.int8)
    label_values[1:7, 1:8] = 0
    prediction = np.full((8, 9), np.nan, dtype=np.float32)
    prediction[1:7, 1:8] = 0.0
    prediction[0, 0] = np.inf
    _write_raster(template, template_values, dtype="float32", nodata=np.nan)
    _write_raster(labels, label_values, dtype="int8", nodata=-1)
    _write_raster(submission, prediction, dtype="float32", nodata=np.nan)

    result = _validate(submission, template, labels)
    assert result.returncode == 1
    assert "outside-footprint cells must be NaN" in result.stdout
