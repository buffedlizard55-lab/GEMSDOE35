#!/usr/bin/env python3
"""Screen preregistered H35-02 strain-discontinuity LHS challengers.

The NW quadrant is a reused comparison block (it has already been examined for
H35-01), not independent confirmation. A new GeoTIFF is exported only when the
predeclared development, proxy-baseline, and exact incumbent comparisons pass.
No competition submission is made by this script.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe35.design import mixed_latin_hypercube  # noqa: E402
from gemsdoe35.io import FEATURE_BANDS, read_inputs, write_json, write_submission  # noqa: E402
from gemsdoe35.validation import run_nested_screen  # noqa: E402


READ_BANDS = {
    "rtp": FEATURE_BANDS["rtp"],
    "tmi": FEATURE_BANDS["tmi"],
    "tmi_hg": FEATURE_BANDS["tmi_hg"],
    "depth_to_base_surf": FEATURE_BANDS["depth_to_base_surf"],
    "iso_grav_anom_hg": FEATURE_BANDS["iso_grav_anom_hg"],
    "det_elev_slope": FEATURE_BANDS["det_elev_slope"],
    "geod_2ndinv": FEATURE_BANDS["geod_2ndinv"],
    "geod_shearrate": FEATURE_BANDS["geod_shearrate"],
    "geod_dilaterate": FEATURE_BANDS["geod_dilaterate"],
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", default="data/raw/training_features.tif")
    parser.add_argument("--labels", default="data/raw/labels.tif")
    parser.add_argument("--template", default="data/raw/sample_submission.tif")
    parser.add_argument("--design", default="configs/h35-02-lhs.json")
    parser.add_argument("--incumbent-report", default=None)
    parser.add_argument("--reports", default="reports")
    parser.add_argument("--downloads", default="docs/downloads")
    parser.add_argument("--require-pass", action="store_true", help="exit 2 if any promotion gate fails")
    parser.add_argument("--no-export", action="store_true", help="screen only, never write a TIFF")
    args = parser.parse_args()

    design_path = ROOT / args.design
    design_spec = json.loads(design_path.read_text(encoding="utf-8"))
    fixed = dict(design_spec["fixed_factors"])
    incumbent_path = ROOT / (args.incumbent_report or fixed["incumbent_report"])
    incumbent_report = json.loads(incumbent_path.read_text(encoding="utf-8"))
    if not incumbent_report.get("gate", {}).get("passed"):
        raise SystemExit(f"incumbent report did not pass its local gate: {incumbent_path}")
    incumbent_config = incumbent_report.get("selected_config")
    incumbent_holdout = incumbent_report.get("final_holdout", {})
    if not isinstance(incumbent_config, dict) or not incumbent_config.get("design_id"):
        raise SystemExit("incumbent report has no selected configuration")
    if incumbent_config["design_id"] != fixed["incumbent_design_id"]:
        raise SystemExit(
            f"registered incumbent {fixed['incumbent_design_id']} does not match report "
            f"{incumbent_config['design_id']}"
        )
    if not incumbent_holdout.get("candidate", {}).get("score"):
        raise SystemExit("incumbent report has no scored final holdout candidate")

    numeric = {key: tuple(value) for key, value in design_spec["numeric_factors"].items()}
    configs = mixed_latin_hypercube(
        int(design_spec["n_designs"]),
        numeric,
        design_spec["categorical_factors"],
        seed=int(design_spec["seed"]),
        prefix=str(design_spec["hypothesis_id"]).lower(),
        fixed=fixed,
    )
    inputs = read_inputs(
        ROOT / args.features,
        ROOT / args.labels,
        ROOT / args.template,
        read_bands=READ_BANDS,
    )
    result = run_nested_screen(
        inputs.features,
        inputs.labels,
        inputs.domain,
        configs,
        pixel_size_m=float(inputs.metadata["pixel_size_m"]),
        spatial_margin_px=int(fixed["spatial_margin_px"]),
        incumbent_config=incumbent_config,
        holdout_reuse_note=(
            "NW was used once to screen H35-01 and is reused here as a paired challenger block. "
            "This comparison is not an untouched independent confirmation; future promotion must "
            "use fresh outer spatial blocks or another preregistered geography."
        ),
    )

    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    generated = datetime.now(timezone.utc).isoformat(timespec="seconds")
    selected_id = str(result.report["selected_design_id"])
    suffix = selected_id.rsplit("-", 1)[-1]
    run_id = f"h35-02-{now}-{suffix}"
    report_dir = ROOT / args.reports
    download_dir = ROOT / args.downloads
    report_dir.mkdir(parents=True, exist_ok=True)
    incumbent_submission = incumbent_report.get("submission") or {}
    report = {
        **result.report,
        "run_id": run_id,
        "generated_utc": generated,
        "hypothesis_register": "docs/hypotheses.md#next-untested-batch-registered-before-implementation-2026-10-04-utc",
        "design_spec": str(design_path.relative_to(ROOT)),
        "design_seed": int(design_spec["seed"]),
        "incumbent_reference": {
            "hypothesis_id": "H35-01",
            "report": str(incumbent_path.relative_to(ROOT)) if incumbent_path.is_relative_to(ROOT) else str(incumbent_path),
            "design_id": incumbent_config["design_id"],
            "source_config_prediction_fraction": float(incumbent_config["prediction_fraction"]),
            "source_report_nw": {
                "prediction_fraction": float(incumbent_config["prediction_fraction"]),
                "emitted_pixels": int(incumbent_holdout.get("emitted_pixels_candidate", 0)),
                "dti": float(incumbent_holdout["candidate"]["score"]),
                "comparison_note": "H35-01's archived result at its own smaller emission fraction; not used for the H35-02 promotion comparison",
            },
            "rescored_nw_at_challenger_budget": {
                "prediction_fraction": float(result.report["selected_config"]["prediction_fraction"]),
                "emitted_pixels": int(result.report["incumbent_holdout"]["emitted_pixels_candidate"]),
                "dti": float(result.report["incumbent_holdout"]["candidate"]["score"]),
                "budget_equal_to_challenger": bool(
                    result.report.get("incumbent_budget_comparison", {}).get("equal_emitted_mass_all_arms", False)
                ),
            },
            "candidate_sha256": incumbent_submission.get("sha256"),
        },
        "input_provenance": {
            **inputs.metadata,
            "provenance_class": "public owner-maintained mirror; pinned file hashes match; not organizer-authenticated",
            "official_data_tab_requires_login": True,
        },
        "public_score": None,
        "organizer_score": None,
    }
    design_path_out = report_dir / f"{run_id}-design.csv"
    with design_path_out.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(configs[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(configs)
    report["design_csv"] = str(design_path_out.relative_to(ROOT))

    passed = bool(report["gate"]["passed"])
    output_path: Path | None = None
    if passed and result.prediction is not None and not args.no_export:
        download_dir.mkdir(parents=True, exist_ok=True)
        filename = f"gemsdoe35-h35-02-{suffix}-{now}-candidate.tif"
        output_path = download_dir / filename
        if output_path.exists():
            output_path = download_dir / f"gemsdoe35-h35-02-{suffix}-{now}-{uuid.uuid4().hex[:6]}-candidate.tif"
        incumbent_nw = report["incumbent_holdout"]["candidate"]["score"]
        candidate_nw = report["final_holdout"]["candidate"]["score"]
        note = (
            f"GEMSDOE35 H35-02 mixed LHS {selected_id}; reused-NW proxy DTI "
            f"{candidate_nw:.4f} vs H35-01 {incumbent_nw:.4f}; owner mirror unverified; not organizer-scored."
        )
        if len(note) > 200:
            raise RuntimeError(f"submission note exceeds 200 characters ({len(note)})")
        receipt = write_submission(
            output_path,
            result.prediction,
            inputs.domain,
            inputs.profile,
            tags={
                "HYPOTHESIS_ID": "H35-02",
                "CONFIG_ID": selected_id,
                "LOCAL_HOLDOUT": "passed_reused_NW_block",
                "PUBLIC_SCORE": "none",
            },
        )
        report["submission"] = {
            **receipt,
            "submission_name": f"GEMSDOE35-H35-02-{suffix}",
            "submission_note": note,
            "status": "local proxy challenger only; NW block reused; no organizer score",
        }
        report["result"] = "LOCAL CHALLENGER PASSED: H35-02 exceeds H35-01 on the reused NW proxy; not independently confirmed or organizer-scored"
    else:
        report["submission"] = None
        if not passed:
            report["result"] = "NO TIFF GENERATED: H35-02 did not beat every predeclared local promotion gate"
        else:
            report["result"] = "SCREEN PASSED (--no-export): no GeoTIFF written"

    report_path = report_dir / f"{run_id}.json"
    write_json(report_path, report)
    pointer = {
        "run_id": run_id,
        "report": str(report_path.relative_to(ROOT)),
        "gate_passed": passed,
        "beats_current_incumbent_on_reused_NW": report["gate"].get("beats_incumbent"),
        "incumbent_budget_comparison": report.get("incumbent_budget_comparison"),
        "challenger_nw_dti": report.get("final_holdout", {}).get("candidate", {}).get("score"),
        "incumbent_nw_dti_at_challenger_budget": report.get("incumbent_holdout", {}).get("candidate", {}).get("score"),
        "tif": str(output_path.relative_to(ROOT)) if output_path else None,
    }
    write_json(report_dir / "h35-02-latest.json", pointer)
    write_json(ROOT / "docs/evidence/h35-02-latest.json", report)
    if passed and output_path is not None:
        write_json(report_dir / "latest.json", pointer)
        write_json(ROOT / "docs/evidence/latest-experiment.json", report)
        print(f"H35-02 passed the local challenger gate; candidate TIFF: {output_path.relative_to(ROOT)}")
    else:
        print("H35-02 produced no new TIFF; the current H35-01 download remains unchanged.")
    print(f"Report: {report_path.relative_to(ROOT)}")
    if args.require_pass and not passed:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
