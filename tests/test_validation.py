import numpy as np

from gemsdoe35.validation import (
    _tile_core_masks,
    run_nested_screen,
    run_nested_spatial_lhs_screen,
)


def test_nested_screen_keeps_final_fold_out_of_selection():
    h = w = 96
    yy, xx = np.indices((h, w))
    domain = np.ones((h, w), dtype=bool)
    # Four spatially separated vertical known-fault traces.
    labels = np.zeros((h, w), dtype=np.uint8)
    labels[12:35, 20] = 1
    labels[12:35, 70] = 1
    labels[62:85, 20] = 1
    labels[62:85, 70] = 1
    rtp = np.where(xx >= 20, 1.0, 0.0).astype(np.float32) + np.where(xx >= 70, 0.5, 0.0).astype(np.float32)
    bands = {
        "rtp": rtp,
        "tmi": rtp.copy(),
        "tmi_hg": np.abs(np.gradient(rtp, axis=1)).astype(np.float32),
        "depth_to_base_surf": (xx + yy).astype(np.float32),
        "iso_grav_anom_hg": np.abs(np.gradient(rtp, axis=0)).astype(np.float32),
        "det_elev_slope": np.zeros((h, w), dtype=np.float32),
    }
    configs = [
        {
            "design_id": "c0",
            "magnetic_source": "rtp",
            "max_continuation_m": 200.0,
            "min_orientation_coherence": 0.1,
            "depth_edge_weight": 0.0,
            "gravity_edge_weight": 0.0,
            "quiescence_weight": 0.0,
            "prediction_fraction": 0.02,
            "catalogue_mask": "pixel_exact_only_no_buffer",
        },
        {
            "design_id": "c1",
            "magnetic_source": "blend",
            "max_continuation_m": 400.0,
            "min_orientation_coherence": 0.1,
            "depth_edge_weight": 0.3,
            "gravity_edge_weight": 0.2,
            "quiescence_weight": 0.2,
            "prediction_fraction": 0.02,
            "catalogue_mask": "pixel_exact_only_no_buffer",
        },
    ]
    result = run_nested_screen(
        bands,
        labels,
        domain,
        configs,
        pixel_size_m=100.0,
        spatial_margin_px=8,
        pad_px=8,
    )
    assert result.report["split"]["final_holdout"] == "NW"
    assert result.report["final_holdout"]["fold"] == "NW"
    assert len(result.report["all_design_results"]) == 2
    assert result.report["gate"]["slot_eligible"] is False
    assert "spatial_margin_px" in result.report["split"]
    assert "visible-label-collar_px" not in result.report["split"]
    if not result.report["gate"]["passed"]:
        assert result.prediction is None
    elif result.prediction is not None:
        assert np.all(result.prediction[labels == 1] == 0.0)

    # Altering only final NW labels must not alter the configuration selected
    # from the development folds or their scores.
    changed_nw = labels.copy()
    changed_nw[: h // 2, : w // 2] = 0
    altered = run_nested_screen(
        bands, changed_nw, domain, configs,
        pixel_size_m=100.0, spatial_margin_px=8, pad_px=8,
    )
    assert altered.report["selected_design_id"] == result.report["selected_design_id"]
    assert altered.report["selected_inner_folds"] == result.report["selected_inner_folds"]


def test_registered_tile_count_does_not_silently_drop_empty_cores():
    shape = (60, 80)
    domain = np.zeros(shape, dtype=bool)
    domain[:20, :40] = True
    labels = np.zeros(shape, dtype=np.uint8)
    labels[10, 10] = 1
    tiles = _tile_core_masks(shape, domain, rows=3, cols=2, margin_px=5)
    assert len(tiles) == 6
    assert tiles["R1C1"].any()
    assert not tiles["R3C2"].any()
    with np.testing.assert_raises(ValueError):
        run_nested_spatial_lhs_screen(
            {},
            labels,
            domain,
            [{"design_id": "not-used"}],
            incumbent_config={},
            spatial_rows=3,
            spatial_cols=2,
            spatial_margin_px=5,
            holdout_reuse_note="synthetic empty-tile validation",
        )


def test_h35_03_nested_3x2_requires_beating_incumbent_at_matched_mass():
    h, w = 180, 240
    yy, xx = np.indices((h, w))
    domain = np.ones((h, w), dtype=bool)
    trough = (
        10.0
        - 5.0 * np.exp(-((xx - 60.0) ** 2) / (2.0 * 5.0**2))
        - 5.0 * np.exp(-((xx - 180.0) ** 2) / (2.0 * 5.0**2))
    ).astype(np.float32)
    labels = np.zeros((h, w), dtype=np.uint8)
    for row in range(3):
        r0 = row * (h // 3)
        for center_col in (60, 180):
            labels[r0 + 26 : r0 + 34, center_col] = 1
    bands = {
        "mag_anom": trough,
        "rtp": trough.copy(),
        "tmi": trough.copy(),
        "tmi_hg": np.abs(np.gradient(trough, axis=1)).astype(np.float32),
        "cond_surf": np.exp(-((xx - 60.0) ** 2) / 100.0).astype(np.float32),
        "iso_grav_anom_hg": np.abs(np.gradient(trough, axis=1)).astype(np.float32),
        "depth_to_base_surf": (xx + yy).astype(np.float32),
        "det_elev_slope": np.zeros((h, w), dtype=np.float32),
    }
    config = {
        "design_id": "h35-03-test-0",
        "feature_detector": "magnetic_low_flank_curvature_halo",
        "magnetic_source": "mag_anom",
        "max_scale_m": 400.0,
        "n_scales": 3,
        "flank_curvature_weight": 0.5,
        "conductance_weight": 0.2,
        "gravity_edge_weight": 0.1,
        "prediction_fraction": 0.02,
    }
    incumbent = {**config, "design_id": "h35-01-synthetic-incumbent"}
    result = run_nested_spatial_lhs_screen(
        bands,
        labels,
        domain,
        [config],
        incumbent_config=incumbent,
        pixel_size_m=100.0,
        spatial_rows=3,
        spatial_cols=2,
        spatial_margin_px=5,
        minimum_positive_outer_folds=5,
        holdout_reuse_note="synthetic historical-exposure check",
    )
    assert result.report["split"]["grid"] == "3x2 equal-index contiguous tiles"
    assert result.report["split"]["outer_fold_count"] == 6
    assert len(result.report["outer_fold_results"]) == 6
    assert result.report["outer_summary"]["matched_actual_emission_all_outer_folds"] is True
    assert result.report["outer_summary"]["positive_folds_vs_incumbent"] == 0
    assert result.report["gate"]["passed"] is False
    assert result.prediction is None
    assert all(
        fold["actual_emitted_pixels"]["candidate"]
        == fold["actual_emitted_pixels"]["baseline"]
        == fold["actual_emitted_pixels"]["incumbent"]
        for fold in result.report["outer_fold_results"]
    )


def test_challenger_gate_requires_beating_exact_incumbent_on_reused_outer_block():
    h = w = 96
    yy, xx = np.indices((h, w))
    domain = np.ones((h, w), dtype=bool)
    labels = np.zeros((h, w), dtype=np.uint8)
    labels[10:36, 22] = 1
    labels[10:36, 72] = 1
    labels[60:86, 22] = 1
    labels[60:86, 72] = 1
    rtp = (xx >= 22).astype(np.float32) + 0.5 * (xx >= 72).astype(np.float32)
    bands = {
        "rtp": rtp,
        "tmi": rtp.copy(),
        "tmi_hg": np.abs(np.gradient(rtp, axis=1)).astype(np.float32),
        "depth_to_base_surf": (xx + yy).astype(np.float32),
        "iso_grav_anom_hg": np.abs(np.gradient(rtp, axis=0)).astype(np.float32),
        "det_elev_slope": np.zeros((h, w), dtype=np.float32),
    }
    config = {
        "design_id": "challenger-0",
        "feature_detector": "deterministic_poisson_gradient_persistence",
        "magnetic_source": "rtp",
        "max_continuation_m": 200.0,
        "min_orientation_coherence": 0.1,
        "depth_edge_weight": 0.0,
        "gravity_edge_weight": 0.0,
        "quiescence_weight": 0.0,
        "prediction_fraction": 0.02,
    }
    incumbent_config = {**config, "design_id": "incumbent-0", "prediction_fraction": 0.01}
    result = run_nested_screen(
        bands,
        labels,
        domain,
        [config],
        pixel_size_m=100.0,
        spatial_margin_px=8,
        pad_px=8,
        incumbent_config=incumbent_config,
        holdout_reuse_note="synthetic reused block check",
    )
    gate = result.report["gate"]
    outer = result.report["final_holdout"]
    incumbent = result.report["incumbent_holdout"]
    budget = result.report["incumbent_budget_comparison"]
    assert result.report["holdout_reuse_note"] == "synthetic reused block check"
    assert incumbent["design_id"] == "incumbent-0"
    assert incumbent["source_config_prediction_fraction"] == 0.01
    assert incumbent["comparison_prediction_fraction"] == config["prediction_fraction"]
    assert outer["prediction_fraction_requested"] == incumbent["prediction_fraction_requested"]
    assert outer["requested_budget"] == incumbent["requested_budget"]
    assert outer["emitted_pixels_candidate"] == incumbent["emitted_pixels_candidate"]
    assert outer["emitted_pixels_candidate"] == outer["emitted_pixels_baseline"]
    assert incumbent["emitted_pixels_candidate"] == incumbent["emitted_pixels_baseline"]
    assert budget["status"] == "matched"
    assert budget["equal_emitted_mass_all_arms"] is True
    assert gate["incumbent_budget_equal"] is True
    assert gate["beats_incumbent"] is False
    assert gate["passed"] is False
    assert result.prediction is None
