"""Distance-weighted Tversky Index as defined on DrivenData's problem page.

Official page: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
The implementation uses a Euclidean triangular kernel with 300 m support.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import hypot
from typing import Any

import numpy as np
from scipy import ndimage


@dataclass(frozen=True)
class DTIResult:
    score: float
    tp_weighted: float
    fp_weighted: float
    fn_weighted: float
    truth_pixels: int
    predicted_mass: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _validate_inputs(
    truth: np.ndarray,
    prediction: np.ndarray,
    valid: np.ndarray | None,
    *,
    require_probability_range: bool,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    y = np.asarray(truth)
    p = np.asarray(prediction)
    if y.shape != p.shape or y.ndim != 2:
        raise ValueError("truth and prediction must be 2-D arrays with equal shape")
    if valid is None:
        domain = np.ones(y.shape, dtype=bool)
    else:
        domain = np.asarray(valid, dtype=bool)
        if domain.shape != y.shape:
            raise ValueError("valid mask shape must match truth")
    if np.any(~np.isfinite(p[domain])):
        raise ValueError("prediction contains NaN or infinity inside the scoring domain")
    if require_probability_range and np.any((p[domain] < 0.0) | (p[domain] > 1.0)):
        lo = float(np.min(p[domain])) if domain.any() else float("nan")
        hi = float(np.max(p[domain])) if domain.any() else float("nan")
        raise ValueError(f"predicted values must be in [0, 1] inside the scoring domain; got [{lo}, {hi}]")
    p = np.where(domain, p.astype(np.float64, copy=False), 0.0)
    y = np.asarray(y, dtype=bool) & domain
    return y, p, domain


def dti(
    truth: np.ndarray,
    prediction: np.ndarray,
    valid: np.ndarray | None = None,
    *,
    pixel_size_m: float = 100.0,
    radius_m: float = 300.0,
    alpha: float = 0.2,
    beta: float = 0.8,
    epsilon: float = 1e-12,
    require_probability_range: bool = True,
) -> DTIResult:
    """Compute the official distance-weighted Tversky Index on a single grid.

    ``truth`` is interpreted as a binary mask. All cells outside ``valid`` are
    excluded, including from the false-positive mass. The probability range is
    checked rather than silently clipping values.
    """
    if pixel_size_m <= 0 or radius_m <= 0:
        raise ValueError("pixel_size_m and radius_m must be positive")
    if alpha < 0 or beta < 0 or epsilon <= 0:
        raise ValueError("alpha/beta must be nonnegative and epsilon positive")
    y, p, domain = _validate_inputs(
        truth, prediction, valid, require_probability_range=require_probability_range
    )
    truth_count = int(y.sum())
    mass = float(p[domain].sum())

    if truth_count == 0:
        tp = 0.0
        fn = 0.0
        fp = mass
    else:
        # d(x,G): nearest truth pixel. SciPy's EDT computes distance to zeros.
        dist_to_truth = ndimage.distance_transform_edt(~y, sampling=(pixel_size_m, pixel_size_m))
        nearest_kernel = np.maximum(1.0 - dist_to_truth / radius_m, 0.0)
        fp = float(np.sum(p[domain] * (1.0 - nearest_kernel[domain]), dtype=np.float64))

        # For each truth pixel g, find max_x p(x) k(d(x,g)). Since R is only
        # three 100-m pixels, evaluating the exact finite offset set is cheap.
        best = np.zeros(y.shape, dtype=np.float64)
        rows, cols = y.shape
        max_offset = int(np.ceil(radius_m / pixel_size_m))
        for dr in range(-max_offset, max_offset + 1):
            for dc in range(-max_offset, max_offset + 1):
                distance = hypot(dr * pixel_size_m, dc * pixel_size_m)
                weight = max(1.0 - distance / radius_m, 0.0)
                if weight <= 0.0:
                    continue
                tr_r0, tr_r1 = max(0, -dr), min(rows, rows - dr)
                tr_c0, tr_c1 = max(0, -dc), min(cols, cols - dc)
                if tr_r0 >= tr_r1 or tr_c0 >= tr_c1:
                    continue
                pr_r0, pr_r1 = tr_r0 + dr, tr_r1 + dr
                pr_c0, pr_c1 = tr_c0 + dc, tr_c1 + dc
                truth_view = y[tr_r0:tr_r1, tr_c0:tr_c1]
                if not truth_view.any():
                    continue
                credit = p[pr_r0:pr_r1, pr_c0:pr_c1] * weight
                best_view = best[tr_r0:tr_r1, tr_c0:tr_c1]
                np.maximum(best_view, np.where(truth_view, credit, 0.0), out=best_view)
        tp = float(best[y].sum(dtype=np.float64))
        fn = float(np.sum(1.0 - best[y], dtype=np.float64))

    denominator = tp + alpha * fp + beta * fn + epsilon
    score = float(tp / denominator) if denominator > 0 else 0.0
    return DTIResult(score, tp, fp, fn, truth_count, mass)
