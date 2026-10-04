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
    scoring_budget: int | None = None,
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
    # `scoring_budget` is used only when matching all arms in a separate
    # incumbent comparison. The requested mass remains visible in the report.
    initial_scoring_budget = target_k if scoring_budget is None else min(target_k, max(0, int(scoring_budget)))
    pred, emitted = _top_k_mask(candidate_score, eval_mask, initial_scoring_budget)
    baseline, baseline_emitted = _top_k_mask(baseline_score, eval_mask, initial_scoring_budget)
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
        "prediction_fraction_requested": float(prediction_fraction),
        "requested_budget": target_k,
        "scoring_budget_cap": initial_scoring_budget,
        "emitted_pixels_candidate": emitted,
        "emitted_pixels_baseline": baseline_emitted,
        "actual_prediction_fraction": float(emitted / available),
        "budget_shortfall_pixels": int(target_k - emitted),
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
    incumbent_config: Mapping[str, Any] | None = None,
    holdout_reuse_note: str | None = None,
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
    incumbent_outer: dict[str, Any] | None = None
    incumbent_budget_comparison: dict[str, Any] | None = None
    beats_incumbent: bool | None = None
    if incumbent_config is not None:
        incumbent = dict(incumbent_config)
        comparison_fraction = float(selected_config["prediction_fraction"])
        incumbent_surface, _ = candidate_surface(
            bands, domain, incumbent, pixel_size_m=pixel_size_m, pad_px=pad_px
        )
        incumbent_outer = _paired_fold_scores(
            incumbent_surface,
            baseline,
            y,
            domain,
            core,
            heldout_name=FINAL_HOLDOUT,
            # The incumbent is rescored at the selected challenger fraction;
            # its own historical emission fraction is metadata, not a fair
            # comparison budget.
            prediction_fraction=comparison_fraction,
            pixel_size_m=pixel_size_m,
        )
        incumbent_outer["design_id"] = str(incumbent.get("design_id", "unknown"))
        incumbent_outer["source_config_prediction_fraction"] = float(incumbent.get("prediction_fraction", 0.0))
        incumbent_outer["comparison_prediction_fraction"] = comparison_fraction
        if outer.get("status") == "scored" and incumbent_outer.get("status") == "scored":
            common_emitted = min(
                int(outer["emitted_pixels_candidate"]),
                int(incumbent_outer["emitted_pixels_candidate"]),
            )
            # Recompute both candidate-vs-baseline pairs at the common actual
            # mass. This handles sparse score surfaces as well as unequal
            # fractions, and lets us assert exact cross-arm budget equality.
            outer = _paired_fold_scores(
                selected_surface,
                baseline,
                y,
                domain,
                core,
                heldout_name=FINAL_HOLDOUT,
                prediction_fraction=comparison_fraction,
                pixel_size_m=pixel_size_m,
                scoring_budget=common_emitted,
            )
            incumbent_outer = _paired_fold_scores(
                incumbent_surface,
                baseline,
                y,
                domain,
                core,
                heldout_name=FINAL_HOLDOUT,
                prediction_fraction=comparison_fraction,
                pixel_size_m=pixel_size_m,
                scoring_budget=common_emitted,
            )
            incumbent_outer["design_id"] = str(incumbent.get("design_id", "unknown"))
            incumbent_outer["source_config_prediction_fraction"] = float(incumbent.get("prediction_fraction", 0.0))
            incumbent_outer["comparison_prediction_fraction"] = comparison_fraction
            equal_budget = (
                int(outer["emitted_pixels_candidate"]) == int(incumbent_outer["emitted_pixels_candidate"])
                == int(outer["emitted_pixels_baseline"]) == int(incumbent_outer["emitted_pixels_baseline"])
            )
            incumbent_budget_comparison = {
                "status": "matched" if equal_budget else "mismatch",
                "prediction_fraction": comparison_fraction,
                "requested_budget_pixels": int(outer["requested_budget"]),
                "common_scoring_budget_pixels": int(common_emitted),
                "challenger_emitted_pixels": int(outer["emitted_pixels_candidate"]),
                "incumbent_emitted_pixels": int(incumbent_outer["emitted_pixels_candidate"]),
                "challenger_baseline_emitted_pixels": int(outer["emitted_pixels_baseline"]),
                "incumbent_baseline_emitted_pixels": int(incumbent_outer["emitted_pixels_baseline"]),
                "equal_emitted_mass_all_arms": bool(equal_budget),
            }
            beats_incumbent = bool(
                equal_budget
                and float(outer["candidate"]["score"]) > float(incumbent_outer["candidate"]["score"])
            )
        else:
            beats_incumbent = False
            incumbent_budget_comparison = {
                "status": "unscored",
                "prediction_fraction": comparison_fraction,
                "equal_emitted_mass_all_arms": False,
            }
    selected_row = next(row for row in design_results if row["design_id"] == selected_config["design_id"])
    inner_deltas = [r["delta_dti"] for r in selected_row["inner_folds"] if r["status"] == "scored"]
    baseline_gate = (
        len(inner_deltas) == len(INNER_FOLDS)
        and all(delta > 0.0 for delta in inner_deltas)
        and outer.get("status") == "scored"
        and float(outer["delta_dti"]) > 0.0
    )
    gate = bool(baseline_gate and (beats_incumbent is not False))
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
        "schema_version": "gemsdoe35-exact-mask-holdout-v4-matched-incumbent-budget",
        "instrument": "official DTI formula, used locally against withheld public catalogue labels",
        "target_population_caveat": "The public labels are existing mapped faults, whereas the competition's initial private labels are newly identified fault pixels absent from USGS/INGENIOUS. Staff state new pixels may be within 300 m of known traces and nearby predictions are not buffered from scoring. This holdout is a spatial screening proxy, not a leaderboard-score estimate.",
        "organizer_scoring_clarification": "Known USGS/INGENIOUS catalogue pixels are masked pixel-exactly; no surrounding radius is excluded. Final candidate emission zeros only exact known-label pixels.",
        "holdout_reuse_note": holdout_reuse_note,
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
        "incumbent_holdout": incumbent_outer,
        "incumbent_budget_comparison": incumbent_budget_comparison,
        "gate": {
            "criterion": "all three development block deltas > 0 and NW spatial holdout delta > 0 versus matched-mass single-scale tmi_hg; when an incumbent is supplied, rescore it at the selected challenger prediction fraction and require identical actual emitted pixel counts across challenger, incumbent, and each matched-mass tmi_hg reference before comparing DTI",
            "baseline_gate_passed": bool(baseline_gate),
            "beats_incumbent": beats_incumbent,
            "incumbent_budget_equal": None if incumbent_budget_comparison is None else incumbent_budget_comparison.get("equal_emitted_mass_all_arms", False),
            "passed": bool(gate),
            "slot_eligible": False,
            "slot_note": "A local proxy pass does not certify official-data provenance or hidden-test gain. Reused NW comparisons are not independent confirmation. No competition slot is spent automatically.",
        },
        "all_design_results": design_results,
    }
    return ValidationOutput(report, prediction, selected_config)


