"""Tests for the household table transformation functions.

These mirror R's synthACS household-table logic (column drops, renames and,
where applicable, aggregation) on raw ACS ``E``/``M`` frames.
"""

import numpy as np
import pandas as pd

from pysynthacs.transforms.household import (
    transform_health_ins,
    transform_hh_inc,
    transform_hh_occ,
    transform_hh_tenure,
    transform_hh_type_r,
    transform_hh_type_units,
)


def _frame(n_rows: int, n_cols: int, start: int = 1) -> pd.DataFrame:
    """Build ``n_rows x n_cols`` frame with sequential float values."""
    return pd.DataFrame(
        np.arange(start, start + n_rows * n_cols, dtype=float).reshape(n_rows, n_cols)
    )


def test_transform_hh_type_r_drops_columns_and_falls_back_to_generic_names():
    # B09019 has 37 columns; 20 are dropped, leaving 17, which does not match
    # the 19 target names, so the function assigns generic col_* names.
    est = _frame(2, 37)
    se = _frame(2, 37)

    out_est, _out_se = transform_hh_type_r(est, se)

    assert out_est.shape == (2, 17)
    assert out_est.columns.tolist() == [f"col_{i}" for i in range(17)]

    # Columns at the dropped indices (1-based in R comments) must be gone.
    drop_idxs = [1, 4, 5, 8, 9, 10, 15, 16, 17, 21, 22, 25, 26, 27, 28, 29, 30, 31, 35, 36]
    kept = [i for i in range(37) if i not in drop_idxs]
    np.testing.assert_array_equal(out_est.columns, [f"col_{i}" for i in range(len(kept))])
    assert out_est.iloc[0, 0] == est.iloc[0, kept[0]]


def test_transform_hh_type_r_assigns_names_when_count_matches():
    # 39 columns -> 19 remain, matching the target names exactly.
    est = _frame(1, 39)
    se = _frame(1, 39)

    out_est, _out_se = transform_hh_type_r(est, se)

    assert out_est.shape == (1, 19)
    assert out_est.columns[0] == "total"
    assert out_est.columns[-1] == "in_grp_qtrs"


def test_transform_hh_type_units_is_identity_placeholder():
    # Current implementation is an un-implemented placeholder: passthrough.
    est = _frame(1, 5)
    se = _frame(1, 5)

    out_est, out_se = transform_hh_type_units(est, se)

    pd.testing.assert_frame_equal(out_est, est)
    pd.testing.assert_frame_equal(out_se, se)


def test_transform_hh_inc_renames_quintile_columns():
    est = _frame(1, 6)
    se = _frame(1, 6)

    out_est, out_se = transform_hh_inc(est, se)

    expected = [
        "mean_hh_inc_bottom_quintile", "mean_hh_inc_2nd_quintile",
        "mean_hh_inc_3rd_quintile", "mean_hh_inc_4th_quintile",
        "mean_hh_inc_top_quintile", "mean_hh_inc_top_5pct",
    ]
    assert out_est.columns.tolist() == expected
    assert out_se.columns.tolist() == expected
    # Values unchanged; only names replaced.
    np.testing.assert_array_equal(out_est.values, est.values)


def test_transform_hh_occ_renames_occupancy_columns():
    est = _frame(1, 3)
    se = _frame(1, 3)

    out_est, out_se = transform_hh_occ(est, se)

    expected = ["total_housing_units", "occupied_housing_units", "vacant_housing_units"]
    assert out_est.columns.tolist() == expected
    assert out_se.columns.tolist() == expected


def test_transform_hh_tenure_renames_tenure_columns():
    est = _frame(1, 3)
    se = _frame(1, 3)

    out_est, out_se = transform_hh_tenure(est, se)

    expected = ["total_tenure_units", "owner_occupied_units", "renter_occupied_units"]
    assert out_est.columns.tolist() == expected
    assert out_se.columns.tolist() == expected


def test_transform_health_ins_drops_every_third_column():
    est = _frame(2, 55)
    se = _frame(2, 55)

    out_est, out_se = transform_health_ins(est, se)

    drop_idxs = list(range(2, 27, 3)) + list(range(30, 55, 3))
    kept = [i for i in range(55) if i not in drop_idxs]

    assert out_est.shape == (2, len(kept))
    # Positional drops preserve the remaining underlying columns.
    np.testing.assert_array_equal(out_est.values, est.iloc[:, kept].values)
    np.testing.assert_array_equal(out_se.values, se.iloc[:, kept].values)
