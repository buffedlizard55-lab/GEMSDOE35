#!/usr/bin/env python3
"""Check official-grid inputs and write a provenance-aware preparation receipt.

This script does not bypass the DrivenData login and does not download files.
Place the competition files in data/raw (or use an authorized, verified local
copy) and run this check before any experiment.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe35.io import read_inputs, write_json  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", default="data/raw/training_features.tif")
    parser.add_argument("--labels", default="data/raw/labels.tif")
    parser.add_argument("--template", default="data/raw/sample_submission.tif")
    parser.add_argument("--receipt", default="reports/data_preparation.json")
    args = parser.parse_args()
    paths = [ROOT / args.features, ROOT / args.labels, ROOT / args.template]
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.is_file()]
    if missing:
        print("Missing competition rasters:", ", ".join(missing), file=sys.stderr)
        print(
            "The official DrivenData data tab is login-walled. Download the authorized files "
            "through your enrolled account; this tool will not request or bypass credentials.",
            file=sys.stderr,
        )
        return 2
    inputs = read_inputs(*paths)
    manifest_path = ROOT / "docs/evidence/owner-mirror-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {"files": []}
    expected = {entry["canonical"]: entry["sha256"] for entry in manifest.get("files", [])}
    actual = {
        "training_features.tif": inputs.metadata["features_sha256"],
        "labels.tif": inputs.metadata["labels_sha256"],
        "sample_submission.tif": inputs.metadata["template_sha256"],
    }
    expected = {
        "training_features.tif": expected.get("training_features.tif"),
        "labels.tif": expected.get("labels.tif"),
        "sample_submission.tif": expected.get("sample_submission.tif"),
    }
    mirror_match = len([digest for digest in expected.values() if digest]) == 3 and all(
        actual.get(name) == digest for name, digest in expected.items() if digest
    )
    receipt = {
        "status": "grid_and_footprint_checks_passed",
        "provenance_class": "matches pinned public owner-mirror hashes; not organizer-authenticated" if mirror_match else "unverified local files; no known mirror hash match",
        "provenance_warning": "A matching grid and hash do not authenticate a mirror as organizer-provided.",
        **inputs.metadata,
        "selected_bands": list(inputs.features),
    }
    out = ROOT / args.receipt
    write_json(out, receipt)
    print(f"Prepared/verified {receipt['domain_pixels']:,} footprint cells; receipt: {out.relative_to(ROOT)}")
    print("Provenance class:", receipt["provenance_class"] if "provenance_class" in receipt else "not independently determined")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
