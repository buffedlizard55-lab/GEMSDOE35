from collections import Counter

import numpy as np

from gemsdoe35.design import assert_latin_stratified, mixed_latin_hypercube


NUMERIC = {"a": (0.0, 1.0), "b": (10.0, 20.0), "c": (1.0, 100.0)}
CATEGORICAL = {"model": ["ridge", "tree", "linear"], "buffer": [0, 1, 2, 3]}


def test_each_numeric_factor_hits_each_stratum_once():
    rows = mixed_latin_hypercube(12, NUMERIC, CATEGORICAL, seed=20261004)
    assert_latin_stratified(rows, NUMERIC)
    for key, (low, high) in NUMERIC.items():
        strata = np.floor((np.array([row[key] for row in rows]) - low) / (high - low) * 12).astype(int)
        assert sorted(np.clip(strata, 0, 11).tolist()) == list(range(12))


def test_design_is_reproducible_and_ids_are_unique():
    a = mixed_latin_hypercube(8, NUMERIC, CATEGORICAL, seed=19)
    b = mixed_latin_hypercube(8, NUMERIC, CATEGORICAL, seed=19)
    assert a == b
    assert len({row["design_id"] for row in a}) == len(a)


def test_categorical_levels_are_balanced():
    rows = mixed_latin_hypercube(12, NUMERIC, CATEGORICAL, seed=123)
    assert Counter(row["model"] for row in rows) == {"ridge": 4, "tree": 4, "linear": 4}
    assert Counter(row["buffer"] for row in rows) == {0: 3, 1: 3, 2: 3, 3: 3}


def test_fixed_protocol_factors_are_hashed_and_repeated():
    rows = mixed_latin_hypercube(
        8, NUMERIC, {"model": ["ridge", "tree"]}, seed=8,
        fixed={"mask": "pixel_exact_only"},
    )
    assert all(row["mask"] == "pixel_exact_only" for row in rows)
    alternate = mixed_latin_hypercube(
        8, NUMERIC, {"model": ["ridge", "tree"]}, seed=8,
        fixed={"mask": "buffered"},
    )
    assert [row["design_id"] for row in rows] != [row["design_id"] for row in alternate]