def _tile_core_masks(
    shape: tuple[int, int],
    domain: np.ndarray,
    *,
    rows: int,
    cols: int,
    margin_px: int,
) -> dict[str, np.ndarray]:
    """Create nonoverlapping spatial evaluation cores inside equal-index tiles."""
    if rows < 1 or cols < 1 or margin_px < 0:
        raise ValueError("tile counts must be positive and margin nonnegative")
    height, width = shape
    row_edges = np.rint(np.linspace(0, height, rows + 1)).astype(int)
    col_edges = np.rint(np.linspace(0, width, cols + 1)).astype(int)
    masks: dict[str, np.ndarray] = {}
    for row in range(rows):
        for col in range(cols):
            r0, r1 = int(row_edges[row]) + margin_px, int(row_edges[row + 1]) - margin_px
            c0, c1 = int(col_edges[col]) + margin_px, int(col_edges[col + 1]) - margin_px
            if r0 >= r1 or c0 >= c1:
                raise ValueError("spatial margin leaves an empty tile")
            mask = np.zeros(shape, dtype=bool)
            mask[r0:r1, c0:c1] = True
            mask &= domain
            # Keep even empty cores so the caller must fail on missing support
            # instead of silently changing the registered fold count.
            masks[f"R{row + 1}C{col + 1}"] = mask
    return masks


