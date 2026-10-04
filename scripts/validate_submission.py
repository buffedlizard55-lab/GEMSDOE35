#!/usr/bin/env python3
"""Validate an existing single-band GeoTIFF against the local official-grid files."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.crs import CRS

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("submission")
    parser.add_argument("--template", default="data/raw/sample_submission.tif")
    parser.add_argument("--labels", default="data/raw/labels.tif")
    parser.add_argument("--receipt", default=None)
    args = parser.parse_args()
    submission_path = (ROOT / args.submission).resolve()
    template_path = (ROOT / args.template).resolve()
    labels_path = (ROOT / args.labels).resolve()
    errors: list[str] = []
    try:
        with rasterio.open(template_path) as template, rasterio.open(labels_path) as labels, rasterio.open(submission_path) as pred:
            if (template.width, template.height) != (labels.width, labels.height):
                errors.append("template and labels shapes differ")
            if template.crs != labels.crs or tuple(template.transform) != tuple(labels.transform):
                errors.append("template and labels georeferencing differ")
            expected_shape = (template.height, template.width)
            if (pred.height, pred.width) != expected_shape:
                errors.append(f"submission shape {(pred.height, pred.width)} != expected {expected_shape}")
            if pred.count != 1:
                errors.append(f"submission has {pred.count} bands, expected 1")
            if pred.dtypes != ("float32",):
                errors.append(f"submission dtype {pred.dtypes} != float32")
            if pred.crs != CRS.from_epsg(32611) or pred.crs != template.crs:
                errors.append(f"submission CRS {pred.crs} != EPSG:32611 / template CRS")
            if tuple(pred.transform) != tuple(template.transform):
                errors.append("submission geotransform differs from template")
            tmpl = template.read(1)
            label = labels.read(1)
            expected = np.isfinite(tmpl)
            if template.nodata is not None and np.isfinite(template.nodata):
                expected &= tmpl != template.nodata
            label_valid = np.ones(label.shape, dtype=bool) if labels.nodata is None else label != labels.nodata
            if not np.array_equal(expected, label_valid):
                errors.append("template and label footprints differ; cannot establish expected nodata mask")
            arr = pred.read(1)
            actual = np.isfinite(arr)
            if not np.array_equal(actual, expected):
                errors.append("submission finite/nodata footprint differs from template")
            if np.any(~np.isfinite(arr[expected])):
                errors.append("submission contains NaN/inf inside the valid footprint")
            if np.any((arr[expected] < 0.0) | (arr[expected] > 1.0)):
                errors.append("submission predictions outside [0, 1]")
            if pred.nodata is None or not np.isnan(pred.nodata):
                errors.append("submission must encode outside-footprint cells as NaN nodata")
            receipt = {
                "file": str(submission_path.relative_to(ROOT)) if submission_path.is_relative_to(ROOT) else str(submission_path),
                "shape": list(arr.shape),
                "dtype": pred.dtypes[0],
                "crs": pred.crs.to_string() if pred.crs else None,
                "transform": list(pred.transform),
                "valid_pixels": int(expected.sum()),
                "finite_pixels": int(actual.sum()),
                "min_inside": float(arr[expected].min()) if expected.any() else None,
                "max_inside": float(arr[expected].max()) if expected.any() else None,
                "positive_pixels": int(np.count_nonzero(arr[expected] > 0.0)),
                "range_gate": "pass" if not any("[0, 1]" in error for error in errors) else "fail",
                "errors": errors,
            }
    except Exception as exc:
        print(f"Cannot validate submission: {exc}", file=sys.stderr)
        return 2
    if args.receipt:
        out = ROOT / args.receipt
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
