#!/usr/bin/env python3
"""Rebuild a candidate prediction array from its saved config and pinned inputs.

This is a verification tool: it never writes or uploads a TIFF. It checks that
the offered GeoTIFF exactly equals the algorithm's deterministic output on the
local input mirror and saves a provenance-aware receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe35.features import candidate_surface  # noqa: E402
from gemsdoe35.io import read_inputs, sha256_file, write_json  # noqa: E402
from gemsdoe35.validation import _top_k_mask  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default="reports/h35-01-20261004T164802Z-e58e5dbee6.json")
    parser.add_argument("--features", default="data/raw/training_features.tif")
    parser.add_argument("--labels", default="data/raw/labels.tif")
    parser.add_argument("--template", default="data/raw/sample_submission.tif")
    parser.add_argument("--tif", default="docs/downloads/gemsdoe35-h35-01-e58e5dbee6-20261004T164802Z-candidate.tif")
    parser.add_argument("--receipt", default="reports/candidate-reconstruction.json")
    args = parser.parse_args()

    report_path = ROOT / args.report
    candidate_path = ROOT / args.tif
    report = json.loads(report_path.read_text(encoding="utf-8"))
    config = report.get("selected_config")
    if not isinstance(config, dict) or not config.get("design_id"):
        raise SystemExit("experiment report has no selected configuration")
    if not candidate_path.is_file():
        raise SystemExit(f"candidate TIFF is missing: {candidate_path}")
    inputs = read_inputs(ROOT / args.features, ROOT / args.labels, ROOT / args.template)
    score, diagnostics = candidate_surface(
        inputs.features,
        inputs.domain,
        config,
        pixel_size_m=float(inputs.metadata["pixel_size_m"]),
    )
    output_domain = inputs.domain & ~inputs.labels
    allowed = output_domain & np.isfinite(score) & (score > 0.0)
    requested = int(round(float(config["prediction_fraction"]) * int(output_domain.sum())))
    reconstructed, emitted = _top_k_mask(score, allowed, requested)

    with rasterio.open(candidate_path) as dataset:
        saved = dataset.read(1)
        grid_ok = (
            dataset.count == 1
            and dataset.dtypes == ("float32",)
            and dataset.crs == rasterio.crs.CRS.from_epsg(32611)
            and (dataset.height, dataset.width) == inputs.domain.shape
            and tuple(dataset.transform) == tuple(inputs.profile["transform"])
        )
        domain_match = np.array_equal(np.isfinite(saved), inputs.domain)
        exact_values = domain_match and np.array_equal(saved[inputs.domain], reconstructed[inputs.domain])
        outside_nan = bool(np.isnan(saved[~inputs.domain]).all()) if (~inputs.domain).any() else True
        positive = int(np.count_nonzero(saved[inputs.domain] > 0.0))
        nodata = dataset.nodata
        nodata_is_nan = nodata is not None and np.isnan(nodata)

    prediction_hash = hashlib.sha256(
        np.ascontiguousarray(reconstructed).tobytes() + np.ascontiguousarray(inputs.domain).tobytes()
    ).hexdigest()
    try:
        candidate_display = str(candidate_path.relative_to(ROOT))
    except ValueError:
        candidate_display = str(candidate_path)
    receipt = {
        "schema_version": "gemsdoe35-candidate-reproduction-v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "exact_prediction_reproduction_passed" if exact_values and grid_ok and outside_nan and nodata_is_nan else "reproduction_or_grid_check_failed",
        "candidate_file": candidate_display,
        "candidate_sha256": sha256_file(candidate_path),
        "candidate_bytes": candidate_path.stat().st_size,
        "prediction_array_sha256": prediction_hash,
        "hypothesis_id": report.get("hypothesis_id") or "-".join(str(report.get("run_id", "H35-01")).split("-")[:2]).upper(),
        "config_id": config["design_id"],
        "feature_detector": diagnostics.get("method"),
        "exact_prediction_array_match_on_domain": bool(exact_values),
        "grid_matches_owner_mirror_template": bool(grid_ok),
        "finite_footprint_matches_template": bool(domain_match),
        "outside_cells_are_nan": outside_nan,
        "nodata_tag_is_nan": bool(nodata_is_nan),
        "emitted_cells_reconstructed": int(emitted),
        "positive_cells_in_tif": positive,
        "source_hashes": {
            "features": inputs.metadata["features_sha256"],
            "labels": inputs.metadata["labels_sha256"],
            "template": inputs.metadata["template_sha256"],
        },
        "provenance_class": "pinned public owner-maintained mirror; not organizer-authenticated",
        "global_duplicate_comparison": "not possible from this checkout because prior submission rasters were not supplied; this receipt proves exact reconstruction from the saved local config, not uniqueness versus every external artifact",
        "organizer_score": None,
    }
    write_json(ROOT / args.receipt, receipt)
    write_json(ROOT / "docs/evidence/candidate-reconstruction.json", receipt)
    print(json.dumps(receipt, indent=2))
    return 0 if receipt["status"] == "exact_prediction_reproduction_passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