def _matched_triad_scores(
    candidate_score: np.ndarray,
    baseline_score: np.ndarray,
    incumbent_score: np.ndarray,
    labels: np.ndarray,
    evaluation_mask: np.ndarray,
    *,
    fold_name: str,
    prediction_fraction: float,
    pixel_size_m: float,
) -> dict[str, Any]:
    """Score challenger, baseline and incumbent at one exact emitted mass."""
    available = int(evaluation_mask.sum())
    requested = int(round(float(prediction_fraction) * available))
    truth = (labels == 1) & evaluation_mask
    if available == 0 or requested < 1 or not truth.any():
        return {
            "fold": fold_name,
            "status": "insufficient_prediction_domain_or_truth",
            "available_pixels": available,
            "truth_pixels": int(truth.sum()),
            "requested_budget": requested,
        }
    candidate_prediction, candidate_emitted = _top_k_mask(
        candidate_score, evaluation_mask, requested
    )
    baseline_prediction, baseline_emitted = _top_k_mask(
        baseline_score, evaluation_mask, requested
    )
    incumbent_prediction, incumbent_emitted = _top_k_mask(
        incumbent_score, evaluation_mask, requested
    )
    common_mass = min(candidate_emitted, baseline_emitted, incumbent_emitted)
    if common_mass < 1:
        return {
            "fold": fold_name,
            "status": "no_common_positive_mass",
            "available_pixels": available,
            "truth_pixels": int(truth.sum()),
            "requested_budget": requested,
            "requested_emissions": {
                "candidate": candidate_emitted,
                "baseline": baseline_emitted,
                "incumbent": incumbent_emitted,
            },
        }
    if candidate_emitted != common_mass:
        candidate_prediction, candidate_emitted = _top_k_mask(
            candidate_score, evaluation_mask, common_mass
        )
    if baseline_emitted != common_mass:
        baseline_prediction, baseline_emitted = _top_k_mask(
            baseline_score, evaluation_mask, common_mass
        )
    if incumbent_emitted != common_mass:
        incumbent_prediction, incumbent_emitted = _top_k_mask(
            incumbent_score, evaluation_mask, common_mass
        )
    candidate = dti(truth, candidate_prediction, valid=evaluation_mask, pixel_size_m=pixel_size_m)
    baseline = dti(truth, baseline_prediction, valid=evaluation_mask, pixel_size_m=pixel_size_m)
    incumbent = dti(truth, incumbent_prediction, valid=evaluation_mask, pixel_size_m=pixel_size_m)
    matched = candidate_emitted == baseline_emitted == incumbent_emitted == common_mass
    return {
        "fold": fold_name,
        "status": "scored" if matched else "emission_mass_mismatch",
        "available_pixels": available,
        "truth_pixels": int(truth.sum()),
        "prediction_fraction_requested": float(prediction_fraction),
        "requested_budget": requested,
        "actual_emitted_pixels": {
            "candidate": int(candidate_emitted),
            "baseline": int(baseline_emitted),
            "incumbent": int(incumbent_emitted),
        },
        "all_emissions_matched": bool(matched),
        "candidate": candidate.as_dict(),
        "baseline": baseline.as_dict(),
        "incumbent": incumbent.as_dict(),
        "delta_vs_baseline": float(candidate.score - baseline.score),
        "delta_vs_incumbent": float(candidate.score - incumbent.score),
    }


