import json
from collections import Counter
from pathlib import Path

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


def test_h35_05_preregistration_records_all_lhs_dimensions_and_promotion_gate():
    path = Path(__file__).resolve().parents[1] / "configs/h35-05-lhs.json"
    spec = json.loads(path.read_text(encoding="utf-8"))
    assert spec["n_designs"] == 8
    assert set(spec["numeric_factors"]) == {
        "max_scale_m",
        "linearity_power",
        "distance_weight",
        "prediction_fraction",
    }
    rows = mixed_latin_hypercube(
        spec["n_designs"],
        {name: tuple(bounds) for name, bounds in spec["numeric_factors"].items()},
        spec["categorical_factors"],
        seed=spec["seed"],
        prefix="h35-05",
        fixed=spec["fixed_factors"],
    )
    assert_latin_stratified(rows, {name: tuple(bounds) for name, bounds in spec["numeric_factors"].items()})
    assert len({row["design_id"] for row in rows}) == 8
    assert spec["fixed_factors"]["catalogue_mask"] == "pixel_exact_only_no_buffer"
    assert spec["fixed_factors"]["spatial_rows"] * spec["fixed_factors"]["spatial_cols"] == 6
    assert spec["promotion_rule"]["outer_tile_count"] == 6
    assert spec["promotion_rule"]["minimum_positive_outer_tiles_against_each_comparator"] == 5
    assert spec["promotion_rule"]["competition_slot_automated"] is False


def test_h35_03_preregistration_records_lhs_and_promotion_gate():
    path = Path(__file__).resolve().parents[1] / "configs/h35-03-lhs.json"
    spec = json.loads(path.read_text(encoding="utf-8"))
    assert spec["n_designs"] == 8
    assert len(spec["numeric_factors"]) == 5
    assert spec["categorical_factors"]["magnetic_source"] == ["mag_anom", "rtp", "tmi"]
    assert spec["fixed_factors"]["spatial_rows"] * spec["fixed_factors"]["spatial_cols"] == 6
    assert spec["promotion_rule"]["outer_tile_count"] == 6
    assert spec["promotion_rule"]["minimum_positive_outer_tiles_against_each_comparator"] == 5
    assert spec["promotion_rule"]["emit_tiff_only_if_all_conditions_pass"] is True
