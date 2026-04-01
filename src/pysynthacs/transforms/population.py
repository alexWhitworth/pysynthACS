import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

def transform_age_by_sex(est: pd.DataFrame, se: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Transforms B01001 age by sex table."""
    age_bins = ["", "u5", "5_9", "10_14", "15_17", "18_19", "20", "21", "22_24", "25_29", "30_34",
               "35_39", "40_44", "45_49", "50_54", "55_59", "60_61", "62_64", "65_66", "67_69",
               "70_74", "75_79", "80_84", "85up"]
    
    col_names = ["total"]
    for gender in ["m", "f"]:
        for bin_name in age_bins:
            if bin_name == "":
                col_names.append(gender)
            else:
                col_names.append(f"{gender}_{bin_name}")
    
    # In censusdis, B01001 variables are B01001_001, B01001_002, etc.
    # We should map current column names to these new ones.
    # Assuming columns are already in correct order.
    est.columns = col_names
    se.columns = col_names
    return est, se

def transform_pop_by_race(est: pd.DataFrame, se: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Transforms B02001 population by race table."""
    col_names = ["total", "white", "black_AA", "nat_amer", "asian", "pac_isl", "other"]
    # Only take first 7 variables if more are present (R code does this)
    est = est.iloc[:, :7]
    se = se.iloc[:, :7]
    est.columns = col_names
    se.columns = col_names
    
    # Calculate percentages
    total = est["total"]
    for race in ["white", "black_AA", "nat_amer", "asian", "pac_isl", "other"]:
        est[f"pct_{race}"] = est[race] / total
        
        # Standard error of percentage (approx formula from R code)
        # se_pct = sqrt(se_num^2 - (pct^2 * se_total^2)) / total
        # Note: If total is 0, this might produce NaNs.
        mask = total > 0
        se[f"pct_{race}"] = np.nan
        se.loc[mask, f"pct_{race}"] = np.sqrt(
            np.maximum(0, se.loc[mask, race]**2 - (est.loc[mask, race] / total.loc[mask])**2 * se.loc[mask, "total"]**2)
        ) / total.loc[mask]
        
    return est, se

def transform_med_age(est: pd.DataFrame, se: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Transforms B01002 median age by sex table."""
    col_names = ["total", "male", "female"]
    est.columns = col_names
    se.columns = col_names
    return est, se

# Add other transformations as needed...
