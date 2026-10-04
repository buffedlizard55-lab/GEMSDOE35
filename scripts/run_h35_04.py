#!/usr/bin/env python3
"""Preregistered H35-04 cross-physics edge-concurrence screen and TIF builder.

The script runs a nested spatial Latin-hypercube screen against the matched-mass
`tmi_hg` baseline and the H35-01 incumbent. It never contacts DrivenData or
submits an entry. `--export-experimental` may write a unique local artifact when
the proxy gate fails, but such a file is explicitly not slot-eligible.
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
    "mag_anom": FEATURE_BANDS["mag_anom"],
    "rtp": FEATURE_BANDS["rtp"],
    "tmi_hg": FEATURE_BANDS["tmi_hg"],
    "tmi": FEATURE_BANDS["tmi"],
    "depth_to_base_surf": FEATURE_BANDS["depth_to_base_surf"],
    "det_elev_slope": FEATURE_BANDS["det_elev_slope"],
    "iso_grav_anom_hg": FEATURE_BANDS["iso_grav_anom_hg"],
    "iso_grav_anom": FEATURE_BANDS["iso_grav_anom"],
    "geod_shearrate": FEATURE_BANDS["geod_shearrate"],
}


def prediction_hash(prediction: np.ndarray, domain: np.ndarray) -> str:
    digest = hashlib.sha256()
    digest.update(np.ascontiguousarray(domain, dtype=np.uint8).tobytes())
    digest.update(np.ascontiguousarray(prediction[domain], dtype=np.float32).tobytes())
    return digest.hexdigest()


def scan_downloads(prediction: np.ndarray, domain: np.ndarray, paths: list[Path]) -> dict[str, Any]:
    candidate_sha = prediction_hash(prediction, domain)
    compared: list[dict[str, str]] = []
    duplicates: list[dict[str, str]] = []
    for path in paths:
        try:
            with rasterio.open(path) as ds:
                if ds.count != 1 or (ds.height, ds.width) != domain.shape:
                    continue
                existing = ds.read(1)
                existing_domain = np.isfinite(existing)
                if not np.array_equal(existing_domain, domain):
                    continue
                digest = prediction_hash(existing, domain)
                record = {"file": str(path.relative_to(ROOT)), "prediction_array_sha256": digest}
                compared.append(record)
                if np.array_equal(existing[domain].astype(np.float32), prediction[domain].astype(np.float32)):
                    duplicates.append(record)
        except (OSError, rasterio.errors.RasterioError):
            compared.append({"file": str(path.relative_to(ROOT)), "scan_error": "unreadable GeoTIFF"})
    return {
        "scope": "all local GeoTIFFs in docs/downloads with the same shape and finite-data footprint; not a global audit",
        "candidate_prediction_array_sha256": candidate_sha,
        "compared": compared,
        "exact_matches": duplicates,
        "unique_within_local_downloads": not duplicates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", default="data/raw/training_features.tif")
    parser.add_argument("--labels", default="data/raw/labels.tif")
    parser.add_argument("--template", default="data/raw/sample_submission.tif")
    parser.add_argument("--design", default="configs/h35-04-lhs.json")
    parser.add_argument("--reports", default="reports")
    parser.add_argument("--downloads", default="docs/downloads")
    parser.add_argument("--require-pass", action="store_true", help="exit 2 if the preregistered promotion gate fails")
    parser.add_argument("--no-export", action="store_true", help="screen only; do not write a GeoTIFF")
    parser.add_argument("--export-experimental", action="store_true", help="write a unique, explicitly non-slot-eligible TIF even if the proxy gate fails")
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
    if not incumbent_report.get("gate", {}).get("passed") or incumbent_config is None:
        raise SystemExit("the registered H35-01 incumbent report is missing or failed")
    if incumbent_config.get("design_id") != fixed["incumbent_design_id"]:
        raise SystemExit("incumbent ID differs from the preregistered H35-04 comparator")

    configs = mixed_latin_hypercube(
        int(spec["n_designs"]), numeric, spec["categorical_factors"],
        seed=int(spec["seed"]), prefix="h35-04", fixed=fixed,
    )
    assert_latin_stratified(configs, numeric)
    if len({row["design_id"] for row in configs}) != len(configs):
        raise SystemExit("duplicate LHS configuration IDs")

    inputs = read_inputs(ROOT / args.features, ROOT / args.labels, ROOT / args.template, read_bands=READ_BANDS)
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
            "H35-01/H35-02/H35-03 previously reported spatial summaries over these known catalogue labels. "
            "Nested outer tiles exclude their own labels from their own configuration selection, but this is exploratory reuse, not independent confirmation or validation against newly identified private faults."
        ),
    )

    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%S%fZ")
    run_id = f"h35-04-{stamp}-{str(result.report['selected_design_id']).rsplit('-', 1)[-1]}"
    report_dir, download_dir = ROOT / args.reports, ROOT / args.downloads
    report_dir.mkdir(parents=True, exist_ok=True)
    download_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{run_id}.json"
    design_csv = report_dir / f"{run_id}-design.csv"
    if report_path.exists() or design_csv.exists():
        raise FileExistsError(f"refusing to overwrite existing run {run_id}")
    with design_csv.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(configs[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(configs)

    report: dict[str, Any] = {
        **result.report,
        "hypothesis_id": "H35-04",
        "run_id": run_id,
        "generated_utc": now.isoformat(timespec="seconds"),
        "design_spec": str(design_path.relative_to(ROOT)),
        "design_seed": int(spec["seed"]),
        "design_csv": str(design_csv.relative_to(ROOT)),
        "promotion_rule": gate_spec,
        "incumbent_report": str(incumbent_path.relative_to(ROOT)),
        "input_provenance": {
            **inputs.metadata,
            "provenance_class": "owner-maintained public mirror; pinned hashes; not organizer-authenticated",
            "official_data_tab_requires_login": True,
        },
        "organizer_score": None,
        "public_score": None,
        "competition_slot_used": False,
    }
    report["gate"]["slot_eligible"] = False
    report["gate"]["slot_note"] = (
        "This spatial proxy never spends a competition slot. The current owner mirror is not organizer-authenticated, "
        "the holdout labels are known catalogue faults rather than the hidden new-fault target, and this geography was previously exposed."
    )

    passed = bool(report["gate"]["passed"])
    export = not args.no_export and (passed or args.export_experimental)
    tif_path: Path | None = None
    if export:
        chosen = dict(report["selected_config"])
        surface, diagnostics = candidate_surface(
            inputs.features, inputs.domain, chosen, pixel_size_m=float(inputs.metadata["pixel_size_m"])
        )
        # Avoid fitting the public catalogue itself into the exported ranking,
        # but keep the complete official sample footprint finite (zeros on known
        # catalogue pixels). NaN is reserved for cells outside the template.
        allowed = inputs.domain & (inputs.labels != 1) & np.isfinite(surface) & (surface > 0.0)
        requested = int(round(float(chosen["prediction_fraction"]) * int(inputs.domain.sum())))
        prediction, emitted = _top_k_mask(surface, allowed, requested)
        if emitted < 1:
            raise RuntimeError("selected H35-04 configuration emitted no in-domain pixels")
        audit = scan_downloads(prediction, inputs.domain, sorted(download_dir.glob("*.tif")))
        report["duplicate_audit"] = audit
        report["selected_surface_diagnostics"] = diagnostics
        if not audit["unique_within_local_downloads"]:
            raise RuntimeError("refusing to export an exact prediction-array duplicate")
        suffix = str(chosen["design_id"]).rsplit("-", 1)[-1]
        filename = f"gemsdoe35-h35-04-{suffix}-{stamp}-candidate.tif"
        tif_path = download_dir / filename
        note = (
            f"GEMSDOE35 H35-04 cross-physics LHS {chosen['design_id']}; "
            f"proxy gate {'passed' if passed else 'FAILED'}; unverified owner mirror; not organizer-scored."
        )
        if len(note) > 200:
            raise RuntimeError(f"DrivenData note exceeds 200 characters ({len(note)})")
        receipt = write_submission(
            tif_path, prediction, inputs.domain, inputs.profile,
            tags={
                "HYPOTHESIS_ID": "H35-04",
                "CONFIG_ID": str(chosen["design_id"]),
                "LOCAL_PROXY_GATE": "passed" if passed else "failed_experimental_only",
                "COMPETITION_SLOT_ELIGIBLE": "false",
                "PUBLIC_SCORE": "none",
            },
        )
        report["submission"] = {
            **receipt,
            "submission_name": f"GEMSDOE35-H35-04-{suffix}-{stamp}",
            "submission_note": note,
            "status": "experimental unique local artifact; NOT slot-eligible; no organizer score",
            "prediction_array_sha256": audit["candidate_prediction_array_sha256"],
            "positive_pixels": int(emitted),
        }
        report["final_candidate_emitted_pixels"] = int(emitted)
        report["artifact_status"] = (
            "unique experimental TIF emitted despite failed local proxy gate; NOT slot-eligible"
            if not passed
            else "gate passed; TIF written as a local candidate only; no automatic submission"
        )
        report["candidate_file"] = str(tif_path.relative_to(ROOT))
    else:
        report["submission"] = None
        report["candidate_file"] = None
        report["artifact_status"] = "no TIF emitted: screen-only mode or failed promotion gate without --export-experimental"

    write_json(report_path, report)
    latest = {
        "run_id": run_id,
        "report": str(report_path.relative_to(ROOT)),
        "gate_passed": passed,
        "slot_eligible": False,
        "tif": None if tif_path is None else str(tif_path.relative_to(ROOT)),
        "unique_within_local_downloads": None if tif_path is None else report["duplicate_audit"]["unique_within_local_downloads"],
    }
    write_json(report_dir / "h35-04-latest.json", latest)
    write_json(ROOT / "docs/evidence/h35-04-latest.json", report)
    if tif_path is not None:
        write_json(report_dir / "latest.json", latest)
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
