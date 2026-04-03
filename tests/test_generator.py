import pytest
import pandas as pd
import xarray as xr
import numpy as np
from pysynthacs.core.generator import SyntheticGenerator
from pysynthacs.core.data import MacroData, MicroData

def test_synthetic_generator_full_flow():
    """Test the full flow from Macro/Micro data to Synthetic Population."""
    # 1. Create Mock MacroData (2 geographies, 2 genders, 3 ages)
    # Total pop = 10 per geo
    data = xr.Dataset(
        data_vars={
            "pop_count": (["geo", "gender", "age"], np.full((2, 2, 3), 2))
        },
        coords={
            "geo": ["G1", "G2"],
            "gender": ["m", "f"],
            "age": ["y1", "y2", "y3"]
        }
    )
    # Flattened bins = 2 * 3 = 6 bins. Total pop = 6 * 2 = 12 per geo.
    macro = MacroData(data=data)
    
    # 2. Create Mock MicroData (Pool of 100 people)
    # Categories 0-5 (matching the 6 bins in macro)
    pool_df = pd.DataFrame({
        "id": range(100),
        "category": np.random.randint(0, 6, 100)
    })
    micro = MicroData(data=pool_df)
    
    # 3. Generate
    gen = SyntheticGenerator(year=2022)
    syn_pop = gen.generate(macro, micro, max_iter=1000)
    
    # 4. Verify
    assert isinstance(syn_pop, pd.DataFrame)
    assert len(syn_pop) == 24 # 12 per geo * 2 geos
    assert "geo" in syn_pop.columns
    assert set(syn_pop["geo"]) == {"G1", "G2"}
    
    # Check that counts roughly match (stochastic, but with 1000 iters should be close)
    g1_pop = syn_pop[syn_pop["geo"] == "G1"]
    assert len(g1_pop) == 12
