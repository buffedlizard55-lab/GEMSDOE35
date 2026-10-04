import numpy as np
import pytest

from gemsdoe35.metric import dti


def test_perfect_overlap_is_one():
    truth = np.zeros((9, 9), dtype=bool)
    truth[4, 4] = True
    result = dti(truth, truth.astype(np.float32))
    assert result.score == pytest.approx(1.0)
    assert result.tp_weighted == pytest.approx(1.0)
    assert result.fp_weighted == pytest.approx(0.0)
    assert result.fn_weighted == pytest.approx(0.0)


def test_off_by_one_pixel_uses_triangular_kernel():
    truth = np.zeros((9, 9), dtype=bool)
    prediction = np.zeros((9, 9), dtype=np.float32)
    truth[4, 4] = True
    prediction[4, 5] = 1.0
    result = dti(truth, prediction, pixel_size_m=100.0, radius_m=300.0)
    assert result.tp_weighted == pytest.approx(2.0 / 3.0)
    assert result.fp_weighted == pytest.approx(1.0 / 3.0)
    assert result.fn_weighted == pytest.approx(1.0 / 3.0)
    assert result.score == pytest.approx(2.0 / 3.0)


def test_range_error_is_not_silently_clipped():
    truth = np.zeros((5, 5), dtype=bool)
    prediction = np.zeros((5, 5), dtype=np.float32)
    prediction[2, 2] = 1.01
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        dti(truth, prediction)


def test_outside_domain_is_ignored_even_if_it_contains_a_sentinel():
    truth = np.zeros((5, 5), dtype=bool)
    domain = np.zeros((5, 5), dtype=bool)
    domain[1:4, 1:4] = True
    prediction = np.full((5, 5), -3.4028235e38, dtype=np.float32)
    prediction[domain] = 0.0
    result = dti(truth, prediction, valid=domain)
    assert result.score == 0.0
    assert result.predicted_mass == 0.0


def test_exact_offset_implementation_matches_bruteforce():
    rng = np.random.default_rng(42)
    truth = rng.random((11, 13)) < 0.12
    prediction = rng.random((11, 13), dtype=np.float32)
    valid = np.ones_like(truth)
    valid[:2, :] = False
    valid[:, -2:] = False
    truth &= valid
    result = dti(truth, prediction, valid=valid)

    r = 300.0
    tp = 0.0
    fn = 0.0
    coords = np.argwhere(truth)
    for gr, gc in coords:
        credits = []
        for pr, pc in np.argwhere(valid & (prediction > 0)):
            distance = np.hypot((pr - gr) * 100.0, (pc - gc) * 100.0)
            credits.append(float(prediction[pr, pc]) * max(1.0 - distance / r, 0.0))
        best = max(credits, default=0.0)
        tp += best
        fn += 1.0 - best
    fp = 0.0
    for pr, pc in np.argwhere(valid):
        nearest = min((np.hypot((pr-gr)*100.0, (pc-gc)*100.0) for gr,gc in coords), default=float("inf"))
        weight = max(1.0 - nearest / r, 0.0)
        fp += float(prediction[pr, pc]) * (1.0 - weight)
    expected = tp / (tp + 0.2 * fp + 0.8 * fn + 1e-12)
    assert result.score == pytest.approx(expected, abs=1e-12)
