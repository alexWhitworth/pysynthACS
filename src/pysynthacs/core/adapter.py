import pandas as pd
import xarray as xr
import numpy as np
from typing import Dict, Any
from pysynthacs.core.base import AcsResult
from pysynthacs.core.data import MacroData

def acs_result_to_macro_data(result: AcsResult) -> MacroData:
    """
    Converts an AcsResult (dict of DataFrames) into a multi-dimensional MacroData (xarray).
    """
    datasets = []
    
    # Process age_by_sex (B01001)
    if "age_by_sex" in result.estimates:
        est = result.estimates["age_by_sex"]
        se = result.standard_errors["age_by_sex"]
        
        # B01001 mapping:
        # columns 1-24 are male (total + bins), 25-48 are female (total + bins)
        # index 0 is total
        
        age_bins = ["u5", "5_9", "10_14", "15_17", "18_19", "20", "21", "22_24", 
                    "25_29", "30_34", "35_39", "40_44", "45_49", "50_54", "55_59", 
                    "60_61", "62_64", "65_66", "67_69", "70_74", "75_79", "80_84", "85up"]
        
        # Create coordinates
        geos = est.index.tolist()
        genders = ["m", "f"]
        
        # Data shape: (geos, gender, age)
        data_shape = (len(geos), len(genders), len(age_bins))
        est_arr = np.zeros(data_shape)
        se_arr = np.zeros(data_shape)
        
        for i, gender in enumerate(genders):
            for j, age in enumerate(age_bins):
                col_name = f"{gender}_{age}"
                if col_name in est.columns:
                    est_arr[:, i, j] = est[col_name].values
                    se_arr[:, i, j] = se[col_name].values
        
        ds_age = xr.Dataset(
            data_vars={
                "pop_count": (["geo", "gender", "age"], est_arr),
                "pop_se": (["geo", "gender", "age"], se_arr),
            },
            coords={
                "geo": geos,
                "gender": genders,
                "age": age_bins
            }
        )
        datasets.append(ds_age)

    # Process pop_by_race (B02001)
    if "pop_by_race" in result.estimates:
        est = result.estimates["pop_by_race"]
        se = result.standard_errors["pop_by_race"]
        
        races = ["white", "black_AA", "nat_amer", "asian", "pac_isl", "other"]
        geos = est.index.tolist()
        
        est_arr = est[races].values
        se_arr = se[races].values
        
        ds_race = xr.Dataset(
            data_vars={
                "race_count": (["geo", "race"], est_arr),
                "race_se": (["geo", "race"], se_arr),
            },
            coords={
                "geo": geos,
                "race": races
            }
        )
        datasets.append(ds_race)

    # Merge all datasets into one
    if not datasets:
        return MacroData(data=xr.Dataset())
        
    full_ds = xr.merge(datasets)
    return MacroData(data=full_ds)
