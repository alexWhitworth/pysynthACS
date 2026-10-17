"""Tests for the population table transformation functions.

These functions port R's synthACS transformation logic on raw ACS
estimates/margins-of-error (``E``/``M``) frames. They are pure, deterministic
and operate on positional column indices, so each test builds a synthetic
frame with known column values and asserts both the renamed/aggregated
estimates and the standard-error propagation.
"""

import numpy as np
import pandas as pd

from pysynthacs.transforms.population import (
    transform_birth_and_lang,
    transform_education_pop,
    transform_income_pop,
    transform_marital_status,
    transform_poverty_pop,
)


def _frame(n_rows: int, n_cols: int, start: int = 1) -> pd.DataFrame:
    """Build ``n_rows x n_cols`` frame with sequential float values."""
    return pd.DataFrame(
        np.arange(start, start + n_rows * n_cols, dtype=float).reshape(n_rows, n_cols)
    )


def _se_us_born(se: pd.DataFrame, in_idx: int, out_idx: int) -> pd.Series:
    """Standard error of an in-state + out-state sum (sqrt of sums of squares)."""
    return np.sqrt(se.iloc[:, in_idx] ** 2 + se.iloc[:, out_idx] ** 2)


# ---------------------------------------------------------------------------
# transform_birth_and_lang (B06007)
# ---------------------------------------------------------------------------

def test_transform_birth_and_lang_renames_and_sums_us_born():
    est = _frame(2, 40)
    se = _frame(2, 40)

    out_est, out_se = transform_birth_and_lang(est, se)

    langs = [
        "total", "only_eng", "spk_span", "spk_span_eng_vw", "spk_span_eng_lt_vw",
        "other", "other_eng_vw", "other_eng_lt_vw",
    ]
    origins = ["all", "citizen_born_out_us", "foreign_born", "us_born"]
    assert out_est.columns.tolist() == [f"{o}_{lang}" for o in origins for lang in langs]

    # Direct copies.
    assert out_est["all_total"].tolist() == est.iloc[:, 0].tolist()
    assert out_est["foreign_born_only_eng"].tolist() == est.iloc[:, 33].tolist()
    assert out_est["citizen_born_out_us_total"].tolist() == est.iloc[:, 24].tolist()

    # us_born = in-state (col 8+i) + out-of-state (col 16+i).
    assert out_est["us_born_total"].tolist() == (est.iloc[:, 8] + est.iloc[:, 16]).tolist()
    np.testing.assert_allclose(
        out_se["us_born_total"], _se_us_born(se, 8, 16)
    )


# ---------------------------------------------------------------------------
# transform_marital_status (B06008)
# ---------------------------------------------------------------------------

def test_transform_marital_status_renames_and_sums_us_born():
    est = _frame(2, 30)
    se = _frame(2, 30)

    out_est, out_se = transform_marital_status(est, se)

    origins = ["all", "citizen_born_out_us", "foreign_born", "us_born"]
    statuses = ["total", "nvr_married", "divorced", "separated", "widowed"]
    assert out_est.columns.tolist() == [f"{o}_{s}" for o in origins for s in statuses]

    # Direct copies of the non-us_born origins.
    assert out_est["all_total"].tolist() == est.iloc[:, 0].tolist()
    assert out_est["all_nvr_married"].tolist() == est.iloc[:, 1].tolist()
    assert out_est["foreign_born_divorced"].tolist() == est.iloc[:, 27].tolist()

    # us_born = in-state + out-of-state, with square-sum SE propagation.
    assert out_est["us_born_separated"].tolist() == (
        est.iloc[:, 10] + est.iloc[:, 16]
    ).tolist()
    np.testing.assert_allclose(
        out_se["us_born_separated"], _se_us_born(se, 10, 16)
    )


# ---------------------------------------------------------------------------
# transform_education_pop (B06009)
# ---------------------------------------------------------------------------

def test_transform_education_pop_renames_and_sums_us_born():
    est = _frame(2, 30)
    se = _frame(2, 30)

    out_est, out_se = transform_education_pop(est, se)

    origins = ["all", "citizen_born_out_us", "foreign_born", "us_born"]
    levels = ["total", "lt_hs", "hs", "some_col", "bachelors", "graduate"]
    assert out_est.columns.tolist() == [f"{o}_{lv}" for o in origins for lv in levels]

    assert out_est["all_total"].tolist() == est.iloc[:, 0].tolist()
    assert out_est["foreign_born_bachelors"].tolist() == est.iloc[:, 28].tolist()

    # us_born = col 6+i + col 12+i.
    assert out_est["us_born_total"].tolist() == (est.iloc[:, 6] + est.iloc[:, 12]).tolist()
    np.testing.assert_allclose(out_se["us_born_total"], _se_us_born(se, 6, 12))


# ---------------------------------------------------------------------------
# transform_income_pop (B06010)
# ---------------------------------------------------------------------------

def test_transform_income_pop_renames_and_sums_us_born():
    est = _frame(2, 54)
    se = _frame(2, 54)

    out_est, out_se = transform_income_pop(est, se)

    origins = ["all", "citizen_born_out_us", "foreign_born", "us_born"]
    brackets = [
        "total", "no_inc", "1_lt10k", "10k_lt15k", "15k_lt25k", "25k_lt35k",
        "35k_lt50k", "50k_lt_65k", "65k_lt75k", "gt75k",
    ]
    assert out_est.columns.tolist() == [f"{o}_{b}" for o in origins for b in brackets]

    assert out_est["all_total"].tolist() == est.iloc[:, 0].tolist()
    assert out_est["all_no_inc"].tolist() == est.iloc[:, 1].tolist()
    assert out_est["foreign_born_total"].tolist() == est.iloc[:, 44].tolist()

    # us_born: in-state [11, 12, 14..21], out-state [22, 23, 25..32].
    assert out_est["us_born_total"].tolist() == (est.iloc[:, 11] + est.iloc[:, 22]).tolist()
    np.testing.assert_allclose(out_se["us_born_total"], _se_us_born(se, 11, 22))


# ---------------------------------------------------------------------------
# transform_poverty_pop (B06012)
# ---------------------------------------------------------------------------

def test_transform_poverty_pop_renames_and_sums_us_born():
    est = _frame(2, 20)
    se = _frame(2, 20)

    out_est, out_se = transform_poverty_pop(est, se)

    origins = ["all", "citizen_born_out_us", "foreign_born", "us_born"]
    levels = ["total", "0_lt100pct_pov_lvl", "100_lt150pct_pov_lvl", "gt150pct_pov_lvl"]
    assert out_est.columns.tolist() == [f"{o}_{lv}" for o in origins for lv in levels]

    assert out_est["all_total"].tolist() == est.iloc[:, 0].tolist()
    assert out_est["foreign_born_gt150pct_pov_lvl"].tolist() == est.iloc[:, 19].tolist()

    # us_born = col 4+i + col 8+i.
    assert out_est["us_born_total"].tolist() == (est.iloc[:, 4] + est.iloc[:, 8]).tolist()
    np.testing.assert_allclose(out_se["us_born_total"], _se_us_born(se, 4, 8))
