"""H35-01: wavelength-persistent magnetic-contact screening surface.

This is a deterministic geophysical transform, not a trained fault classifier.
It uses Poisson upward continuation of RTP/TMI, checks orientation persistence,
and optionally corroborates with cover-depth and gravity-gradient contrasts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np
from scipy import ndimage


@dataclass
class MagneticPersistence:
    mean_gradient: np.ndarray
    orientation_coherence: np.ndarray
    persistence: np.ndarray
    heights_m: list[float]


def _fill_nearest(values: np.ndarray, valid: np.ndarray) -> np.ndarray:
    valid = np.asarray(valid, dtype=bool) & np.isfinite(values)
    if not valid.any():
        raise ValueError("cannot fill a feature band with no valid values")
    result = np.asarray(values, dtype=np.float32).copy()
    if valid.all():
        return result
    indices = ndimage.distance_transform_edt(~valid, return_distances=False, return_indices=True)
    result[~valid] = result[tuple(axis[~valid] for axis in indices)]
    return result


def _robust_unit(values: np.ndarray, domain: np.ndarray, *, lo_q: float = 0.05, hi_q: float = 0.95) -> np.ndarray:
    valid = np.asarray(domain, dtype=bool) & np.isfinite(values)
    if not valid.any():
        raise ValueError("no finite pixels available to normalize")
    lo, hi = np.quantile(np.asarray(values[valid], dtype=np.float64), [lo_q, hi_q])
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        return np.zeros(values.shape, dtype=np.float32)
    out = np.zeros(values.shape, dtype=np.float32)
    out[valid] = np.clip((values[valid] - lo) / (hi - lo), 0.0, 1.0).astype(np.float32)
    return out


def _poisson_gradients(
    values: np.ndarray,
    domain: np.ndarray,
    *,
    pixel_size_m: float,
    heights_m: list[float],
    pad_px: int = 48,
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Return horizontal/vertical derivatives after exact FFT Poisson continuation.

    For a potential field, upward continuation attenuates wavenumber magnitude
    |k| by exp(-h|k|). Reflection padding reduces FFT wrap-around; the caller
    also excludes the data-footprint edge during holdout scoring.
    """
    if pixel_size_m <= 0:
        raise ValueError("pixel_size_m must be positive")
    filled = _fill_nearest(values, domain)
    if pad_px > 0:
        padded = np.pad(filled, pad_width=pad_px, mode="reflect")
    else:
        padded = filled
    rows, cols = padded.shape
    transform = np.fft.rfft2(padded)
    ky = 2.0 * np.pi * np.fft.fftfreq(rows, d=pixel_size_m).astype(np.float64)
    kx = 2.0 * np.pi * np.fft.rfftfreq(cols, d=pixel_size_m).astype(np.float64)
    wave_number = np.hypot(ky[:, None], kx[None, :])
    original = (slice(pad_px, pad_px + values.shape[0]), slice(pad_px, pad_px + values.shape[1]))
    output: list[tuple[np.ndarray, np.ndarray]] = []
    for height in heights_m:
        if height < 0 or not np.isfinite(height):
            raise ValueError("upward continuation heights must be finite and nonnegative")
        attenuation = np.exp(-float(height) * wave_number)
        gx_full = np.fft.irfft2(transform * (1j * kx[None, :]) * attenuation, s=padded.shape)
        gy_full = np.fft.irfft2(transform * (1j * ky[:, None]) * attenuation, s=padded.shape)
        gx = gx_full[original].astype(np.float32, copy=False)
        gy = gy_full[original].astype(np.float32, copy=False)
        output.append((gx, gy))
        del gx_full, gy_full, attenuation
    return output


def magnetic_persistence(
    values: np.ndarray,
    domain: np.ndarray,
    *,
    pixel_size_m: float = 100.0,
    max_continuation_m: float = 600.0,
    n_levels: int = 3,
    pad_px: int = 48,
) -> MagneticPersistence:
    """Measure scale-normalized gradient strength times axial orientation agreement."""
    if n_levels < 2:
        raise ValueError("n_levels must be at least two")
    if max_continuation_m <= 0:
        raise ValueError("max_continuation_m must be positive")
    heights = np.linspace(0.0, float(max_continuation_m), num=n_levels).tolist()
    gradients = _poisson_gradients(
        values, domain, pixel_size_m=pixel_size_m, heights_m=heights, pad_px=pad_px
    )
    shape = np.asarray(values).shape
    mag_sum = np.zeros(shape, dtype=np.float32)
    orient_x_sum = np.zeros(shape, dtype=np.float32)
    orient_y_sum = np.zeros(shape, dtype=np.float32)
    for gx, gy in gradients:
        magnitude = np.hypot(gx, gy)
        scale = float(np.quantile(magnitude[domain], 0.95))
        if not np.isfinite(scale) or scale <= 0:
            normalized = np.zeros(shape, dtype=np.float32)
        else:
            normalized = np.clip(magnitude / scale, 0.0, 1.0)
        denom = magnitude * magnitude + np.finfo(np.float32).eps
        axial_cos = (gx * gx - gy * gy) / denom
        axial_sin = (2.0 * gx * gy) / denom
        weight = normalized * domain
        mag_sum += weight
        orient_x_sum += weight * axial_cos
        orient_y_sum += weight * axial_sin
        del gx, gy, magnitude, normalized, denom, axial_cos, axial_sin, weight
    mean_gradient = mag_sum / float(n_levels)
    orientation_coherence = np.zeros(shape, dtype=np.float32)
    nonzero = mag_sum > 0
    orientation_coherence[nonzero] = np.clip(
        np.hypot(orient_x_sum[nonzero], orient_y_sum[nonzero]) / mag_sum[nonzero], 0.0, 1.0
    )
    persistence = mean_gradient * orientation_coherence
    persistence[~domain] = 0.0
    mean_gradient[~domain] = 0.0
    orientation_coherence[~domain] = 0.0
    return MagneticPersistence(mean_gradient, orientation_coherence, persistence, heights)


