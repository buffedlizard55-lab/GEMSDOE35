#!/usr/bin/env python3
"""Run the preregistered H35-06 topographic scarp curvature spatial-LHS screen.

The script uses detrended elevation, slope, potential-field tilt curvature,
and basement depth bands from local inputs, performs nested spatial validation
against matched-mass `tmi_hg` and H35-01 comparators, and never contacts or
submits to DrivenData. By default a GeoTIFF is written only if the registered
local promotion gate passes. `--export-experimental` can explicitly write a
unique, locally experimental artifact after a failed gate; it is always marked
not slot-eligible here.
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
from gemsdoe35.features import candidate_surface  # noqa: E402
from gemsdoe35.io import FEATURE_BANDS, read_inputs, write_json, write_submission  # noqa: E402
from gemsdoe35.validation import _top_k_mask, run_nested_spatial_lhs_screen  # noqa: E402

READ_BANDS = {
    # H35-06 candidate layers.
    "det_elev": FEATURE_BANDS["det_elev"],
    "det_elev_slope": FEATURE_BANDS["det_elev_slope"],
    "tc": FEATURE_BANDS["tc"],
    "depth_to_base_surf": FEATURE_BANDS["depth_to_base_surf"],
    "iso_grav_anom_hg": FEATURE_BANDS["iso_grav_anom_hg"],
    # H35-01 incumbent and `tmi_hg` baseline layers required for fair comparison.
    "rtp": FEATURE_BANDS["rtp"],
    "tmi": FEATURE_BANDS["tmi"],
    "tmi_hg": FEATURE_BANDS["tmi_hg"],
}


def prediction_hash(prediction: np.ndarray, domain: np.ndarray) -> str:
    digest = hashlib.sha256()
    digest.update(np.ascontiguousarray(domain, dtype=np.uint8).tobytes())
    digest.update(np.ascontiguousarray(prediction[domain], dtype=np.float32).tobytes())
    return digest.hexdigest()


def _dataset_domain(dataset: rasterio.io.DatasetReader, values: np.ndarray) -> np.ndarray:
    valid = np.isfinite(values)
    if dataset.nodata is not None:
        if np.isnan(dataset.nodata):
            valid &= ~np.isnan(values)
        else:
            valid &= values != dataset.nodata
    return valid


def scan_local_tiffs(
    prediction: np.ndarray,
    domain: np.ndarray,
    *,
    profile: dict[str, Any],
    roots: tuple[Path, ...] = (ROOT / "docs", ROOT / "data", ROOT / "outputs"),
) -> dict[str, Any]:
    """Compare canonical arrays on the exact grid, not filenames or TIFF bytes."""
    candidate_sha = prediction_hash(prediction, domain)
    compared: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    exact_matches: list[dict[str, str]] = []
    unreadable: list[dict[str, str]] = []
    paths = sorted({path for root in roots if root.exists() for path in root.rglob("*.tif")})
    expected_crs = rasterio.crs.CRS.from_user_input(profile["crs"])
    expected_transform = tuple(profile["transform"])

    for path in paths:
        try:
            with rasterio.open(path) as dataset:
                if dataset.count != 1 or (dataset.height, dataset.width) != domain.shape:
                    skipped.append({"file": str(path.relative_to(ROOT)), "reason": "band count or shape differs"})
                    continue
                if dataset.crs != expected_crs or tuple(dataset.transform) != expected_transform:
                    skipped.append({"file": str(path.relative_to(ROOT)), "reason": "CRS or geotransform differs"})
                    continue
                existing = dataset.read(1)
                existing_domain = _dataset_domain(dataset, existing)
                if not np.array_equal(existing_domain, domain):
                    skipped.append({"file": str(path.relative_to(ROOT)), "reason": "valid-data footprint differs"})
                    continue
                digest = prediction_hash(existing, domain)
                record = {"file": str(path.relative_to(ROOT)), "prediction_array_sha256": digest}
                compared.append(record)
                if np.array_equal(existing[domain].astype(np.float32, copy=False), prediction[domain].astype(np.float32, copy=False)):
                    exact_matches.append(record)
        except (OSError, rasterio.errors.RasterioError, ValueError) as exc:
            unreadable.append({"file": str(path.relative_to(ROOT)), "error": type(exc).__name__})

    complete = not unreadable
    return {
        "scope": "all readable .tif files under local docs/, data/, and outputs/ with matching one-band grid and footprint; not a global competition-upload archive",
        "candidate_prediction_array_sha256": candidate_sha,
        "files_compared_with_matching_crs_shape_transform_and_footprint": compared,
        "skipped_files": skipped,
        "unreadable_files": unreadable,
        "scan_complete": complete,
        "exact_prediction_matches": exact_matches,
        "unique_within_local_scan": bool(complete and not exact_matches),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", default="data/raw/training_features.tif")
    parser.add_argument("--labels", default="data/raw/labels.tif")
    parser.add_argument("--template", default="data/raw/sample_submission.tif")
    parser.add_argument("--design", default="configs/h35-06-lhs.json")
    parser.add_argument("--reports", default="reports")
    parser.add_argument("--downloads", default="docs/downloads")
    parser.add_argument("--require-pass", action="store_true", help="exit 2 if the registered local promotion gate fails")
    parser.add_argument("--no-export", action="store_true", help="screen only; do not write a GeoTIFF")
    parser.add_argument("--export-experimental", action="store_true", help="write a local research TIF even if the gate fails; never slot-eligible")
    args = parser.parse_args()

    design_path = ROOT / args.design
    spec = json.loads(design_path.read_text(encoding="utf-8"))
    numeric = {name: tuple(bounds) for name, bounds in spec["numeric_factors"].items()}
    fixed = dict(spec["fixed_factors"])
    gate_spec = dict(spec["promotion_rule"])
    if gate_spec.get("competition_slot_automated") is not False:
        raise SystemExit("competition submission must remain manual")

    incumbent_path = ROOT / fixed["incumbent_report"]
    incumbent_report = json.loads(incumbent_path.read_text(encoding="utf-8"))
    incumbent_config = incumbent_report.get("selected_config")
    if not incumbent_report.get("gate", {}).get("passed") or not isinstance(incumbent_config, dict):
        raise SystemExit("the registered H35-01 incumbent report is missing or failed")
    if incumbent_config.get("design_id") != fixed["incumbent_design_id"]:
        raise SystemExit("incumbent ID differs from the preregistered H35-06 comparator")

    configs = mixed_latin_hypercube(
        int(spec["n_designs"]),
        numeric,
        spec["categorical_factors"],
        seed=int(spec["seed"]),
        prefix="h35-06",
        fixed=fixed,
    )
    assert_latin_stratified(configs, numeric)
    if len({str(row["design_id"]) for row in configs}) != len(configs):
        raise SystemExit("duplicate H35-06 design IDs")

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
        spatial_rows=int(fixed["spatial_rows"]),
        spatial_cols=int(fixed["spatial_cols"]),
        spatial_margin_px=int(fixed["spatial_margin_px"]),
        minimum_positive_outer_folds=int(gate_spec["minimum_positive_outer_tiles_against_each_comparator"]),
        holdout_reuse_note=(
            "H35-01 through H35-05 previously summarized this known-catalogue label geography. "
            "Each outer tile is excluded from its own H35-06 configuration selection, but prior exposure makes this exploratory nested spatial CV, "
            "not an untouched independent confirmation or validation against newly identified private faults."
        ),
    )

    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%S%fZ")
    run_id = f"h35-06-{stamp}-{str(result.report['selected_design_id']).rsplit('-', 1)[-1]}"
    report_dir = ROOT / args.reports
    download_dir = ROOT / args.downloads
    report_dir.mkdir(parents=True, exist_ok=True)
    download_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{run_id}.json"
    design_csv = report_dir / f"{run_id}-design.csv"
    if report_path.exists() or design_csv.exists():
        raise FileExistsError(f"refusing to overwrite existing H35-06 run {run_id}")
    with design_csv.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(configs[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(configs)

    report: dict[str, Any] = {
        **result.report,
        "hypothesis_id": "H35-06",
        "run_id": run_id,
        "generated_utc": now.isoformat(timespec="seconds"),
        "design_spec": str(design_path.relative_to(ROOT)),
        "design_seed": int(spec["seed"]),
        "design_csv": str(design_csv.relative_to(ROOT)),
        "promotion_rule": gate_spec,
        "incumbent_report": str(incumbent_path.relative_to(ROOT)),
        "input_provenance": {
            **inputs.metadata,
            "provenance_class": "public owner-maintained mirror; pinned hashes; not organizer-authenticated",
            "official_data_tab_requires_login": True,
        },
        "source_notes": {
            "band_descriptions": inputs.metadata.get("feature_band_descriptions", {}),
            "band_metadata_provenance": "the descriptions were read from the public owner-mirror GeoTIFF; not authenticated as official organizer metadata",
            "geomorphic_scarp_caveat": "topographic slope breaks and relief curvature reflect both Quaternary fault scarps and non-tectonic erosional features (drainages, alluvial edges)",
        },
        "organizer_score": None,
        "public_score": None,
        "competition_slot_used": False,
        "generative_ai_use": {
            "disclosure_required_in_final_narrative": True,
            "extent": "Arena.ai Agent Mode assisted with source review, geological-hypothesis framing, design-of-experiments planning, code implementation, test design, and documentation. Repository scripts generated the candidate raster and experiment artifacts from the local inputs.",
            "competitor_responsibility": "The registered competitor must independently verify code, scientific claims, data rights/provenance, artifact validity, and all final submission statements.",
        },
    }
    report["gate"]["slot_eligible"] = False
    report["gate"]["slot_note"] = (
        "This proxy screen never spends a competition slot. Input rasters are a public owner-maintained mirror, not organizer-authenticated; "
        "the labels are existing catalogue faults, not the hidden newly identified target; and this geography was previously exposed."
    )

    passed = bool(report["gate"]["passed"])
    export = not args.no_export and (passed or args.export_experimental)
    tif_path: Path | None = None
    if export:
        chosen = dict(report["selected_config"])
        surface, diagnostics = candidate_surface(
            inputs.features,
            inputs.domain,
            chosen,
            pixel_size_m=float(inputs.metadata["pixel_size_m"]),
        )
        allowed = inputs.domain & (inputs.labels != 1) & np.isfinite(surface) & (surface > 0.0)
        requested = int(round(float(chosen["prediction_fraction"]) * int(inputs.domain.sum())))
        prediction, emitted = _top_k_mask(surface, allowed, requested)
        if emitted < 1:
            raise RuntimeError("selected H35-06 configuration emitted no in-domain pixels")

        duplicate_audit = scan_local_tiffs(
            prediction,
            inputs.domain,
            profile=inputs.profile,
        )
        report["duplicate_audit"] = duplicate_audit
        report["selected_surface_diagnostics"] = diagnostics
        if not duplicate_audit["scan_complete"]:
            raise RuntimeError("local duplicate scan was incomplete; refusing to assert uniqueness")
        if not duplicate_audit["unique_within_local_scan"]:
            raise RuntimeError("refusing to export a local prediction-array duplicate")

        suffix = str(chosen["design_id"]).rsplit("-", 1)[-1]
        filename = f"gemsdoe35-h35-06-{suffix}-{stamp}-candidate.tif"
        tif_path = download_dir / filename
        if tif_path.exists():
            raise FileExistsError(f"refusing to overwrite existing candidate: {tif_path}")
        note = (
            f"GEMSDOE35 H35-06 scarp-curvature LHS {chosen['design_id']}; "
            f"proxy gate {'passed' if passed else 'FAILED'}; owner mirror unverified; not organizer-scored."
        )
        if len(note) > 200:
            raise RuntimeError(f"DrivenData note exceeds 200 characters ({len(note)})")
        receipt = write_submission(
            tif_path,
            prediction,
            inputs.domain,
            inputs.profile,
            tags={
                "HYPOTHESIS_ID": "H35-06",
                "CONFIG_ID": str(chosen["design_id"]),
                "LOCAL_PROXY_GATE": "passed" if passed else "failed_experimental_only",
                "COMPETITION_SLOT_ELIGIBLE": "false",
                "PUBLIC_SCORE": "none",
            },
        )
        report["submission"] = {
            **receipt,
            "submission_name": f"GEMSDOE35-H35-06-{suffix}-{stamp}",
            "submission_note": note,
            "status": "local experimental artifact; never slot-eligible from this owner-mirror screen; no organizer score",
            "prediction_array_sha256": duplicate_audit["candidate_prediction_array_sha256"],
            "positive_pixels": int(emitted),
        }
        report["candidate_file"] = str(tif_path.relative_to(ROOT))
        report["artifact_status"] = (
            "unique local research TIF emitted despite failed proxy gate; NOT slot-eligible"
            if not passed
            else "local proxy gate passed; TIF written for manual provenance review; not organizer-scored or automatically submitted"
        )
        report["final_candidate_emitted_pixels"] = int(emitted)
    else:
        report["submission"] = None
        report["candidate_file"] = None
        report["artifact_status"] = "no TIF emitted: screen-only mode or failed gate without --export-experimental"

    write_json(report_path, report)
    latest = {
        "run_id": run_id,
        "report": str(report_path.relative_to(ROOT)),
        "gate_passed": passed,
        "slot_eligible": False,
        "tif": None if tif_path is None else str(tif_path.relative_to(ROOT)),
        "unique_within_local_scan": None if tif_path is None else report["duplicate_audit"]["unique_within_local_scan"],
    }
    write_json(report_dir / "h35-06-latest.json", latest)
    write_json(ROOT / "docs/evidence/h35-06-latest.json", report)
    if tif_path is not None:
        write_json(report_dir / "latest.json", latest)
        write_json(ROOT / "docs/evidence/latest-experiment.json", report)
    print(json.dumps(latest, indent=2))
    if tif_path is not None:
        print("Candidate TIFF:", tif_path.relative_to(ROOT))
        print("Submission name:", report["submission"]["submission_name"])
        print("Submission note:", report["submission"]["submission_note"])
        print("Slot eligible: NO")
    if args.require_pass and not passed:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
