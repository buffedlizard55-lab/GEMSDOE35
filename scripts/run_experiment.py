#!/usr/bin/env python3
"""Run the H35-01 mixed-LHS experiment and only export after its local gate."""
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
from gemsdoe35.io import read_inputs, write_json, write_submission  # noqa: E402
from gemsdoe35.validation import run_nested_screen  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", default="data/raw/training_features.tif")
    parser.add_argument("--labels", default="data/raw/labels.tif")
    parser.add_argument("--template", default="data/raw/sample_submission.tif")
    parser.add_argument("--design", default="configs/h35-01-lhs.json")
    parser.add_argument("--reports", default="reports")
    parser.add_argument("--downloads", default="docs/downloads")
    parser.add_argument("--require-pass", action="store_true", help="exit 2 if the local holdout gate fails")
    parser.add_argument("--no-export", action="store_true", help="run validation but do not write a TIFF even if it passes")
    args = parser.parse_args()

    design_path = ROOT / args.design
    design_spec = json.loads(design_path.read_text(encoding="utf-8"))
    numeric = {key: tuple(value) for key, value in design_spec["numeric_factors"].items()}
    configs = mixed_latin_hypercube(
        int(design_spec["n_designs"]),
        numeric,
        design_spec["categorical_factors"],
        seed=int(design_spec["seed"]),
        prefix="h35-01",
        fixed={
            "catalogue_mask": design_spec["fixed_factors"]["catalogue_mask"],
            "feature_detector": design_spec["fixed_factors"]["feature_detector"],
            "continuation_levels": int(design_spec["fixed_factors"]["continuation_levels"]),
        },
    )

    inputs = read_inputs(
        ROOT / args.features,
        ROOT / args.labels,
        ROOT / args.template,
    )
    result = run_nested_screen(
        inputs.features,
        inputs.labels,
        inputs.domain,
        configs,
        pixel_size_m=float(inputs.metadata["pixel_size_m"]),
        spatial_margin_px=int(design_spec["fixed_factors"]["spatial_margin_px"]),
    )
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_dir = ROOT / args.reports
    download_dir = ROOT / args.downloads
    report_dir.mkdir(parents=True, exist_ok=True)
    gate_passed = bool(result.report["gate"]["passed"])
    selected_id = str(result.report["selected_design_id"])
    run_id = f"h35-01-{now}-{selected_id.rsplit('-', 1)[-1]}"
    report = {
        **result.report,
        "run_id": run_id,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "hypothesis_register": "docs/hypotheses.md#rank-1",
        "design_spec": str(design_path.relative_to(ROOT)),
        "design_seed": int(design_spec["seed"]),
        "input_provenance": {
            **inputs.metadata,
            "provenance_class": "owner-supplied mirror; SHA-256 pinned; not organizer-authenticated",
            "official_data_tab_requires_login": True,
        },
        "public_score": None,
        "organizer_score": None,
    }
    csv_path = report_dir / f"{run_id}-design.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(configs[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(configs)
    report["design_csv"] = str(csv_path.relative_to(ROOT))
    report_path = report_dir / f"{run_id}.json"
    write_json(report_path, report)
    write_json(report_dir / "latest.json", {"run_id": run_id, "report": str(report_path.relative_to(ROOT)), "gate_passed": gate_passed})

    if gate_passed and result.prediction is not None and not args.no_export:
        download_dir.mkdir(parents=True, exist_ok=True)
        filename = f"gemsdoe35-h35-01-{selected_id.rsplit('-', 1)[-1]}-{now}-candidate.tif"
        output = download_dir / filename
        if output.exists():
            output = download_dir / f"gemsdoe35-h35-01-{selected_id.rsplit('-', 1)[-1]}-{now}-{uuid.uuid4().hex[:6]}-candidate.tif"
        outer = report["final_holdout"]
        note = (
            f"GEMSDOE35 H35-01 LHS {selected_id}; NW blocked proxy DTI delta "
            f"{float(outer['delta_dti']):+.4f} vs tmi_hg; owner mirror unverified; not organizer-scored."
        )
        if len(note) > 200:
            raise RuntimeError(f"submission note too long ({len(note)} chars)")
        raster_receipt = write_submission(
            output,
            result.prediction,
            inputs.domain,
            inputs.profile,
            tags={
                "HYPOTHESIS_ID": "H35-01",
                "CONFIG_ID": selected_id,
                "LOCAL_HOLDOUT": "passed",
                "PUBLIC_SCORE": "none",
            },
        )
        report["submission"] = {
            **raster_receipt,
            "submission_name": f"GEMSDOE35-H35-01-{selected_id.rsplit('-', 1)[-1]}",
            "submission_note": note,
            "status": "candidate only; no organizer score; use only after a human reviews the proxy caveat and rules",
        }
        write_json(report_path, report)
        write_json(report_dir / "latest.json", {"run_id": run_id, "report": str(report_path.relative_to(ROOT)), "gate_passed": True, "tif": str(output.relative_to(ROOT))})
        print(f"HOLDOUT GATE PASSED on the specified local proxy. Candidate TIFF: {output.relative_to(ROOT)}")
    else:
        report["submission"] = None
        report["result"] = "NO TIFF GENERATED: the predeclared local holdout gate did not pass" if not gate_passed else "validation only (--no-export)"
        write_json(report_path, report)
        write_json(report_dir / "latest.json", {"run_id": run_id, "report": str(report_path.relative_to(ROOT)), "gate_passed": gate_passed, "tif": None})
        print("No submission TIFF generated: local holdout gate did not pass (or --no-export was set).")
    # Keep a site-visible copy because GitHub Pages serves only docs/.
    write_json(ROOT / "docs/evidence/latest-experiment.json", report)
    print(f"Report: {report_path.relative_to(ROOT)}")
    if args.require_pass and not gate_passed:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
