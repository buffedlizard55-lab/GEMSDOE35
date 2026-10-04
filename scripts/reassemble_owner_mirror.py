#!/usr/bin/env python3
"""Reassemble the pinned public owner-mirror bridge; never bypass DrivenData auth.

This is a reproducibility fallback, not an organizer download. It fetches the
public bridge repository (or accepts a local sparse clone), verifies every
part and final file against the pinned small manifest, then writes ignored
rasters under data/raw/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINNED_MANIFEST = ROOT / "docs/evidence/owner-mirror-manifest.json"
REPOSITORY = "https://github.com/buffedlizard55-lab/GEMSDOE.git"
BRIDGE_PATH = "data/bridge"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def safe_child(root: Path, name: str) -> Path:
    if Path(name).name != name or name in {"", ".", ".."}:
        raise ValueError(f"unsafe manifest filename {name!r}")
    return root / name


def sparse_clone(cache: Path) -> Path:
    cache.mkdir(parents=True, exist_ok=True)
    target = cache / "GEMSDOE-bridge"
    if target.exists():
        shutil.rmtree(target)
    subprocess.run(
        ["git", "clone", "--depth=1", "--filter=blob:none", "--sparse", REPOSITORY, str(target)],
        check=True,
    )
    subprocess.run(["git", "-C", str(target), "sparse-checkout", "set", BRIDGE_PATH], check=True)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", help="existing clone containing data/bridge (offline/repro test option)")
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--cache-dir", default="data/cache")
    parser.add_argument("--receipt", default="reports/owner-mirror-reassembly.json")
    args = parser.parse_args()
    if not PINNED_MANIFEST.is_file():
        print(f"Pinned manifest missing: {PINNED_MANIFEST}", file=sys.stderr)
        return 2
    manifest = json.loads(PINNED_MANIFEST.read_text(encoding="utf-8"))
    temp_context = None
    try:
        if args.source_dir:
            source_root = Path(args.source_dir).resolve()
        else:
            cache = (ROOT / args.cache_dir).resolve()
            cache.mkdir(parents=True, exist_ok=True)
            temp_context = tempfile.TemporaryDirectory(prefix="gemsdoe35-bridge-", dir=cache)
            source_root = sparse_clone(Path(temp_context.name))
        bridge = source_root / BRIDGE_PATH
        if not bridge.is_dir():
            raise FileNotFoundError(f"bridge directory missing: {bridge}")
        remote_manifest_path = bridge / "manifest.json"
        remote_manifest = json.loads(remote_manifest_path.read_text(encoding="utf-8"))
        if sha256_file(remote_manifest_path) != manifest["upstream_manifest_sha256"]:
            raise ValueError("upstream bridge manifest bytes differ from the pinned SHA-256")
        if remote_manifest.get("files") != manifest["files"]:
            raise ValueError("upstream bridge file records differ from the sanitized local pin")

        raw_dir = (ROOT / args.raw_dir).resolve()
        raw_dir.mkdir(parents=True, exist_ok=True)
        receipt_files: list[dict[str, object]] = []
        for entry in manifest["files"]:
            canonical_name = str(entry["canonical"])
            target = safe_child(raw_dir, canonical_name)
            if "parts" not in entry:
                source = safe_child(bridge, str(entry["name"]))
                expected_size = int(entry["bytes"])
                expected_sha = str(entry["sha256"])
                if not source.is_file():
                    raise FileNotFoundError(source)
                actual_size = source.stat().st_size
                actual_sha = sha256_file(source)
                if actual_size != expected_size or actual_sha != expected_sha:
                    raise ValueError(f"source integrity failure for {source.name}")
                if target.exists() and target.stat().st_size == expected_size and sha256_file(target) == expected_sha:
                    action = "already_verified"
                else:
                    shutil.copyfile(source, target)
                    action = "copied_and_verified"
            else:
                part_records = entry["parts"]
                tmp_target = target.with_suffix(target.suffix + ".partial")
                digest = hashlib.sha256()
                size_total = 0
                with tmp_target.open("wb") as output:
                    for part in part_records:
                        source = safe_child(bridge, str(part["name"]))
                        if not source.is_file():
                            raise FileNotFoundError(source)
                        part_size = source.stat().st_size
                        part_sha = sha256_file(source)
                        if part_size != int(part["bytes"]) or part_sha != str(part["sha256"]):
                            raise ValueError(f"source-part integrity failure for {source.name}")
                        with source.open("rb") as inp:
                            while chunk := inp.read(8 * 1024 * 1024):
                                output.write(chunk)
                                digest.update(chunk)
                                size_total += len(chunk)
                if size_total != int(entry["bytes"]) or digest.hexdigest() != str(entry["sha256"]):
                    tmp_target.unlink(missing_ok=True)
                    raise ValueError(f"reassembled file integrity failure for {canonical_name}")
                tmp_target.replace(target)
                action = "reassembled_and_verified"
            receipt_files.append({
                "canonical": canonical_name,
                "bytes": target.stat().st_size,
                "sha256": sha256_file(target),
                "action": action,
            })
        receipt = {
            "status": "all_mirror_hashes_verified",
            "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "source_repository": REPOSITORY,
            "source_bridge_path": BRIDGE_PATH,
            "source_class": "public owner-maintained mirror; not authenticated by DrivenData",
            "official_data_tab": manifest["official_data_tab"],
            "official_data_tab_bypassed": False,
            "warning": "Matching the bridge's own pinned hashes verifies mirror integrity only; it does not prove organizer provenance or licensing. Check the official data tab/rules before external use.",
            "files": receipt_files,
        }
        receipt_path = ROOT / args.receipt
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        serialized = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        receipt_path.write_text(serialized, encoding="utf-8")
        site_receipt = ROOT / "docs/evidence/owner-mirror-reassembly.json"
        site_receipt.write_text(serialized, encoding="utf-8")
        print(json.dumps(receipt, indent=2))
        try:
            receipt_label = receipt_path.relative_to(ROOT)
        except ValueError:
            receipt_label = receipt_path
        print("Reassembly receipt:", receipt_label)
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"Reassembly failed: {exc}", file=sys.stderr)
        return 2
    finally:
        if temp_context is not None:
            temp_context.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
