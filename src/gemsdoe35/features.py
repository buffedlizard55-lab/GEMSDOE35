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


def magnetic_low_halo_surface(
    bands: Mapping[str, np.ndarray],
    domain: np.ndarray,
    config: Mapping[str, Any],
    *,
    pixel_size_m: float = 100.0,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Build H35-03's magnetic-low centerline and paired-flank ranking surface.

    A candidate is a positive local-low residual (Gaussian neighborhood mean
    minus the magnetic field) whose flank geometry is supported by positive
    transverse Hessian curvature and line anisotropy. Supplied shallow
    conductance and isostatic-gravity horizontal gradient enter only as
    registered corroboration weights. This is a physical hypothesis ranking,
    not a calibrated probability or proof of a fault.
    """
    if pixel_size_m <= 0 or not np.isfinite(pixel_size_m):
        raise ValueError("pixel_size_m must be finite and positive")
    source = str(config["magnetic_source"])
    if source not in {"mag_anom", "rtp", "tmi"}:
        raise ValueError(f"unsupported magnetic_source {source!r}")
    required = (source, "cond_surf", "iso_grav_anom_hg")
    missing = [name for name in required if name not in bands]
    if missing:
        raise ValueError(f"missing H35-03 input band(s): {missing}")
    if any(np.asarray(bands[name]).shape != domain.shape for name in required):
        raise ValueError("H35-03 feature band shapes must match the domain")

    max_scale_m = float(config["max_scale_m"])
    if not np.isfinite(max_scale_m) or max_scale_m <= 0.0:
        raise ValueError("max_scale_m must be finite and positive")
    n_scales = int(config.get("n_scales", 3))
    if n_scales < 2:
        raise ValueError("n_scales must be at least two")
    flank_weight = float(config["flank_curvature_weight"])
    cond_weight = float(config["conductance_weight"])
    gravity_weight = float(config["gravity_edge_weight"])
    if not 0.0 <= flank_weight <= 1.0:
        raise ValueError("flank_curvature_weight must be in [0,1]")
    if not 0.0 <= cond_weight <= 1.0 or not 0.0 <= gravity_weight <= 1.0:
        raise ValueError("corroboration weights must be in [0,1]")

    magnetic = _fill_nearest(np.asarray(bands[source], dtype=np.float32), domain)
    halo_sum = np.zeros(domain.shape, dtype=np.float32)
    line_sum = np.zeros(domain.shape, dtype=np.float32)
    scale_levels_m = np.linspace(max_scale_m / n_scales, max_scale_m, n_scales).tolist()
    eps = np.finfo(np.float32).eps
    for sigma_m in scale_levels_m:
        sigma_px = float(sigma_m / pixel_size_m)
        local_mean = ndimage.gaussian_filter(magnetic, sigma=sigma_px, mode="reflect")
        local_low = np.maximum(local_mean - magnetic, 0.0)
        low_unit = _robust_unit(local_low, domain)

        # Gaussian scale-normalized Hessian. The positive dominant eigenvalue
        # selects a magnetic trough; eigenvalue anisotropy favours a line-like
        # centre between two flanks over a point-like low.
        scale_factor = sigma_m * sigma_m
        hxx = ndimage.gaussian_filter(
            magnetic, sigma=sigma_px, order=(0, 2), mode="reflect"
        ) * (scale_factor / (pixel_size_m * pixel_size_m))
        hyy = ndimage.gaussian_filter(
            magnetic, sigma=sigma_px, order=(2, 0), mode="reflect"
        ) * (scale_factor / (pixel_size_m * pixel_size_m))
        hxy = ndimage.gaussian_filter(
            magnetic, sigma=sigma_px, order=(1, 1), mode="reflect"
        ) * (scale_factor / (pixel_size_m * pixel_size_m))
        trace = hxx + hyy
        discriminant = np.sqrt(np.maximum((hxx - hyy) ** 2 + 4.0 * hxy * hxy, 0.0))
        eigen_plus = 0.5 * (trace + discriminant)
        eigen_minus = 0.5 * (trace - discriminant)
        plus_dominant = np.abs(eigen_plus) >= np.abs(eigen_minus)
        normal_curvature = np.where(plus_dominant, eigen_plus, eigen_minus)
        tangent_curvature = np.where(plus_dominant, eigen_minus, eigen_plus)
        positive_trough_curvature = np.maximum(normal_curvature, 0.0)
        anisotropy = np.clip(
            1.0 - np.abs(tangent_curvature) / (np.abs(normal_curvature) + eps),
            0.0,
            1.0,
        )
        line_unit = _robust_unit(positive_trough_curvature * anisotropy, domain)
        halo_sum += low_unit
        line_sum += line_unit
        del local_mean, local_low, low_unit
        del hxx, hyy, hxy, trace, discriminant, eigen_plus, eigen_minus
        del plus_dominant, normal_curvature, tangent_curvature
        del positive_trough_curvature, anisotropy, line_unit

    mean_low = halo_sum / float(n_scales)
    mean_line = line_sum / float(n_scales)
    magnetic_halo = mean_low * ((1.0 - flank_weight) + flank_weight * mean_line)
    conductance = _robust_unit(np.asarray(bands["cond_surf"], dtype=np.float32), domain)
    gravity_edge = _robust_unit(
        np.asarray(bands["iso_grav_anom_hg"], dtype=np.float32), domain
    )
    score = (
        magnetic_halo
        * (1.0 + cond_weight * conductance)
        * (1.0 + gravity_weight * gravity_edge)
    ).astype(np.float32, copy=False)
    score[~domain] = 0.0
    diagnostics = {
        "method": "magnetic_low_flank_curvature_halo",
        "magnetic_source": source,
        "scale_levels_m": scale_levels_m,
        "median_magnetic_low_valid": float(np.median(mean_low[domain])),
        "p95_magnetic_low_valid": float(np.quantile(mean_low[domain], 0.95)),
        "median_flank_line_score_valid": float(np.median(mean_line[domain])),
        "p95_flank_line_score_valid": float(np.quantile(mean_line[domain], 0.95)),
        "config": dict(config),
    }
    del magnetic, halo_sum, line_sum, mean_low, mean_line, magnetic_halo
    del conductance, gravity_edge
    return score, diagnostics


def multiphysics_edge_concurrence_surface(
    bands: Mapping[str, np.ndarray],
    domain: np.ndarray,
    config: Mapping[str, Any],
    *,
    pixel_size_m: float = 100.0,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Rank co-located, directionally concordant magnetic/gravity/strain edges.

    This is a falsifiable cross-physics screening transform, not a fault
    classifier or calibrated probability. It combines multi-scale Gaussian
    derivative magnitudes from one magnetic anomaly, isostatic gravity anomaly,
    and geodetic shear-rate layers. The axial orientation term rewards shared
    edge-normal direction (orientation modulo 180 degrees).
    """
    if pixel_size_m <= 0.0 or not np.isfinite(pixel_size_m):
        raise ValueError("pixel_size_m must be finite and positive")
    magnetic_source = str(config["magnetic_source"])
    if magnetic_source not in {"mag_anom", "rtp"}:
        raise ValueError(f"unsupported magnetic_source {magnetic_source!r}")
    names = (magnetic_source, "iso_grav_anom", "geod_shearrate")
    missing = [name for name in names if name not in bands]
    if missing:
        raise ValueError(f"missing cross-physics edge band(s): {missing}")
    for name in names:
        if np.asarray(bands[name]).shape != domain.shape:
            raise ValueError(f"band {name!r} shape does not match the scoring domain")

    max_scale_m = float(config["max_scale_m"])
    orientation_power = float(config["orientation_power"])
    balance = float(config["multiphysics_balance"])
    n_scales = int(config.get("smoothing_scales", 3))
    if not np.isfinite(max_scale_m) or max_scale_m <= 0.0:
        raise ValueError("max_scale_m must be finite and positive")
    if not np.isfinite(orientation_power) or orientation_power < 0.0:
        raise ValueError("orientation_power must be finite and nonnegative")
    if not np.isfinite(balance) or not 0.0 <= balance <= 1.0:
        raise ValueError("multiphysics_balance must be in [0,1]")
    if n_scales < 2:
        raise ValueError("smoothing_scales must be at least two")

    sigma_levels_m = np.linspace(max_scale_m / n_scales, max_scale_m, n_scales)
    family_strengths: list[np.ndarray] = []
    orientation_x = np.zeros(domain.shape, dtype=np.float32)
    orientation_y = np.zeros(domain.shape, dtype=np.float32)
    orientation_weight = np.zeros(domain.shape, dtype=np.float32)
    for name in names:
        raw = np.asarray(bands[name], dtype=np.float32)
        filled = _fill_nearest(raw, domain)
        strength_sum = np.zeros(domain.shape, dtype=np.float32)
        for sigma_m in sigma_levels_m:
            sigma_px = float(sigma_m / pixel_size_m)
            gx = ndimage.gaussian_filter(filled, sigma=sigma_px, order=(0, 1), mode="reflect") / pixel_size_m
            gy = ndimage.gaussian_filter(filled, sigma=sigma_px, order=(1, 0), mode="reflect") / pixel_size_m
            magnitude = np.hypot(gx, gy).astype(np.float32, copy=False)
            # Scale-wise robust normalization prevents units and amplitudes of
            # disparate geophysical layers from dominating the ensemble.
            unit = _robust_unit(magnitude, domain)
            strength_sum += unit
            denominator = gx * gx + gy * gy + np.finfo(np.float32).eps
            axial_cos = (gx * gx - gy * gy) / denominator
            axial_sin = (2.0 * gx * gy) / denominator
            orientation_x += unit * axial_cos
            orientation_y += unit * axial_sin
            orientation_weight += unit
            del gx, gy, magnitude, unit, denominator, axial_cos, axial_sin
        family_strengths.append(strength_sum / float(n_scales))
        del filled, strength_sum

    stack = np.stack(family_strengths, axis=0)
    strongest = np.max(stack, axis=0)
    # Geometric concurrence suppresses a one-layer edge; the preregistered
    # balance factor controls interpolation toward that stricter criterion.
    concurrence = np.exp(np.mean(np.log(np.maximum(stack, 1.0e-6)), axis=0)).astype(np.float32)
    consensus = np.zeros(domain.shape, dtype=np.float32)
    active = orientation_weight > 0.0
    consensus[active] = np.clip(
        np.hypot(orientation_x[active], orientation_y[active])
        / (orientation_weight[active] + np.finfo(np.float32).eps),
        0.0,
        1.0,
    )
    score = ((1.0 - balance) * strongest + balance * concurrence)
    score *= np.power(consensus, orientation_power).astype(np.float32, copy=False)
    score[~domain] = 0.0
    diagnostics = {
        "method": "multiphysics_edge_concurrence",
        "magnetic_source": magnetic_source,
        "other_edge_families": ["iso_grav_anom", "geod_shearrate"],
        "scale_levels_m": [float(value) for value in sigma_levels_m],
        "median_orientation_consensus_valid": float(np.median(consensus[domain])),
        "p95_orientation_consensus_valid": float(np.quantile(consensus[domain], 0.95)),
        "median_score_valid": float(np.median(score[domain])),
        "p95_score_valid": float(np.quantile(score[domain], 0.95)),
        "config": dict(config),
    }
    del stack, strongest, concurrence, consensus, family_strengths
    del orientation_x, orientation_y, orientation_weight
    return score.astype(np.float32, copy=False), diagnostics

def seismicity_ridge_surface(
    bands: Mapping[str, np.ndarray],
    domain: np.ndarray,
    config: Mapping[str, Any],
    *,
    pixel_size_m: float = 100.0,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Build H35-05's seismicity-ridge / earthquake-distance-trough surface.

    The detector tests whether multi-scale, line-like curvature in earthquake
    intensity/density is supported by a nearby-earthquake distance trough. The
    two surfaces may be derived from correlated catalogue products; this is a
    ranking hypothesis, not independent evidence, a fault classifier, or a
    calibrated probability. A bright density ridge has negative dominant
    transverse curvature; a trough in positive distance has positive dominant
    transverse curvature.
    """
    if pixel_size_m <= 0.0 or not np.isfinite(pixel_size_m):
        raise ValueError("pixel_size_m must be finite and positive")
    required = ("ieq_n100a15", "deq_n100a15")
    missing = [name for name in required if name not in bands]
    if missing:
        raise ValueError(f"missing H35-05 feature band(s): {missing}")
    for name in required:
        if np.asarray(bands[name]).shape != domain.shape:
            raise ValueError(f"band {name!r} shape does not match the scoring domain")

    max_scale_m = float(config["max_scale_m"])
    linearity_power = float(config["linearity_power"])
    distance_weight = float(config["distance_weight"])
    n_scales = int(config.get("smoothing_scales", 3))
    if not np.isfinite(max_scale_m) or max_scale_m <= 0.0:
        raise ValueError("max_scale_m must be finite and positive")
    if not np.isfinite(linearity_power) or linearity_power < 0.0:
        raise ValueError("linearity_power must be finite and nonnegative")
    if not np.isfinite(distance_weight) or not 0.0 <= distance_weight <= 1.0:
        raise ValueError("distance_weight must be in [0,1]")
    if n_scales < 2:
        raise ValueError("smoothing_scales must be at least two")

    density_raw = _fill_nearest(np.asarray(bands["ieq_n100a15"], dtype=np.float32), domain)
    distance_raw = _fill_nearest(np.asarray(bands["deq_n100a15"], dtype=np.float32), domain)
    # These two bands are nonnegative by their local owner-mirror descriptions.
    # Clamping protects log1p against small numerical negatives without allowing
    # the raw nodata sentinel to enter the transform (read_inputs masks it).
    density_log = np.log1p(np.maximum(density_raw, 0.0)).astype(np.float32, copy=False)
    distance_log = np.log1p(np.maximum(distance_raw, 0.0)).astype(np.float32, copy=False)
    density_activity = _robust_unit(density_log, domain)
    distance_proximity = _robust_unit(-distance_log, domain)

    def curvature_response(field: np.ndarray, *, sign: float, sigma_m: float) -> np.ndarray:
        sigma_px = float(sigma_m / pixel_size_m)
        scale_factor = sigma_m * sigma_m / (pixel_size_m * pixel_size_m)
        hxx = ndimage.gaussian_filter(
            field, sigma=sigma_px, order=(0, 2), mode="reflect"
        ) * scale_factor
        hyy = ndimage.gaussian_filter(
            field, sigma=sigma_px, order=(2, 0), mode="reflect"
        ) * scale_factor
        hxy = ndimage.gaussian_filter(
            field, sigma=sigma_px, order=(1, 1), mode="reflect"
        ) * scale_factor
        trace = hxx + hyy
        discriminant = np.sqrt(np.maximum((hxx - hyy) ** 2 + 4.0 * hxy * hxy, 0.0))
        eigen_low = 0.5 * (trace - discriminant)
        eigen_high = 0.5 * (trace + discriminant)
        high_dominant = np.abs(eigen_high) >= np.abs(eigen_low)
        dominant = np.where(high_dominant, eigen_high, eigen_low)
        tangent = np.where(high_dominant, eigen_low, eigen_high)
        epsilon = np.finfo(np.float32).eps
        line_likeness = np.clip(
            1.0 - np.abs(tangent) / (np.abs(dominant) + epsilon), 0.0, 1.0
        )
        signed_curvature = np.maximum(sign * dominant, 0.0)
        response = signed_curvature * np.power(line_likeness, linearity_power)
        response[~domain] = 0.0
        return _robust_unit(response, domain)

    density_sum = np.zeros(domain.shape, dtype=np.float32)
    distance_sum = np.zeros(domain.shape, dtype=np.float32)
    scale_levels_m = np.linspace(max_scale_m / n_scales, max_scale_m, n_scales).tolist()
    for sigma_m in scale_levels_m:
        density_ridge = curvature_response(density_log, sign=-1.0, sigma_m=sigma_m)
        distance_trough = curvature_response(distance_log, sign=1.0, sigma_m=sigma_m)
        density_sum += density_ridge * density_activity
        distance_sum += distance_trough * distance_proximity
        del density_ridge, distance_trough
    density_evidence = density_sum / float(n_scales)
    distance_evidence = distance_sum / float(n_scales)
    score = (
        (1.0 - distance_weight) * density_evidence
        + distance_weight * distance_evidence
    ).astype(np.float32, copy=False)
    score[~domain] = 0.0
    diagnostics = {
        "method": "multiscale_seismicity_density_ridge_and_distance_trough",
        "feature_layers": list(required),
        "scale_levels_m": scale_levels_m,
        "distance_weight": distance_weight,
        "linearity_power": linearity_power,
        "median_density_evidence_valid": float(np.median(density_evidence[domain])),
        "p95_density_evidence_valid": float(np.quantile(density_evidence[domain], 0.95)),
        "median_distance_evidence_valid": float(np.median(distance_evidence[domain])),
        "p95_distance_evidence_valid": float(np.quantile(distance_evidence[domain], 0.95)),
        "median_score_valid": float(np.median(score[domain])),
        "p95_score_valid": float(np.quantile(score[domain], 0.95)),
        "config": dict(config),
        "correlation_caveat": "earthquake intensity and distance layers may derive from correlated seismic catalog products",
    }
    del density_raw, distance_raw, density_log, distance_log
    del density_activity, distance_proximity, density_sum, distance_sum
    del density_evidence, distance_evidence
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
    if detector == "multiphysics_edge_concurrence":
        return multiphysics_edge_concurrence_surface(
            bands, domain, config, pixel_size_m=pixel_size_m
        )
    if detector == "seismicity_ridge_curvature":
        return seismicity_ridge_surface(
            bands, domain, config, pixel_size_m=pixel_size_m
        )
    if detector == "magnetic_low_flank_curvature_halo":
        return magnetic_low_halo_surface(
            bands, domain, config, pixel_size_m=pixel_size_m
        )
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