def _gradient_magnitude(values: np.ndarray, domain: np.ndarray, pixel_size_m: float) -> np.ndarray:
    filled = _fill_nearest(values, domain)
    gy, gx = np.gradient(filled, pixel_size_m, pixel_size_m)
    magnitude = np.hypot(gx, gy).astype(np.float32)
    magnitude[~domain] = 0.0
    return magnitude


def strain_discontinuity_surface(
    bands: Mapping[str, np.ndarray],
    domain: np.ndarray,
    config: Mapping[str, Any],
    *,
    pixel_size_m: float = 100.0,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Build H35-02's multi-scale strain-boundary ranking surface.

    The signal is the spatial gradient magnitude of provided geodetic-strain
    fields, not their absolute magnitude. Gradient axes are compared as
    unoriented (180-degree) line normals across three smoothing scales. This is
    a deterministic hypothesis transform, not a calibrated fault probability.
    """
    if pixel_size_m <= 0:
        raise ValueError("pixel_size_m must be positive")
    source = str(config["strain_source"])
    sources = (
        ["geod_2ndinv", "geod_shearrate", "geod_dilaterate"]
        if source == "all_three"
        else [source]
    )
    if not sources or any(name not in {"geod_2ndinv", "geod_shearrate", "geod_dilaterate"} for name in sources):
        raise ValueError(f"unsupported strain_source {source!r}")
    if any(name not in bands for name in sources):
        raise ValueError(f"missing strain band(s): {[name for name in sources if name not in bands]}")
    max_sigma_m = float(config["max_smoothing_sigma_m"])
    if not np.isfinite(max_sigma_m) or max_sigma_m <= 0:
        raise ValueError("max_smoothing_sigma_m must be finite and positive")
    n_scales = int(config.get("n_scales", 3))
    if n_scales < 2:
        raise ValueError("n_scales must be at least two")

    source_persistence: list[np.ndarray] = []
    source_coherence: list[np.ndarray] = []
    sigma_levels_m = np.linspace(max_sigma_m / n_scales, max_sigma_m, num=n_scales).tolist()
    for name in sources:
        values = np.asarray(bands[name], dtype=np.float32)
        if values.shape != domain.shape:
            raise ValueError(f"strain band {name!r} shape does not match domain")
        filled = _fill_nearest(values, domain)
        grad_sum = np.zeros(domain.shape, dtype=np.float32)
        orient_x_sum = np.zeros(domain.shape, dtype=np.float32)
        orient_y_sum = np.zeros(domain.shape, dtype=np.float32)
        for sigma_m in sigma_levels_m:
            sigma_px = float(sigma_m / pixel_size_m)
            gx = ndimage.gaussian_filter(filled, sigma=sigma_px, order=(0, 1), mode="reflect") / pixel_size_m
            gy = ndimage.gaussian_filter(filled, sigma=sigma_px, order=(1, 0), mode="reflect") / pixel_size_m
            magnitude = np.hypot(gx, gy).astype(np.float32, copy=False)
            scale = float(np.quantile(magnitude[domain], 0.95))
            if not np.isfinite(scale) or scale <= 0:
                normalized = np.zeros(domain.shape, dtype=np.float32)
            else:
                normalized = np.clip(magnitude / scale, 0.0, 1.0)
            denom = gx * gx + gy * gy + np.finfo(np.float32).eps
            axial_cos = (gx * gx - gy * gy) / denom
            axial_sin = (2.0 * gx * gy) / denom
            weight = normalized * domain
            grad_sum += weight
            orient_x_sum += weight * axial_cos
            orient_y_sum += weight * axial_sin
            del gx, gy, magnitude, normalized, denom, axial_cos, axial_sin, weight
        mean_gradient = grad_sum / float(n_scales)
        coherence = np.zeros(domain.shape, dtype=np.float32)
        active = grad_sum > 0
        coherence[active] = np.clip(
            np.hypot(orient_x_sum[active], orient_y_sum[active]) / grad_sum[active], 0.0, 1.0
        )
        persistence = mean_gradient * coherence
        persistence[~domain] = 0.0
        coherence[~domain] = 0.0
        source_persistence.append(persistence)
        source_coherence.append(coherence)
        del filled, grad_sum, orient_x_sum, orient_y_sum, mean_gradient, active

    persistence = np.mean(np.stack(source_persistence, axis=0), axis=0, dtype=np.float32)
    coherence = np.mean(np.stack(source_coherence, axis=0), axis=0, dtype=np.float32)
    threshold = float(config["min_orientation_coherence"])
    if not np.isfinite(threshold) or not 0.0 <= threshold <= 1.0:
        raise ValueError("min_orientation_coherence must be in [0,1]")
    score = np.where(coherence >= threshold, persistence, 0.0).astype(np.float32)
    score[~domain] = 0.0
    diagnostics = {
        "method": "multiscale_strain_gradient_orientation_persistence",
        "strain_source": source,
        "smoothing_sigma_levels_m": sigma_levels_m,
        "median_persistence_valid": float(np.median(persistence[domain])),
        "p95_persistence_valid": float(np.quantile(persistence[domain], 0.95)),
        "median_orientation_coherence_valid": float(np.median(coherence[domain])),
        "config": dict(config),
    }
    return score, diagnostics


def candidate_surface(
    bands: Mapping[str, np.ndarray],
    domain: np.ndarray,
    config: Mapping[str, Any],
    *,
    pixel_size_m: float = 100.0,
    pad_px: int = 48,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Build a deterministic ranking field from a pre-registered configuration."""
    detector = str(config.get("feature_detector", "deterministic_poisson_gradient_persistence"))
    if detector == "multiscale_strain_gradient_orientation":
        return strain_discontinuity_surface(
            bands, domain, config, pixel_size_m=pixel_size_m
        )
    if detector != "deterministic_poisson_gradient_persistence":
        raise ValueError(f"unsupported feature_detector {detector!r}")
    source = str(config["magnetic_source"])
    height = float(config["max_continuation_m"])
    if source not in {"rtp", "tmi", "blend"}:
        raise ValueError(f"unsupported magnetic_source {source!r}")
    sources = ["rtp", "tmi"] if source == "blend" else [source]
    persistences: list[np.ndarray] = []
    coherences: list[np.ndarray] = []
    for name in sources:
        result = magnetic_persistence(
            bands[name], domain,
            pixel_size_m=pixel_size_m,
            max_continuation_m=height,
            n_levels=3,
            pad_px=pad_px,
        )
        persistences.append(result.persistence)
        coherences.append(result.orientation_coherence)
        del result
    mag_persist = np.mean(np.stack(persistences, axis=0), axis=0, dtype=np.float32)
    coherence = np.mean(np.stack(coherences, axis=0), axis=0, dtype=np.float32)
    coherence_threshold = float(config["min_orientation_coherence"])
    mag_persist = np.where(coherence >= coherence_threshold, mag_persist, 0.0).astype(np.float32)

    depth_edge = _robust_unit(
        _gradient_magnitude(bands["depth_to_base_surf"], domain, pixel_size_m), domain
    )
    gravity_edge = _robust_unit(bands["iso_grav_anom_hg"], domain)
    surface_slope = _robust_unit(bands["det_elev_slope"], domain)
    depth_weight = float(config["depth_edge_weight"])
    gravity_weight = float(config["gravity_edge_weight"])
    quiet_weight = float(config["quiescence_weight"])
    if any(not 0.0 <= value <= 1.0 for value in (depth_weight, gravity_weight, quiet_weight)):
        raise ValueError("corroboration weights must be in [0,1]")
    score = (
        mag_persist
        * (1.0 + depth_weight * depth_edge)
        * (1.0 + gravity_weight * gravity_edge)
        * (1.0 - quiet_weight * surface_slope)
    ).astype(np.float32)
    score[~domain] = 0.0
    diagnostics = {
        "method": "poisson_continuation_gradient_orientation_persistence",
        "magnetic_source": source,
        "continuation_heights_m": [0.0, height / 2.0, height],
        "median_persistence_valid": float(np.median(mag_persist[domain])),
        "p95_persistence_valid": float(np.quantile(mag_persist[domain], 0.95)),
        "median_orientation_coherence_valid": float(np.median(coherence[domain])),
        "config": dict(config),
    }
    return score, diagnostics


def normalize_for_ranking(values: np.ndarray, domain: np.ndarray) -> np.ndarray:
    """Robust monotone scaling for a baseline field; preserves ranking ties."""
    return _robust_unit(np.asarray(values), np.asarray(domain, dtype=bool))
