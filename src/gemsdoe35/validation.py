"""Spatially separated configuration selection and a frozen final holdout."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np
from scipy import ndimage

from .features import candidate_surface, normalize_for_ranking
from .metric import dti


FINAL_HOLDOUT = "NW"
INNER_FOLDS = ("NE", "SW", "SE")


@dataclass
class ValidationOutput:
    report: dict[str, Any]
    prediction: np.ndarray | None
    selected_config: dict[str, Any] | None


def _fold_masks(shape: tuple[int, int], domain: np.ndarray, margin_px: int) -> dict[str, np.ndarray]:
    """Return evaluation cores for four contiguous quadrants.

    The margin is an erosion from each quadrant boundary, not a label/catalogue
    buffer. It prevents nearby boundary pixels from being counted in two
    spatial blocks and limits edge-context sensitivity in the feature transform.
    """
    if margin_px < 0:
        raise ValueError("spatial margin must be nonnegative")
    h, w = shape
    row_mid, col_mid = h // 2, w // 2
    bounds = {
        "NW": (0, row_mid, 0, col_mid),
        "NE": (0, row_mid, col_mid, w),
        "SW": (row_mid, h, 0, col_mid),
        "SE": (row_mid, h, col_mid, w),
    }
    core: dict[str, np.ndarray] = {}
    for name, (r0, r1, c0, c1) in bounds.items():
        cr0, cr1 = r0 + margin_px, r1 - margin_px
        cc0, cc1 = c0 + margin_px, c1 - margin_px
        if cr0 >= cr1 or cc0 >= cc1:
            raise ValueError("spatial margin leaves an empty fold")
        inside = np.zeros(shape, dtype=bool)
        inside[cr0:cr1, cc0:cc1] = True
        core[name] = inside & domain
    return core


def _top_k_mask(score: np.ndarray, allowed: np.ndarray, k: int) -> tuple[np.ndarray, int]:
    result = np.zeros(score.shape, dtype=np.float32)
    indices = np.flatnonzero(allowed & np.isfinite(score) & (score > 0))
    k = min(max(int(k), 0), len(indices))
    if k == 0:
        return result, 0
    values = score.ravel()[indices]
    partition = np.argpartition(values, len(values) - k)[len(values) - k :]
    selected = indices[partition]
    # Deterministic tie-breaking for reproducible builds.
    selected_values = score.ravel()[selected]
    order = np.lexsort((selected, -selected_values))
    selected = selected[order[:k]]
    result.ravel()[selected] = 1.0
    return result, int(k)


def _paired_fold_scores(
    candidate_score: np.ndarray,
    baseline_score: np.ndarray,
    labels: np.ndarray,
    domain: np.ndarray,
    core_masks: Mapping[str, np.ndarray],
    *,
    heldout_name: str,
    prediction_fraction: float,
    pixel_size_m: float,
) -> dict[str, Any]:
    eval_mask = core_masks[heldout_name] & domain
    available = int(eval_mask.sum())
    target_k = int(round(float(prediction_fraction) * available))
    truth = (labels == 1) & eval_mask
    if available == 0 or target_k < 1:
        return {
            "fold": heldout_name,
            "status": "insufficient_prediction_domain",
            "available_pixels": available,
            "truth_pixels": int(truth.sum()),
        }
    pred, emitted = _top_k_mask(candidate_score, eval_mask, target_k)
    baseline, baseline_emitted = _top_k_mask(baseline_score, eval_mask, target_k)
    # Both arms have the same scoring domain and target budget. If a field has
    # fewer positive scores, report and match the actual emitted mass.
    matched_k = min(emitted, baseline_emitted)
    if emitted != matched_k:
        pred, emitted = _top_k_mask(candidate_score, eval_mask, matched_k)
    if baseline_emitted != matched_k:
        baseline, baseline_emitted = _top_k_mask(baseline_score, eval_mask, matched_k)
    cand_metric = dti(truth, pred, valid=eval_mask, pixel_size_m=pixel_size_m)
    base_metric = dti(truth, baseline, valid=eval_mask, pixel_size_m=pixel_size_m)
    return {
        "fold": heldout_name,
        "status": "scored",
        "available_pixels": available,
        "requested_budget": target_k,
        "emitted_pixels_candidate": emitted,
        "emitted_pixels_baseline": baseline_emitted,
        "truth_pixels": int(truth.sum()),
        "candidate": cand_metric.as_dict(),
        "baseline": base_metric.as_dict(),
        "delta_dti": float(cand_metric.score - base_metric.score),
    }


def run_nested_screen(
    bands: Mapping[str, np.ndarray],
    labels: np.ndarray,
    domain: np.ndarray,
    configs: Sequence[Mapping[str, Any]],
    *,
    pixel_size_m: float = 100.0,
    spatial_margin_px: int = 30,
    pad_px: int = 48,
) -> ValidationOutput:
    """Select on three spatial blocks and evaluate once on frozen NW.

    H35-01 is deterministic and has no fitted model: candidate surfaces use
    feature rasters only. NE/SW/SE labels select the configuration; NW labels
    are not inspected until the selected configuration is evaluated once on
    the final holdout. Thus this is a spatial proxy on existing public catalogue
    faults, not a learned model's generalization estimate or a substitute for
    hidden newly identified faults.
    """
    y = np.asarray(labels)
    domain = np.asarray(domain, dtype=bool)
    if y.shape != domain.shape or y.ndim != 2:
        raise ValueError("labels and domain must be matching 2-D arrays")
    if not configs:
        raise ValueError("at least one LHS configuration is required")
    core = _fold_masks(y.shape, domain, spatial_margin_px)
    baseline = normalize_for_ranking(bands["tmi_hg"], domain)
    design_results: list[dict[str, Any]] = []
    selected_config: dict[str, Any] | None = None
    selected_surface: np.ndarray | None = None
    selected_diagnostics: dict[str, Any] | None = None
    best_inner_mean: float | None = None

    for raw_config in configs:
        config = dict(raw_config)
        surface, diagnostics = candidate_surface(
            bands, domain, config, pixel_size_m=pixel_size_m, pad_px=pad_px
        )
        fold_results = [
            _paired_fold_scores(
                surface,
                baseline,
                y,
                domain,
                core,
                heldout_name=fold,
                prediction_fraction=float(config["prediction_fraction"]),
                pixel_size_m=pixel_size_m,
            )
            for fold in INNER_FOLDS
        ]
        deltas = [r["delta_dti"] for r in fold_results if r["status"] == "scored"]
        inner_mean = float(np.mean(deltas)) if len(deltas) == len(INNER_FOLDS) else None
        design_results.append(
            {
                "design_id": str(config["design_id"]),
                "config": config,
                "inner_folds": fold_results,
                "inner_mean_delta_dti": inner_mean,
                "inner_positive_folds": int(sum(delta > 0 for delta in deltas)),
            }
        )
        if inner_mean is not None and (best_inner_mean is None or inner_mean > best_inner_mean):
            best_inner_mean = inner_mean
            selected_config = config
            selected_surface = surface
            selected_diagnostics = diagnostics
        else:
            del surface, diagnostics

    if selected_config is None or selected_surface is None or best_inner_mean is None:
        raise RuntimeError("no configuration had valid scores in all development folds")
    outer = _paired_fold_scores(
        selected_surface,
        baseline,
        y,
        domain,
        core,
        heldout_name=FINAL_HOLDOUT,
        prediction_fraction=float(selected_config["prediction_fraction"]),
        pixel_size_m=pixel_size_m,
    )
    selected_row = next(row for row in design_results if row["design_id"] == selected_config["design_id"])
    inner_deltas = [r["delta_dti"] for r in selected_row["inner_folds"] if r["status"] == "scored"]
    gate = (
        len(inner_deltas) == len(INNER_FOLDS)
        and all(delta > 0.0 for delta in inner_deltas)
        and outer.get("status") == "scored"
        and float(outer["delta_dti"]) > 0.0
    )
    prediction: np.ndarray | None = None
    if gate:
        # The organizer masks known catalogue pixels exactly. No buffer is
        # applied: new fault pixels may lie near known traces and nearby output
        # pixels are otherwise scored normally.
        all_known = y == 1
        output_domain = domain & ~all_known
        allowed = output_domain & np.isfinite(selected_surface) & (selected_surface > 0)
        target_k = int(round(float(selected_config["prediction_fraction"]) * int(output_domain.sum())))
        prediction, final_emitted = _top_k_mask(selected_surface, allowed, target_k)
        if final_emitted < 1:
            gate = False
            prediction = None

    report = {
        "schema_version": "gemsdoe35-h35-01-exact-mask-holdout-v3",
        "instrument": "official DTI formula, used locally against withheld public catalogue labels",
        "target_population_caveat": "The public labels are existing mapped faults, whereas the competition's initial private labels are newly identified fault pixels absent from USGS/INGENIOUS. Staff state new pixels may be within 300 m of known traces and nearby predictions are not buffered from scoring. This holdout is a spatial screening proxy, not a leaderboard-score estimate.",
        "organizer_scoring_clarification": "Known USGS/INGENIOUS catalogue pixels are masked pixel-exactly; no surrounding radius is excluded. Final candidate emission zeros only exact known-label pixels.",
        "split": {
            "grid": "2x2 contiguous spatial quadrants",
            "development_folds": list(INNER_FOLDS),
            "final_holdout": FINAL_HOLDOUT,
            "spatial_margin_px": int(spatial_margin_px),
            "metric_radius_m": 300.0,
            "selection": "maximize mean inner-fold delta over single-scale tmi_hg baseline; final NW labels are not used for selection",
            "label_use": "no model fitting; only NE/SW/SE labels select the configuration, then NW is scored once",
            "catalogue_mask": "pixel-exact only at final output; no neighbourhood buffer",
        },
        "baseline": "single-scale supplied tmi_hg edge-strength ranking; matched emitted mass",
        "selected_design_id": selected_config["design_id"],
        "selected_config": selected_config,
        "selected_surface_diagnostics": selected_diagnostics or {},
        "selected_inner_folds": selected_row["inner_folds"],
        "selected_inner_mean_delta_dti": best_inner_mean,
        "final_holdout": outer,
        "gate": {
            "criterion": "all three development block deltas > 0 and final NW spatial holdout delta > 0, all compared to a matched-mass single-scale tmi_hg baseline",
            "passed": bool(gate),
            "slot_eligible": False,
            "slot_note": "Local proxy pass is relative only to this repository's single-scale baseline; it does not certify official-data provenance or hidden-test gain. No competition slot is spent automatically.",
        },
        "all_design_results": design_results,
    }
    return ValidationOutput(report, prediction, selected_config)
