import numpy as np

from gemsdoe35.validation import run_nested_screen


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
