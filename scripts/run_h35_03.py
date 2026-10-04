#!/usr/bin/env python3
"""Run the preregistered H35-03 magnetic-low/flank-curvature screen.

The LHS and nested spatial validation are fully local; this script never logs
into DrivenData or submits a competition entry. A new TIFF is emitted only when
both the registered baseline and exact-incumbent promotion gates pass, and its
prediction array differs from every GeoTIFF already in the local download folder.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe35.design import assert_latin_stratified, mixed_latin_hypercube  # noqa: E402
from gemsdoe35.io import FEATURE_BANDS, read_inputs, write_json, write_submission  # noqa: E402
from gemsdoe35.validation import run_nested_spatial_lhs_screen  # noqa: E402

READ_BANDS = {
    "mag_anom": FEATURE_BANDS["mag_anom"],
    "rtp": FEATURE_BANDS["rtp"],
    "tmi": FEATURE_BANDS["tmi"],
    "tmi_hg": FEATURE_BANDS["tmi_hg"],
    "depth_to_base_surf": FEATURE_BANDS["depth_to_base_surf"],
    "det_elev_slope": FEATURE_BANDS["det_elev_slope"],
    "iso_grav_anom_hg": FEATURE_BANDS["iso_grav_anom_hg"],
    "cond_surf": FEATURE_BANDS["cond_surf"],
}


def _canonical_prediction_hash(prediction: np.ndarray, domain: np.ndarray) -> str:
    digest = hashlib.sha256()
    digest.update(np.ascontiguousarray(domain, dtype=np.uint8).tobytes())
    digest.update(np.ascontiguousarray(prediction[domain], dtype=np.float32).tobytes())
    return digest.hexdigest()


def _duplicate_scan(
    prediction: np.ndarray,
    domain: np.ndarray,
    existing_paths: list[Path],
) -> dict[str, Any]:
    """Compare prediction arrays, not filenames or GeoTIFF byte encodings."""
    candidate_hash = _canonical_prediction_hash(prediction, domain)
    matches: list[dict[str, str]] = []
    checked: list[dict[str, str]] = []
    for path in existing_paths:
        try:
            with rasterio.open(path) as dataset:
                if dataset.count != 1 or (dataset.height, dataset.width) != domain.shape:
                    continue
                existing = dataset.read(1)
                existing_domain = np.isfinite(existing)
                if not np.array_equal(existing_domain, domain):
                    continue
                existing_hash = _canonical_prediction_hash(existing, domain)
                checked.append({"file": str(path.relative_to(ROOT)), "prediction_array_sha256": existing_hash})
                if np.array_equal(existing[domain].astype(np.float32, copy=False), prediction[domain].astype(np.float32, copy=False)):
                    matches.append({"file": str(path.relative_to(ROOT)), "prediction_array_sha256": existing_hash})
        except (OSError, rasterio.errors.RasterioError):
            # A malformed/unreadable prior raster cannot be treated as a match,
            # but is recorded for review instead of silently swallowed.
            checked.append({"file": str(path.relative_to(ROOT)), "scan_error": "unreadable GeoTIFF"})
    return {
        "scope": "only GeoTIFFs present in the local docs/downloads folder; not a global prior-submission audit",
        "candidate_prediction_array_sha256": candidate_hash,
        "files_compared_with_matching_shape_and_footprint": checked,
        "exact_prediction_matches": matches,
        "unique_within_local_downloads": not matches,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", default="data/raw/training_features.tif")
    parser.add_argument("--labels", default="data/raw/labels.tif")
    parser.add_argument("--template", default="data/raw/sample_submission.tif")
    parser.add_argument("--design", default="configs/h35-03-lhs.json")
    parser.add_argument("--incumbent-report", default=None)
    parser.add_argument("--reports", default="reports")
    parser.add_argument("--downloads", default="docs/downloads")
    parser.add_argument("--require-pass", action="store_true", help="exit 2 if the promotion gate fails")
    parser.add_argument("--no-export", action="store_true", help="screen only; never write a TIFF")
    args = parser.parse_args()

    design_path = ROOT / args.design
    design_spec = json.loads(design_path.read_text(encoding="utf-8"))
    numeric = {key: tuple(value) for key, value in design_spec["numeric_factors"].items()}
    fixed = dict(design_spec["fixed_factors"])
    promotion_rule = dict(design_spec["promotion_rule"])
    minimum_positive_outer_folds = int(
        promotion_rule["minimum_positive_outer_tiles_against_each_comparator"]
    )
    expected_outer_tiles = int(promotion_rule["outer_tile_count"])
    if expected_outer_tiles != int(fixed.get("spatial_rows", 3)) * int(fixed.get("spatial_cols", 2)):
        raise SystemExit("promotion_rule.outer_tile_count does not match the registered spatial grid")
    if not promotion_rule.get("mean_outer_delta_vs_baseline_and_incumbent_must_be_positive"):
        raise SystemExit("H35-03 requires positive mean deltas against both comparators")
    if not promotion_rule.get("require_exact_matched_actual_emission_in_every_outer_tile"):
        raise SystemExit("H35-03 requires exact matched actual emission in every outer tile")
    if promotion_rule.get("comparators") != ["tmi_hg", fixed["incumbent_design_id"]]:
        raise SystemExit("promotion_rule comparators do not match the declared baseline/incumbent")
    if promotion_rule.get("competition_slot_automated") is not False:
        raise SystemExit("competition submissions must remain manual")
    incumbent_report_path = ROOT / (args.incumbent_report or fixed["incumbent_report"])
    incumbent_report = json.loads(incumbent_report_path.read_text(encoding="utf-8"))
    if not incumbent_report.get("gate", {}).get("passed"):
        raise SystemExit(f"registered incumbent did not pass its local gate: {incumbent_report_path}")
    incumbent_config = incumbent_report.get("selected_config")
    if not isinstance(incumbent_config, dict) or not incumbent_config.get("design_id"):
        raise SystemExit("incumbent report has no selected configuration")
    if incumbent_config["design_id"] != fixed["incumbent_design_id"]:
        raise SystemExit(
            f"registered incumbent {fixed['incumbent_design_id']} does not match report "
            f"{incumbent_config['design_id']}"
        )

    configs = mixed_latin_hypercube(
        int(design_spec["n_designs"]),
        numeric,
        design_spec["categorical_factors"],
        seed=int(design_spec["seed"]),
        prefix="h35-03",
        fixed=fixed,
    )
    assert_latin_stratified(configs, numeric)
    if len({str(config["design_id"]) for config in configs}) != len(configs):
        raise RuntimeError("LHS produced duplicate design IDs")

    inputs = read_inputs(
        ROOT / args.features,
        ROOT / args.labels,
        ROOT / args.template,
        read_bands=READ_BANDS,
    )
    result = run_nested_spatial_lhs_screen(
        inputs.features,
        inputs.labels,
        inputs.domain,
        configs,
        incumbent_config=incumbent_config,
        pixel_size_m=float(inputs.metadata["pixel_size_m"]),
        spatial_rows=int(fixed.get("spatial_rows", 4)),
        spatial_cols=int(fixed.get("spatial_cols", 2)),
        spatial_margin_px=int(fixed["spatial_margin_px"]),
        minimum_positive_outer_folds=minimum_positive_outer_folds,
        holdout_reuse_note=(
            "H35-01/H35-02 previously reported aggregate scores over all four coarse quadrants, exposing labels in these 3x2 tiles; the middle row also crosses the earlier north/south boundary. "
            "Each outer tile is excluded from its own LHS selection in this nested run, but this is exploratory spatial CV, not a pristine independent replication."
        ),
    )

    generated = datetime.now(timezone.utc)
    timestamp = generated.strftime("%Y%m%dT%H%M%S%fZ")
    report_dir = ROOT / args.reports
    download_dir = ROOT / args.downloads
    report_dir.mkdir(parents=True, exist_ok=True)
    download_dir.mkdir(parents=True, exist_ok=True)
    selected_id = str(result.report["selected_design_id"])
    run_id = f"h35-03-{timestamp}-{selected_id.rsplit('-', 1)[-1]}"
    report = {
        **result.report,
        "run_id": run_id,
        "generated_utc": generated.isoformat(timespec="seconds"),
        "design_spec": str(design_path.relative_to(ROOT)),
        "design_seed": int(design_spec["seed"]),
        "promotion_rule": promotion_rule,
        "incumbent_report": str(incumbent_report_path.relative_to(ROOT)),
        "input_provenance": {
            **inputs.metadata,
            "provenance_class": "owner-supplied mirror; SHA-256 pinned; not organizer-authenticated",
            "official_data_tab_requires_login": True,
        },
        "organizer_score": None,
        "public_score": None,
        "generative_ai_use": {
            "disclosure_required_in_final_narrative": True,
            "extent": "Arena.ai Agent Mode assisted with source review, geological-hypothesis framing, design-of-experiments planning, code implementation, test design, and documentation. The repository scripts generated the raster and experiment artifacts from the local inputs.",
            "competitor_responsibility": "The registered competitor must independently verify code, scientific claims, data rights/provenance, artifact validity, and all final submission statements.",
        },
    }

    design_csv = report_dir / f"{run_id}-design.csv"
    report_path = report_dir / f"{run_id}.json"
    if design_csv.exists() or report_path.exists():
        raise FileExistsError(f"refusing to overwrite an existing H35-03 run: {run_id}")
    with design_csv.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(configs[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(configs)
    report["design_csv"] = str(design_csv.relative_to(ROOT))

    duplicate_audit: dict[str, Any] | None = None
    tif_path: Path | None = None
    if result.report["gate"]["passed"] and result.prediction is not None:
        duplicate_audit = _duplicate_scan(
            result.prediction,
            inputs.domain,
            sorted(download_dir.glob("*.tif")),
        )
        report["duplicate_audit"] = duplicate_audit
        if duplicate_audit["unique_within_local_downloads"] and not args.no_export:
            filename = f"gemsdoe35-h35-03-{selected_id.rsplit('-', 1)[-1]}-{timestamp}-candidate.tif"
            tif_path = download_dir / filename
            if tif_path.exists():
                raise FileExistsError(f"refusing to overwrite an existing candidate: {tif_path}")
            note = (
                f"GEMSDOE35 H35-03 LHS {selected_id}; nested 3x2 proxy ΔDTI "
                f"{float(report['outer_summary']['mean_delta_vs_incumbent']):+.4f} vs H35-01; "
                "owner mirror unverified; not organizer-scored."
            )
            if len(note) > 200:
                raise RuntimeError(f"DrivenData note exceeds 200 characters ({len(note)})")
            receipt = write_submission(
                tif_path,
                result.prediction,
                inputs.domain,
                inputs.profile,
                tags={
                    "HYPOTHESIS_ID": "H35-03",
                    "CONFIG_ID": selected_id,
                    "LOCAL_NESTED_SPATIAL_GATE": "passed",
                    "PUBLIC_SCORE": "none",
                },
            )
            report["submission"] = {
                **receipt,
                "submission_name": f"GEMSDOE35-H35-03-{selected_id.rsplit('-', 1)[-1]}-{timestamp}",
                "submission_note": note,
                "status": "local-proxy candidate only; no organizer score; manual provenance/rules review required",
            }
            report["candidate_file"] = str(tif_path.relative_to(ROOT))
        elif not duplicate_audit["unique_within_local_downloads"]:
            report["submission"] = None
            report["candidate_file"] = None
            report["artifact_status"] = "no TIFF emitted: prediction array exactly duplicates a file already in local docs/downloads"
        else:
            report["submission"] = None
            report["candidate_file"] = None
            report["artifact_status"] = "validation only (--no-export); prediction array differs from local downloads"
    else:
        report["submission"] = None
        report["candidate_file"] = None
        report["artifact_status"] = "no TIFF emitted: nested matched-budget promotion gate failed"

    write_json(report_path, report)
    latest = {
        "run_id": run_id,
        "report": str(report_path.relative_to(ROOT)),
        "gate_passed": bool(report["gate"]["passed"]),
        "tif": None if tif_path is None else str(tif_path.relative_to(ROOT)),
        "candidate_file": report.get("candidate_file"),
        "unique_within_local_downloads": (
            None if duplicate_audit is None else duplicate_audit["unique_within_local_downloads"]
        ),
    }
    write_json(report_dir / "h35-03-latest.json", latest)
    write_json(ROOT / "docs/evidence/h35-03-latest.json", report)

    # Keep the public download pointer stable unless a genuinely different,
    # locally unique candidate passed every registered comparison.
    if tif_path is not None:
        write_json(report_dir / "latest.json", {**latest, "tif": str(tif_path.relative_to(ROOT))})
    print(json.dumps(latest, indent=2))
    if tif_path is not None:
        print(f"Candidate TIFF: {tif_path.relative_to(ROOT)}")
        print(f"Submission name: {report['submission']['submission_name']}")
        print(f"Submission note: {report['submission']['submission_note']}")
    else:
        status = str(report["artifact_status"]).removeprefix("no TIFF emitted: ")
        print(f"No new TIFF emitted: {status}")
    if args.require_pass and not report["gate"]["passed"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
