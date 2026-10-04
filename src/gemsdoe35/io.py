"""Raster loading, grid checks, provenance, and safe GeoTIFF I/O."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.crs import CRS


FEATURE_BANDS = {
    "rtp": 2,
    "tmi_hg": 3,
    "geod_2ndinv": 4,
    "iso_grav_anom_slope": 5,
    "tc": 6,
    "geod_shearrate": 7,
    "geod_dilaterate": 8,
    "tmi_vg": 9,
    "deq_n100a15": 10,
    "iso_grav_anom_vg": 11,
    "det_elev": 12,
    "iso_grav_anom": 13,
    "tmi": 14,
    "depth_to_base_surf": 15,
    "ieq_n100a15": 16,
    "cond_surf": 17,
    "iso_grav_anom_hg": 18,
    "det_elev_slope": 19,
}


@dataclass
class GEMSInputs:
    features: dict[str, np.ndarray]
    labels: np.ndarray
    domain: np.ndarray
    profile: dict[str, Any]
    metadata: dict[str, Any]


def sha256_file(path: str | Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _grid_signature(dataset: rasterio.io.DatasetReader) -> tuple[Any, ...]:
    return (
        dataset.width,
        dataset.height,
        dataset.count,
        dataset.crs,
        tuple(dataset.transform),
    )


def _assert_same_grid(reference: rasterio.io.DatasetReader, other: rasterio.io.DatasetReader, name: str) -> None:
    a = _grid_signature(reference)
    b = _grid_signature(other)
    # Count is intentionally omitted: feature/label/template rasters have distinct band counts.
    if a[:2] != b[:2] or a[3:] != b[3:]:
        raise ValueError(f"{name} grid does not exactly match the feature grid: {b!r} != {a!r}")


def read_inputs(
    features_path: str | Path,
    labels_path: str | Path,
    template_path: str | Path,
    *,
    read_bands: dict[str, int] | None = None,
) -> GEMSInputs:
    """Read selected feature bands and require matching template/label grids.

    The template is used only for georeferencing and its finite-data footprint;
    its pixel values are never used as predictions. Label and template footprints
    must agree exactly so an accidental non-zero template cannot be mistaken for
    the domain mask.
    """
    feature_names = read_bands or {
        "rtp": FEATURE_BANDS["rtp"],
        "tmi": FEATURE_BANDS["tmi"],
        "tmi_hg": FEATURE_BANDS["tmi_hg"],
        "depth_to_base_surf": FEATURE_BANDS["depth_to_base_surf"],
        "iso_grav_anom_hg": FEATURE_BANDS["iso_grav_anom_hg"],
        "det_elev_slope": FEATURE_BANDS["det_elev_slope"],
    }
    with rasterio.open(features_path) as fds, rasterio.open(labels_path) as lds, rasterio.open(template_path) as tds:
        _assert_same_grid(fds, lds, "labels")
        _assert_same_grid(fds, tds, "template")
        if fds.crs != CRS.from_epsg(32611):
            raise ValueError(f"expected EPSG:32611, got {fds.crs}")
        if not np.isclose(abs(fds.transform.a), 100.0) or not np.isclose(abs(fds.transform.e), 100.0):
            raise ValueError(f"expected 100 m pixels, got transform {fds.transform}")
        if fds.count < max(feature_names.values()):
            raise ValueError(f"feature raster has {fds.count} bands; requested band {max(feature_names.values())}")

        labels_raw = lds.read(1)
        label_nodata = lds.nodata
        if label_nodata is None:
            labels_valid = np.ones(labels_raw.shape, dtype=bool)
        else:
            labels_valid = labels_raw != label_nodata
        template_raw = tds.read(1)
        template_nodata = tds.nodata
        template_valid = np.isfinite(template_raw)
        if template_nodata is not None and np.isfinite(template_nodata):
            template_valid &= template_raw != template_nodata
        if not np.array_equal(labels_valid, template_valid):
            mismatch = int(np.count_nonzero(labels_valid != template_valid))
            raise ValueError(
                f"label and template valid-data footprints differ at {mismatch:,} cells; refusing to guess the submission mask"
            )
        if not set(np.unique(labels_raw[labels_valid]).tolist()).issubset({0, 1, 0.0, 1.0, False, True}):
            raise ValueError("labels must be binary 0/1 on their valid footprint")

        domain = labels_valid & template_valid
        labels = (labels_raw == 1) & domain
        selected: dict[str, np.ndarray] = {}
        missing_by_band: dict[str, int] = {}
        for name, band in feature_names.items():
            array = fds.read(band).astype(np.float32, copy=False)
            bad = ~np.isfinite(array)
            if fds.nodata is not None:
                if np.isnan(fds.nodata):
                    bad |= np.isnan(array)
                else:
                    bad |= array == fds.nodata
            # GeoTIFF float32 nodata sentinels are sometimes preserved in the
            # array but not recognized by third-party readers. Treat their
            # magnitude as invalid; never propagate them to derivative math.
            bad |= array < -1.0e30
            valid = domain & ~bad
            missing_by_band[name] = int(np.count_nonzero(domain & bad))
            array = array.copy()
            array[~valid] = np.nan
            selected[name] = array

        profile = fds.profile.copy()
        profile.update(count=1, dtype="float32", nodata=np.nan)
        metadata = {
            "width": int(fds.width),
            "height": int(fds.height),
            "band_count": int(fds.count),
            "crs": fds.crs.to_string() if fds.crs else None,
            "transform": list(fds.transform),
            "pixel_size_m": float(abs(fds.transform.a)),
            "domain_pixels": int(domain.sum()),
            "label_positive_pixels": int(labels.sum()),
            "feature_missing_inside_domain": missing_by_band,
            "features_file": str(features_path),
            "labels_file": str(labels_path),
            "template_file": str(template_path),
            "features_sha256": sha256_file(features_path),
            "labels_sha256": sha256_file(labels_path),
            "template_sha256": sha256_file(template_path),
            "feature_band_descriptions": {str(i + 1): d for i, d in enumerate(fds.descriptions)},
            "template_values_used": False,
            "label_template_footprints_identical": True,
        }
    return GEMSInputs(selected, labels, domain, profile, metadata)


def write_submission(
    output_path: str | Path,
    prediction: np.ndarray,
    domain: np.ndarray,
    profile: dict[str, Any],
    *,
    tags: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Write an official-format candidate, then reopen and verify written bytes."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    p = np.asarray(prediction, dtype=np.float32)
    mask = np.asarray(domain, dtype=bool)
    if p.ndim != 2 or p.shape != mask.shape:
        raise ValueError("prediction and domain must be matching 2-D arrays")
    if not np.all(np.isfinite(p[mask])):
        raise ValueError("submission contains NaN/inf inside the valid footprint")
    if np.any((p[mask] < 0.0) | (p[mask] > 1.0)):
        raise ValueError("submission values inside the footprint must be in [0, 1]")
    out_profile = profile.copy()
    out_profile.update(
        driver="GTiff",
        width=p.shape[1],
        height=p.shape[0],
        count=1,
        dtype="float32",
        crs=CRS.from_epsg(32611),
        nodata=np.nan,
        compress="deflate",
        predictor=3,
        tiled=True,
        blockxsize=256,
        blockysize=256,
    )
    data = np.full(p.shape, np.nan, dtype=np.float32)
    data[mask] = p[mask]
    with rasterio.open(out, "w", **out_profile) as dst:
        dst.write(data, 1)
        dst.set_band_description(1, "fault confidence [0,1]")
        dst.update_tags(
            AREA_OR_POINT="Area",
            GEMS_CANDIDATE="true",
            **(tags or {}),
        )
    with rasterio.open(out) as check:
        reread = check.read(1)
        valid = np.isfinite(reread)
        expected_profile = out_profile
        if check.count != 1 or check.dtypes != ("float32",):
            raise ValueError("written file is not single-band float32")
        if check.crs != CRS.from_epsg(32611):
            raise ValueError(f"written CRS is wrong: {check.crs}")
        if (check.width, check.height) != (p.shape[1], p.shape[0]):
            raise ValueError("written shape is wrong")
        if not np.array_equal(valid, mask):
            raise ValueError("written nodata footprint differs from expected mask")
        if not np.all(np.isfinite(reread[mask])) or np.any((reread[mask] < 0) | (reread[mask] > 1)):
            raise ValueError("written predictions are not finite in [0,1]")
        if check.nodata is None or not np.isnan(check.nodata):
            raise ValueError("written file must use NaN nodata outside the scoring footprint")
        if tuple(check.transform) != tuple(expected_profile["transform"]):
            raise ValueError("written geotransform differs from template")
        summary = {
            "path": str(out),
            "sha256": sha256_file(out),
            "bytes": out.stat().st_size,
            "shape": [int(p.shape[0]), int(p.shape[1])],
            "bands": int(check.count),
            "dtype": check.dtypes[0],
            "crs": check.crs.to_string(),
            "transform": list(check.transform),
            "valid_pixels": int(mask.sum()),
            "nodata_pixels": int((~mask).sum()),
            "prediction_min": float(reread[mask].min()),
            "prediction_max": float(reread[mask].max()),
            "positive_pixels": int(np.count_nonzero(reread[mask] > 0)),
            "outside_encoding": "NaN/nodata",
            "value_range_verified": True,
            "postwrite_reread_verified": True,
        }
    return summary


def write_json(path: str | Path, value: Any) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
