import pytest
import pandas as pd
import xarray as xr
import numpy as np
from pysynthacs.core.data import MacroData, MicroData
from pysynthacs.core.base import AcsResult, PullConfig
from pysynthacs.core.adapter import acs_result_to_macro_data

def test_macro_data_marginalization():
    """Test that MacroData can correctly sum over dimensions."""
    data = xr.Dataset(
        data_vars={
            "count": (["geo", "gender", "age"], np.ones((2, 2, 3)))
        },
        coords={
            "geo": ["G1", "G2"],
            "gender": ["m", "f"],
            "age": ["y1", "y2", "y3"]
        }
    )
    macro = MacroData(data=data)
    
    # Marginalize to gender
    gender_marg = macro.get_marginal("gender")
    assert "gender" in gender_marg.dims
    assert "age" not in gender_marg.dims
    # Each gender should have 2 (geos) * 3 (ages) = 6
    assert (gender_marg["count"].values == 6).all()

def test_micro_data_sampling():
    """Test MicroData sampling with weights."""
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "age": [20, 30, 40],
        "p": [0.1, 0.1, 0.8] # 3 is very likely
    })
    micro = MicroData(data=df)
    
    sample = micro.sample(n=100, seed=42)
    assert len(sample) == 100
    # ID 3 should appear most frequently
    assert (sample["id"] == 3).sum() > 50

def test_acs_adapter_population():
    """Test converting Population AcsResult to MacroData."""
    # Mock AcsResult for Population
    est_df = pd.DataFrame({
        "total": [100],
        "m_u5": [10],
        "m_5_9": [15],
        "f_u5": [12],
        "f_5_9": [13]
    }, index=["06041"])
    se_df = est_df * 0.1
    
    result = AcsResult(
        estimates={"age_by_sex": est_df},
        standard_errors={"age_by_sex": se_df},
        metadata={},
        config=PullConfig(year=2022, span=5, geography={}, table_ids=[])
    )
    
    macro = acs_result_to_macro_data(result)
    ds = macro.data
    
    assert "geo" in ds.coords
    assert "gender" in ds.coords
    assert "age" in ds.coords
    assert ds.sel(geo="06041", gender="m", age="u5")["pop_count"] == 10
    assert ds.sel(geo="06041", gender="f", age="5_9")["pop_count"] == 13
