"""Reproducible mixed-factor Latin-hypercube designs.

Numeric columns are stratified independently; categorical columns are balanced
as evenly as possible and shuffled. This provides one-dimensional coverage, not
pairwise orthogonality or a guarantee that every interaction is sampled.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

import numpy as np


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def config_id(config: Mapping[str, Any], prefix: str = "lhs") -> str:
    digest = hashlib.sha256(canonical_json(config).encode("utf-8")).hexdigest()[:10]
    return f"{prefix}-{digest}"


def mixed_latin_hypercube(
    n: int,
    numeric: Mapping[str, tuple[float, float]],
    categorical: Mapping[str, Sequence[Any]] | None = None,
    *,
    seed: int,
    prefix: str = "lhs",
    fixed: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Generate a deterministic mixed-factor LHS with unique full configurations.

    Each numeric factor has exactly one point in each of ``n`` equal-width
    strata. Categorical levels are replicated to balance counts (differing by
    at most one when ``n`` is not divisible by the number of levels). Fixed
    protocol values are copied into every row and included in the config hash.
    """
    if n < 1:
        raise ValueError("n must be positive")
    fixed_values = dict(fixed or {})
    factor_names = list(numeric) + list(categorical or {}) + list(fixed_values)
    if len(factor_names) != len(set(factor_names)) or "design_id" in factor_names:
        raise ValueError("numeric, categorical, and fixed factor names must be disjoint and cannot use 'design_id'")
    rng = np.random.default_rng(seed)
    numeric_columns: dict[str, np.ndarray] = {}
    for name, bounds in numeric.items():
        if len(bounds) != 2:
            raise ValueError(f"numeric factor {name!r} must have exactly two bounds")
        low, high = map(float, bounds)
        if not np.isfinite(low) or not np.isfinite(high) or not low < high:
            raise ValueError(f"invalid numeric bounds for {name!r}: {bounds!r}")
        strata = (np.arange(n, dtype=np.float64) + rng.random(n)) / n
        rng.shuffle(strata)
        numeric_columns[name] = low + strata * (high - low)

    categorical_columns: dict[str, np.ndarray] = {}
    for name, raw_levels in (categorical or {}).items():
        levels = list(raw_levels)
        if not levels:
            raise ValueError(f"categorical factor {name!r} needs at least one level")
        if len({canonical_json({"v": value}) for value in levels}) != len(levels):
            raise ValueError(f"categorical factor {name!r} has duplicate levels")
        reps = (n + len(levels) - 1) // len(levels)
        column = np.asarray((levels * reps)[:n], dtype=object)
        rng.shuffle(column)
        categorical_columns[name] = column

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i in range(n):
        row: dict[str, Any] = {}
        for name, column in numeric_columns.items():
            row[name] = float(column[i])
        for name, column in categorical_columns.items():
            value = column[i]
            row[name] = value.item() if isinstance(value, np.generic) else value
        row.update(fixed_values)
        # Validate all factors are serializable before deriving a stable ID.
        canonical_json(row)
        row["design_id"] = config_id(row, prefix=prefix)
        signature = canonical_json(row)
        if signature in seen:
            raise RuntimeError("duplicate configuration generated; increase n or revise factors")
        seen.add(signature)
        rows.append(row)

    # Explicit integrity assertions make the design property testable.
    for name, (low, high) in numeric.items():
        values = np.asarray([row[name] for row in rows], dtype=np.float64)
        if not np.all(np.isfinite(values)) or np.any(values < low) or np.any(values >= high):
            raise RuntimeError(f"factor {name!r} falls outside its half-open bounds [{low}, {high})")
        strata = np.floor((values - low) / (high - low) * n).astype(int)
        strata = np.clip(strata, 0, n - 1)
        if len(np.unique(strata)) != n:
            raise RuntimeError(f"factor {name!r} is not Latin-stratified")
    return rows


def assert_latin_stratified(
    rows: Sequence[Mapping[str, Any]], numeric: Mapping[str, tuple[float, float]]
) -> None:
    """Raise if a persisted design no longer has one value per numeric stratum."""
    n = len(rows)
    if n < 1:
        raise ValueError("empty design")
    for name, (low, high) in numeric.items():
        values = np.asarray([float(row[name]) for row in rows], dtype=np.float64)
        if not np.all(np.isfinite(values)) or np.any(values < low) or np.any(values >= high):
            raise ValueError(f"persisted factor {name!r} falls outside [{low}, {high})")
        strata = np.floor((values - low) / (high - low) * n).astype(int)
        strata = np.clip(strata, 0, n - 1)
        if len(np.unique(strata)) != n:
            raise ValueError(f"persisted factor {name!r} is not Latin-stratified")