def run_nested_spatial_lhs_screen(
    bands: Mapping[str, np.ndarray],
    labels: np.ndarray,
    domain: np.ndarray,
    configs: Sequence[Mapping[str, Any]],
    *,
    incumbent_config: Mapping[str, Any],
    pixel_size_m: float = 100.0,
    spatial_rows: int = 3,
    spatial_cols: int = 2,
    spatial_margin_px: int = 30,
    minimum_positive_outer_folds: int = 5,
    holdout_reuse_note: str,
) -> ValidationOutput:
    """Nested leave-one-tile-out selection and matched incumbent validation.

    The LHS is generated before labels are scored. For each outer tile, the
    winning config is selected using only the other tiles, then compared against
    both `tmi_hg` and the frozen incumbent on the held-out tile at identical
    actual pixel mass. The final config is selected over all tiles only after
    procedure-level outer-CV results have been computed. This is an exploratory
    local proxy when historical analysis has already exposed the same geography.
    """
    y = np.asarray(labels)
    valid_domain = np.asarray(domain, dtype=bool)
    if y.ndim != 2 or y.shape != valid_domain.shape:
        raise ValueError("labels and domain must be matching 2-D arrays")
    if not configs:
        raise ValueError("at least one LHS configuration is required")
    if not holdout_reuse_note.strip():
        raise ValueError("holdout_reuse_note must describe prior exposure")
    ids = [str(config.get("design_id", "")) for config in configs]
    if any(not item for item in ids) or len(set(ids)) != len(ids):
        raise ValueError("each configuration must have a unique nonempty design_id")

    tiles = _tile_core_masks(
        y.shape,
        valid_domain,
        rows=spatial_rows,
        cols=spatial_cols,
        margin_px=spatial_margin_px,
    )
    if len(tiles) < 3:
        raise ValueError("nested spatial screening needs at least three nonempty tiles")
    tile_metadata = {
        name: {
            "available_pixels": int(mask.sum()),
            "truth_pixels": int(((y == 1) & mask).sum()),
        }
        for name, mask in tiles.items()
    }
    unusable = [name for name, info in tile_metadata.items() if info["available_pixels"] < 1 or info["truth_pixels"] < 1]
    if unusable:
        raise ValueError(f"spatial tiles require valid domain and truth pixels: {unusable}")
    if minimum_positive_outer_folds < 1 or minimum_positive_outer_folds > len(tiles):
        raise ValueError("minimum_positive_outer_folds must be within the number of tiles")

    if "tmi_hg" not in bands:
        raise ValueError("bands must include `tmi_hg` for the declared baseline")
    baseline_surface = normalize_for_ranking(bands["tmi_hg"], valid_domain)
    incumbent_surface, incumbent_diagnostics = candidate_surface(
        bands,
        valid_domain,
        dict(incumbent_config),
        pixel_size_m=pixel_size_m,
    )
    surfaces: list[np.ndarray] = []
    design_results: list[dict[str, Any]] = []
    for raw_config in configs:
        config = dict(raw_config)
        surface, diagnostics = candidate_surface(
            bands, valid_domain, config, pixel_size_m=pixel_size_m
        )
        if surface.shape != y.shape or not np.isfinite(surface[valid_domain]).all():
            raise ValueError(f"candidate surface {config['design_id']} is invalid on the domain")
        fold_results: dict[str, dict[str, Any]] = {}
        for fold_name, core in tiles.items():
            score = _paired_fold_scores(
                surface,
                baseline_surface,
                y,
                valid_domain,
                tiles,
                heldout_name=fold_name,
                prediction_fraction=float(config["prediction_fraction"]),
                pixel_size_m=pixel_size_m,
            )
            fold_results[fold_name] = score
        deltas = [
            float(value["delta_dti"])
            for value in fold_results.values()
            if value.get("status") == "scored"
        ]
        inner_mean = float(np.mean(deltas)) if len(deltas) == len(tiles) else None
        design_results.append(
            {
                "design_id": str(config["design_id"]),
                "config": config,
                "folds_vs_baseline": fold_results,
                "all_tile_mean_delta_vs_baseline": inner_mean,
                "all_tile_positive_folds_vs_baseline": int(sum(delta > 0 for delta in deltas)),
                "surface_diagnostics": diagnostics,
            }
        )
        surfaces.append(surface)

    outer_results: list[dict[str, Any]] = []
    for heldout_name in tiles:
        development_names = [name for name in tiles if name != heldout_name]
        rankings: list[tuple[float, int]] = []
        for result_index, result in enumerate(design_results):
            development_deltas = [
                result["folds_vs_baseline"][name].get("delta_dti")
                for name in development_names
            ]
            if any(value is None for value in development_deltas):
                mean_delta = float("-inf")
            else:
                mean_delta = float(np.mean(np.asarray(development_deltas, dtype=np.float64)))
            rankings.append((mean_delta, result_index))
        selected_mean, selected_index = max(rankings, key=lambda item: (item[0], -item[1]))
        selected_config = dict(configs[selected_index])
        test_result = _matched_triad_scores(
            surfaces[selected_index],
            baseline_surface,
            incumbent_surface,
            y,
            tiles[heldout_name],
            fold_name=heldout_name,
            prediction_fraction=float(selected_config["prediction_fraction"]),
            pixel_size_m=pixel_size_m,
        )
        outer_results.append(
            {
                "heldout_tile": heldout_name,
                "development_tiles": development_names,
                "selected_config_id": selected_config["design_id"],
                "selected_development_mean_delta_vs_baseline": selected_mean,
                **test_result,
            }
        )

    scored_outer = [row for row in outer_results if row.get("status") == "scored"]
    deltas_baseline = [float(row["delta_vs_baseline"]) for row in scored_outer]
    deltas_incumbent = [float(row["delta_vs_incumbent"]) for row in scored_outer]
    matched_every_fold = (
        len(scored_outer) == len(tiles)
        and all(row.get("all_emissions_matched") is True for row in scored_outer)
    )
    mean_baseline = float(np.mean(deltas_baseline)) if deltas_baseline else None
    mean_incumbent = float(np.mean(deltas_incumbent)) if deltas_incumbent else None
    positive_baseline = int(sum(delta > 0 for delta in deltas_baseline))
    positive_incumbent = int(sum(delta > 0 for delta in deltas_incumbent))
    gate = bool(
        matched_every_fold
        and mean_baseline is not None
        and mean_incumbent is not None
        and mean_baseline > 0.0
        and mean_incumbent > 0.0
        and positive_baseline >= minimum_positive_outer_folds
        and positive_incumbent >= minimum_positive_outer_folds
    )

    final_index = max(
        range(len(design_results)),
        key=lambda index: (
            float("-inf")
            if design_results[index]["all_tile_mean_delta_vs_baseline"] is None
            else float(design_results[index]["all_tile_mean_delta_vs_baseline"]),
            -index,
        ),
    )
    final_config = dict(configs[final_index])
    final_prediction: np.ndarray | None = None
    final_emitted = 0
    if gate:
        output_domain = valid_domain & (y != 1)
        allowed = output_domain & np.isfinite(surfaces[final_index]) & (surfaces[final_index] > 0.0)
        requested = int(round(float(final_config["prediction_fraction"]) * int(output_domain.sum())))
        final_prediction, final_emitted = _top_k_mask(surfaces[final_index], allowed, requested)
        if final_emitted < 1:
            gate = False
            final_prediction = None

    report = {
        "schema_version": "gemsdoe35-nested-spatial-lhs-v1",
        "hypothesis_id": "H35-03",
        "instrument": "official DTI formula applied locally to withheld public catalogue labels",
        "target_population_caveat": "Existing public catalogue faults are a proxy, not the newly identified private target. No local DTI delta is a leaderboard estimate.",
        "data_provenance": "pinned public owner-maintained mirror; not organizer-authenticated",
        "holdout_reuse_note": holdout_reuse_note,
        "split": {
            "grid": f"{spatial_rows}x{spatial_cols} equal-index contiguous tiles",
            "outer_tiles": list(tiles),
            "outer_fold_count": len(tiles),
            "spatial_margin_px": int(spatial_margin_px),
            "metric_radius_m": 300.0,
            "selection": "each outer tile is scored after selecting the highest mean development-tile delta against tmi_hg; its labels do not select its own configuration",
            "outer_tile_support": tile_metadata,
            "holdout_reuse_status": "nested within-run exclusion; prior quadrant reports exposed the same geographic labels; exploratory rather than pristine independent confirmation",
        },
        "baseline": "single-scale supplied tmi_hg edge-strength ranking",
        "incumbent": {
            "design_id": str(incumbent_config.get("design_id", "unknown")),
            "method": incumbent_diagnostics.get("method"),
            "source_prediction_fraction": incumbent_config.get("prediction_fraction"),
            "comparison": "rescored at each selected challenger's prediction fraction and matched to identical actual emitted mass",
        },
        "all_design_results": design_results,
        "outer_fold_results": outer_results,
        "outer_summary": {
            "mean_delta_vs_baseline": mean_baseline,
            "positive_folds_vs_baseline": positive_baseline,
            "mean_delta_vs_incumbent": mean_incumbent,
            "positive_folds_vs_incumbent": positive_incumbent,
            "required_positive_folds": int(minimum_positive_outer_folds),
            "matched_actual_emission_all_outer_folds": bool(matched_every_fold),
        },
        "selected_design_id": final_config["design_id"],
        "selected_config": final_config,
        "selection_diagnostic": "final config selected using all spatial tiles after nested procedure-level outer scores; its own score is not an untouched holdout estimate",
        "gate": {
            "criterion": "nested outer-fold mean delta > 0 and at least the registered number of positive tiles against both tmi_hg and the frozen H35-01 incumbent, with matched actual pixel mass across challenger, baseline and incumbent in every outer tile",
            "passed": bool(gate),
            "slot_eligible": False,
            "slot_note": "Local proxy CV never spends a competition slot; a pass still requires official-data provenance review and human decision. Historical quadrant exposure means this is exploratory, not pristine independent confirmation.",
        },
        "submission": None,
        "final_candidate_emitted_pixels": int(final_emitted),
    }
    return ValidationOutput(report, final_prediction, final_config)
