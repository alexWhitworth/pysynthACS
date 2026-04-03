import pytest
import pandas as pd
import numpy as np
import xarray as xr
from pysynthacs.core.data import MacroData
from pysynthacs.core.diagnostics import calculate_tae, validate_marginals

def test_calculate_tae():
    """Test TAE calculation logic."""
    data = xr.Dataset(
        data_vars={"pop_count": (["geo", "gender", "age"], np.full((1, 2, 2), 5))},
        coords={"geo": ["G1"], "gender": ["m", "f"], "age": ["y1", "y2"]}
    )
    macro = MacroData(data=data)
    
    # Perfectly matching synthetic pop (total 20)
    syn_pop = pd.DataFrame({
        "geo": ["G1"] * 20,
        "category": [0, 1, 2, 3] * 5 # 5 in each of the 4 bins
    })
    
    tae = calculate_tae(syn_pop, macro)
    assert tae == 0
    
    # Non-matching (total 20, but shifted)
    syn_pop_bad = pd.DataFrame({
        "geo": ["G1"] * 20,
        "category": [0] * 20 # All in first bin
    })
    # Target: [5, 5, 5, 5]. Actual: [20, 0, 0, 0].
    # Diff: [15, 5, 5, 5]. Sum = 30.
    tae_bad = calculate_tae(syn_pop_bad, macro)
    assert tae_bad == 30

def test_validate_marginals():
    """Test marginal comparison table generation."""
    data = xr.Dataset(
        data_vars={"pop_count": (["geo", "gender", "age"], np.full((1, 2, 2), 5))},
        coords={"geo": ["G1"], "gender": ["m", "f"], "age": ["y1", "y2"]}
    )
    macro = MacroData(data=data)
    syn_pop = pd.DataFrame({
        "geo": ["G1"] * 20,
        "category": [0] * 20
    })
    
    df = validate_marginals(syn_pop, macro)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 4 # 4 bins
    assert df.loc[df["bin_idx"] == 0, "syn_count"].values[0] == 20
    assert df.loc[df["bin_idx"] == 1, "syn_count"].values[0] == 0
