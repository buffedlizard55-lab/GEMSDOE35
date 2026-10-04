import json

import numpy as np

from gemsdoe35.features import (
    candidate_surface,
    magnetic_low_halo_surface,
    multiphysics_edge_concurrence_surface,
    seismicity_ridge_surface,
    magnetic_persistence,
    strain_discontinuity_surface,
)


def _line_data(shape=(64, 64)):
    h, w = shape
    data = np.zeros(shape, dtype=np.float32)
    data[:, w // 2 :] = 10.0
    return data


def test_magnetic_persistence_returns_finite_bounded_orientation():
    data = _line_data()
    domain = np.ones(data.shape, dtype=bool)
    result = magnetic_persistence(data, domain, max_continuation_m=400.0, pad_px=8)
    for array in (result.mean_gradient, result.orientation_coherence, result.persistence):
        assert array.shape == data.shape
        assert np.isfinite(array).all()
    assert np.max(result.persistence) > 0
    assert np.all((result.orientation_coherence >= 0) & (result.orientation_coherence <= 1))
    assert result.heights_m == [0.0, 200.0, 400.0]


def test_candidate_surface_uses_declared_layers_and_masks_outside():
    shape = (64, 64)
    domain = np.ones(shape, dtype=bool)
    domain[:3] = False
    bands = {
        "rtp": _line_data(shape),
        "tmi": _line_data(shape) * 0.5,
        "depth_to_base_surf": np.indices(shape)[1].astype(np.float32),
        "iso_grav_anom_hg": np.indices(shape)[0].astype(np.float32),
        "det_elev_slope": np.zeros(shape, dtype=np.float32),
    }
    config = {
        "design_id": "test-001",
        "magnetic_source": "blend",
        "max_continuation_m": 400.0,
        "min_orientation_coherence": 0.2,
        "depth_edge_weight": 0.3,
        "gravity_edge_weight": 0.2,
        "quiescence_weight": 0.5,
        "prediction_fraction": 0.01,
        "catalogue_mask": "pixel_exact_only_no_buffer",
    }
    score, diagnostics = candidate_surface(bands, domain, config, pad_px=8)
    assert score.shape == shape
    assert np.isfinite(score).all()
    assert np.all(score[~domain] == 0)
    assert diagnostics["method"] == "poisson_continuation_gradient_orientation_persistence"
    json.dumps(diagnostics, allow_nan=False)


def test_magnetic_low_halo_scores_a_line_like_magnetic_trough():
    shape = (80, 96)
    yy, xx = np.indices(shape)
    domain = np.ones(shape, dtype=bool)
    domain[:2] = False
    trough = (10.0 - 6.0 * np.exp(-((xx - 48.0) ** 2) / (2.0 * 5.0**2))).astype(np.float32)
    bands = {
        "mag_anom": trough,
        "rtp": trough * 0.8,
        "tmi": trough * 1.2,
        "cond_surf": np.exp(-((xx - 48.0) ** 2) / (2.0 * 8.0**2)).astype(np.float32),
        "iso_grav_anom_hg": np.abs(np.gradient(trough, axis=1)).astype(np.float32),
    }
    config = {
        "feature_detector": "magnetic_low_flank_curvature_halo",
        "design_id": "test-h35-03",
        "magnetic_source": "mag_anom",
        "max_scale_m": 500.0,
        "n_scales": 3,
        "flank_curvature_weight": 0.75,
        "conductance_weight": 0.2,
        "gravity_edge_weight": 0.1,
        "prediction_fraction": 0.01,
    }
    score, diagnostics = magnetic_low_halo_surface(
        bands, domain, config, pixel_size_m=100.0
    )
    assert score.shape == shape
    assert np.isfinite(score).all()
    assert np.all(score[~domain] == 0.0)
    assert score[:, 48].max() > score[:, 20].max()
    assert diagnostics["method"] == "magnetic_low_flank_curvature_halo"
    assert np.allclose(diagnostics["scale_levels_m"], [500.0 / 3.0, 1000.0 / 3.0, 500.0])
    json.dumps(diagnostics, allow_nan=False)

    routed, routed_diagnostics = candidate_surface(bands, domain, config)
    assert np.allclose(routed, score)
    assert routed_diagnostics == diagnostics


def test_magnetic_low_halo_rejects_unknown_source():
    shape = (16, 16)
    with np.testing.assert_raises(ValueError):
        magnetic_low_halo_surface(
            {"cond_surf": np.ones(shape), "iso_grav_anom_hg": np.ones(shape)},
            np.ones(shape, dtype=bool),
            {"magnetic_source": "unknown", "max_scale_m": 500.0},
        )


def test_strain_discontinuity_targets_multiscale_edges_not_hotspot_magnitude():
    shape = (80, 96)
    yy, xx = np.indices(shape)
    domain = np.ones(shape, dtype=bool)
    step = np.where(xx >= 48, 10.0, 0.0).astype(np.float32)
    bands = {
        "geod_2ndinv": step,
        "geod_shearrate": -step,
        "geod_dilaterate": step * 0.5,
    }
    config = {
        "feature_detector": "multiscale_strain_gradient_orientation",
        "strain_source": "all_three",
        "max_smoothing_sigma_m": 500.0,
        "min_orientation_coherence": 0.2,
        "n_scales": 3,
        "prediction_fraction": 0.01,
    }
    score, diagnostics = strain_discontinuity_surface(
        bands, domain, config, pixel_size_m=100.0
    )
    assert score.shape == shape
    assert np.isfinite(score).all()
    assert score[:, 48].max() > 0.0
    assert score[:, 20].max() == 0.0
    assert diagnostics["method"] == "multiscale_strain_gradient_orientation_persistence"
    json.dumps(diagnostics, allow_nan=False)

    routed, routed_diagnostics = candidate_surface(bands, domain, config)
    assert np.array_equal(routed, score)
    assert routed_diagnostics == diagnostics


def test_multiphysics_edge_concurrence_rewards_aligned_independent_families():
    shape = (80, 96)
    yy, xx = np.indices(shape)
    domain = np.ones(shape, dtype=bool)
    mag = np.where(xx >= 48, 8.0, 0.0).astype(np.float32)
    gravity_aligned = np.where(xx >= 48, 4.0, 0.0).astype(np.float32)
    strain_aligned = np.where(xx >= 48, 2.0, 0.0).astype(np.float32)
    config = {
        "feature_detector": "multiphysics_edge_concurrence",
        "design_id": "test-h35-04",
        "magnetic_source": "mag_anom",
        "max_scale_m": 600.0,
        "smoothing_scales": 3,
        "orientation_power": 2.0,
        "multiphysics_balance": 0.7,
        "prediction_fraction": 0.01,
    }
    aligned, aligned_meta = multiphysics_edge_concurrence_surface(
        {"mag_anom": mag, "iso_grav_anom": gravity_aligned, "geod_shearrate": strain_aligned},
        domain, config, pixel_size_m=100.0
    )
    strain_cross = np.where(yy >= 40, 2.0, 0.0).astype(np.float32)
    crossed, crossed_meta = candidate_surface(
        {"mag_anom": mag, "iso_grav_anom": gravity_aligned, "geod_shearrate": strain_cross},
        domain, config, pixel_size_m=100.0
    )
    assert np.isfinite(aligned).all() and np.isfinite(crossed).all()
    assert np.all(aligned[~domain] == 0.0)
    assert float(np.quantile(aligned[:, 45:52], 0.95)) > float(np.quantile(crossed[:, 45:52], 0.95))
    assert aligned_meta["method"] == "multiphysics_edge_concurrence"
    assert crossed_meta["method"] == "multiphysics_edge_concurrence"
    assert aligned_meta["scale_levels_m"] == [200.0, 400.0, 600.0]
    json.dumps(aligned_meta, allow_nan=False)


def test_multiphysics_edge_concurrence_rejects_missing_or_invalid_factors():
    shape = (16, 16)
    domain = np.ones(shape, dtype=bool)
    bands = {name: np.ones(shape, dtype=np.float32) for name in ("mag_anom", "iso_grav_anom")}
    config = {"magnetic_source": "mag_anom", "max_scale_m": 300.0, "orientation_power": 1.0, "multiphysics_balance": 0.5}
    with np.testing.assert_raises(ValueError):
        multiphysics_edge_concurrence_surface(bands, domain, config)
    bands["geod_shearrate"] = np.ones(shape, dtype=np.float32)
    config["multiphysics_balance"] = 1.5
    with np.testing.assert_raises(ValueError):
        multiphysics_edge_concurrence_surface(bands, domain, config)


def test_h35_05_seismic_curvature_rewards_coherent_ridge_and_distance_trough():
    shape = (96, 112)
    yy, xx = np.indices(shape)
    distance_from_line = yy.astype(np.float32) - 48.0
    density = (250.0 + 1800.0 * np.exp(-(distance_from_line**2) / (2.0 * 7.0**2))).astype(np.float32)
    distance = (100.0 + 5000.0 * (1.0 - np.exp(-(distance_from_line**2) / (2.0 * 9.0**2)))).astype(np.float32)
    domain = np.ones(shape, dtype=bool)
    domain[:2, :] = False
    domain[-2:, :] = False
    bands = {"ieq_n100a15": density, "deq_n100a15": distance}
    config = {
        "feature_detector": "seismicity_ridge_curvature",
        "design_id": "test-h35-05",
        "max_scale_m": 600.0,
        "smoothing_scales": 3,
        "linearity_power": 1.4,
        "distance_weight": 0.5,
        "prediction_fraction": 0.01,
    }
    score, diagnostics = seismicity_ridge_surface(bands, domain, config, pixel_size_m=100.0)
    assert score.shape == shape
    assert np.isfinite(score).all()
    assert np.all(score[~domain] == 0.0)
    assert float(np.max(score[45:52, :])) > float(np.max(score[10:20, :]))
    assert diagnostics["method"] == "multiscale_seismicity_density_ridge_and_distance_trough"
    assert diagnostics["scale_levels_m"] == [200.0, 400.0, 600.0]
    json.dumps(diagnostics, allow_nan=False)

    routed, routed_diagnostics = candidate_surface(bands, domain, config)
    assert np.array_equal(routed, score)
    assert routed_diagnostics == diagnostics


def test_h35_05_seismic_curvature_rejects_bad_inputs_and_handles_constant_layers():
    shape = (24, 24)
    domain = np.ones(shape, dtype=bool)
    config = {
        "feature_detector": "seismicity_ridge_curvature",
        "max_scale_m": 400.0,
        "linearity_power": 1.0,
        "distance_weight": 1.0,
    }
    with np.testing.assert_raises(ValueError):
        seismicity_ridge_surface({"ieq_n100a15": np.ones(shape)}, domain, config)
    bands = {name: np.ones(shape, dtype=np.float32) for name in ("ieq_n100a15", "deq_n100a15")}
    config["distance_weight"] = 1.1
    with np.testing.assert_raises(ValueError):
        seismicity_ridge_surface(bands, domain, config)
    config["distance_weight"] = 0.5
    score, _ = seismicity_ridge_surface(bands, domain, config)
    assert np.isfinite(score).all()
    assert np.all(score == 0.0)
