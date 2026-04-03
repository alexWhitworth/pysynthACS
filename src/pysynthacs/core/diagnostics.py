import numpy as np
import pandas as pd
import xarray as xr
from typing import Dict, List, Any, Union
from pysynthacs.core.data import MacroData

def calculate_tae(synthetic_pop: pd.DataFrame, macro: MacroData) -> int:
    """
    Calculates Total Absolute Error (TAE) for a synthetic population 
    against its macro constraints.
    """
    ds = macro.data
    total_tae = 0
    
    # Iterate through each geography in the macro data
    for geo in macro.geography:
        geo_pop = synthetic_pop[synthetic_pop["geo"] == geo]
        if geo_pop.empty:
            continue
            
        target_ds = ds.sel(geo=geo)
        
        # 1. Compare Age/Gender (B01001)
        if "pop_count" in ds.data_vars:
            # We assume synthetic_pop has 'age' and 'gender' columns matching macro coords
            # This is a simplified validation for now.
            # In a real run, the 'category' would need to be mapped back.
            # For diagnostics, we can use the counts of categories.
            target_counts = target_ds["pop_count"].values.flatten()
            
            # Map synthetic pop to same bins
            # (Assuming synthetic_pop has a 'category' col used during generation)
            if "category" in geo_pop.columns:
                syn_counts = geo_pop["category"].value_counts().reindex(range(len(target_counts)), fill_value=0).values
                total_tae += np.abs(target_counts - syn_counts).sum()
                
    return int(total_tae)

def validate_marginals(synthetic_pop: pd.DataFrame, macro: MacroData) -> pd.DataFrame:
    """
    Returns a comparison table of synthetic counts vs macro totals for all attributes.
    """
    ds = macro.data
    comparisons = []
    
    for geo in macro.geography:
        geo_pop = synthetic_pop[synthetic_pop["geo"] == geo]
        target_ds = ds.sel(geo=geo)
        
        # Example for age/gender
        if "pop_count" in ds.data_vars:
            # Flatten target
            target_vals = target_ds["pop_count"].values.flatten()
            # Get synthetic counts
            if "category" in geo_pop.columns:
                syn_counts = geo_pop["category"].value_counts().reindex(range(len(target_vals)), fill_value=0).values
                
                for i, (t, s) in enumerate(zip(target_vals, syn_counts)):
                    comparisons.append({
                        "geo": geo,
                        "attribute": "age_gender",
                        "bin_idx": i,
                        "macro_count": t,
                        "syn_count": s,
                        "abs_diff": abs(t - s)
                    })
                    
    return pd.DataFrame(comparisons)
