from pathlib import Path

import numpy as np
import rasterio
from affine import Affine

from gemsdoe35.io import read_inputs, write_submission


def _make_rasters(tmp_path: Path):
    h, w = 64, 80
    transform = Affine(100, 0, 300000, 0, -100, 4400000)
    crs = "EPSG:32611"
    feature_path = tmp_path / "features.tif"
    label_path = tmp_path / "labels.tif"
    template_path = tmp_path / "template.tif"
    features = np.zeros((19, h, w), dtype=np.float32)
    for i in range(19):
        features[i] = np.indices((h, w))[1] + i
    features[:, :4, :4] = -3.4028235e38
    with rasterio.open(
        feature_path, "w", driver="GTiff", width=w, height=h, count=19, dtype="float32",
        crs=crs, transform=transform, nodata=-3.4028235e38,
    ) as dst:
        dst.write(features)
        for band in range(1, 20):
            dst.set_band_description(band, f"band-{band}")
    labels = np.zeros((h, w), dtype=np.int8)
    labels[:4, :] = -1
    labels[20:25, 20] = 1
    with rasterio.open(
        label_path, "w", driver="GTiff", width=w, height=h, count=1, dtype="int8",
        crs=crs, transform=transform, nodata=-1,
    ) as dst:
        dst.write(labels, 1)
    template = np.full((h, w), np.nan, dtype=np.float32)
    template[labels != -1] = 0.0
    with rasterio.open(
        template_path, "w", driver="GTiff", width=w, height=h, count=1, dtype="float32",
        crs=crs, transform=transform, nodata=np.nan,
    ) as dst:
        dst.write(template, 1)
    return feature_path, label_path, template_path


def test_read_and_submission_round_trip_checks_footprint(tmp_path):
    feature_path, label_path, template_path = _make_rasters(tmp_path)
    inputs = read_inputs(feature_path, label_path, template_path)
    assert inputs.domain.sum() == 60 * 80
    assert inputs.labels.sum() == 5
    assert inputs.metadata["feature_missing_inside_domain"]["rtp"] == 0
    prediction = np.zeros(inputs.domain.shape, dtype=np.float32)
    prediction[30, 30] = 1.0
    receipt = write_submission(tmp_path / "candidate.tif", prediction, inputs.domain, inputs.profile)
    assert receipt["postwrite_reread_verified"] is True
    assert receipt["valid_pixels"] == 60 * 80
    with rasterio.open(tmp_path / "candidate.tif") as ds:
        values = ds.read(1)
        assert ds.count == 1
        assert ds.dtypes == ("float32",)
        assert np.isnan(values[0, 0])
        assert values[30, 30] == 1.0


def test_read_refuses_mismatched_label_and_template_masks(tmp_path):
    feature_path, label_path, template_path = _make_rasters(tmp_path)
    with rasterio.open(template_path, "r+") as ds:
        a = ds.read(1)
        a[10, 10] = np.nan
        ds.write(a, 1)
    try:
        read_inputs(feature_path, label_path, template_path)
    except ValueError as exc:
        assert "footprints differ" in str(exc)
    else:
        raise AssertionError("expected mismatched masks to be rejected")
