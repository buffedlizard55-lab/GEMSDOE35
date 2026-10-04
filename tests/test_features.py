import json

import numpy as np

from gemsdoe35.features import (
    candidate_surface,
    magnetic_low_halo_surface,
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
