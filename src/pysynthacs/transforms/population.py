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

def transform_birth_and_lang(est: pd.DataFrame, se: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Transforms B06007 place of birth by language."""
    # Logic from R: combines various columns to simplify to 4 origins 
    # (all, citizen_born_out_us, foreign_born, us_born) 
    # x 8 language categories
    origins = ["all", "citizen_born_out_us", "foreign_born", "us_born"]
    langs = ["total", "only_eng", "spk_span", "spk_span_eng_vw", "spk_span_eng_lt_vw",
             "other", "other_eng_vw", "other_eng_lt_vw"]
    
    # R logic involves summing specific columns for 'us_born' (indices 9,17 for total, etc.)
    # In censusdis/B06007: 1-8 is Total, 9-16 is Born in State, 17-24 is Born Out of State, 
    # 25-32 is Native Born outside US, 33-40 is Foreign Born.
    # us_born = Born in State + Born Out of State
    
    # We'll use the indices from the R code as reference but apply them to the DataFrame
    # R indices are 1-based. Python 0-based.
    # us_born total = col 9 + col 17 (R) -> indices 8 + 16 (Python)
    
    est_new = est.iloc[:, 0:32].copy() # placeholder columns
    se_new = se.iloc[:, 0:32].copy()
    
    # Mapping for US Born (sums of In State + Out of State)
    for i in range(8):
        # us_born (last 8 columns in the result)
        col_idx_in_state = 8 + i
        col_idx_out_state = 16 + i
        est_new.iloc[:, 24 + i] = est.iloc[:, col_idx_in_state] + est.iloc[:, col_idx_out_state]
        se_new.iloc[:, 24 + i] = np.sqrt(se.iloc[:, col_idx_in_state]**2 + se.iloc[:, col_idx_out_state]**2)

    # Copy All, Citizen Out, Foreign
    # All: 0-7
    # Citizen Out: 24-31 (R) -> 24-31 (Python) -> wait, let's just re-index cleanly
    final_est = pd.DataFrame(index=est.index)
    final_se = pd.DataFrame(index=se.index)
    
    # all: 0-7
    # citizen_born_out_us: 24-31
    # foreign_born: 32-39
    # us_born: calculated above
    
    # We rename based on the flattened list
    col_names = [f"{o}_{l}" for o in origins for l in langs]
    
    data_map = {
        "all": list(range(0, 8)),
        "citizen_born_out_us": list(range(24, 32)),
        "foreign_born": list(range(32, 40)),
    }
    
    for origin, idxs in data_map.items():
        for i, idx in enumerate(idxs):
            final_est[f"{origin}_{langs[i]}"] = est.iloc[:, idx]
            final_se[f"{origin}_{langs[i]}"] = se.iloc[:, idx]
            
    for i in range(8):
        final_est[f"us_born_{langs[i]}"] = est.iloc[:, 8+i] + est.iloc[:, 16+i]
        final_se[f"us_born_{langs[i]}"] = np.sqrt(se.iloc[:, 8+i]**2 + se.iloc[:, 16+i]**2)
        
    final_est = final_est[col_names]
    final_se = final_se[col_names]
    return final_est, final_se

def transform_marital_status(est: pd.DataFrame, se: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Transforms B06008 place of birth by marital status."""
    origins = ["all", "citizen_born_out_us", "foreign_born", "us_born"]
    statuses = ["total", "nvr_married", "divorced", "separated", "widowed"]
    col_names = [f"{o}_{s}" for o in origins for s in statuses]
    
    # Similar summing logic as above for us_born
    final_est = pd.DataFrame(index=est.index)
    final_se = pd.DataFrame(index=se.index)
    
    data_map = {
        "all": [0, 1, 3, 4, 5], # indices for total, never, divorced, separated, widowed
        "citizen_born_out_us": [18, 19, 21, 22, 23],
        "foreign_born": [24, 25, 27, 28, 29],
    }
    
    for origin, idxs in data_map.items():
        for i, idx in enumerate(idxs):
            final_est[f"{origin}_{statuses[i]}"] = est.iloc[:, idx]
            final_se[f"{origin}_{statuses[i]}"] = se.iloc[:, idx]
            
    # us_born = in state + out state
    in_state_idxs = [6, 7, 9, 10, 11]
    out_state_idxs = [12, 13, 15, 16, 17]
    for i in range(5):
        final_est[f"us_born_{statuses[i]}"] = est.iloc[:, in_state_idxs[i]] + est.iloc[:, out_state_idxs[i]]
        final_se[f"us_born_{statuses[i]}"] = np.sqrt(se.iloc[:, in_state_idxs[i]]**2 + se.iloc[:, out_state_idxs[i]]**2)
        
    return final_est[col_names], final_se[col_names]

def transform_education_pop(est: pd.DataFrame, se: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Transforms B06009 place of birth by education."""
    origins = ["all", "citizen_born_out_us", "foreign_born", "us_born"]
    levels = ["total", "lt_hs", "hs", "some_col", "bachelors", "graduate"]
    col_names = [f"{o}_{l}" for o in origins for l in levels]
    
    final_est = pd.DataFrame(index=est.index)
    final_se = pd.DataFrame(index=se.index)
    
    data_map = {
        "all": list(range(0, 6)),
        "citizen_born_out_us": list(range(18, 24)),
        "foreign_born": list(range(24, 30)),
    }
    
    for origin, idxs in data_map.items():
        for i, idx in enumerate(idxs):
            final_est[f"{origin}_{levels[i]}"] = est.iloc[:, idx]
            final_se[f"{origin}_{levels[i]}"] = se.iloc[:, idx]
            
    for i in range(6):
        final_est[f"us_born_{levels[i]}"] = est.iloc[:, 6+i] + est.iloc[:, 12+i]
        final_se[f"us_born_{levels[i]}"] = np.sqrt(se.iloc[:, 6+i]**2 + se.iloc[:, 12+i]**2)
        
    return final_est[col_names], final_se[col_names]

def transform_income_pop(est: pd.DataFrame, se: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Transforms B06010 place of birth by income."""
    origins = ["all", "citizen_born_out_us", "foreign_born", "us_born"]
    brackets = ["total", "no_inc", "1_lt10k", "10k_lt15k", "15k_lt25k", "25k_lt35k", 
                "35k_lt50k", "50k_lt_65k", "65k_lt75k", "gt75k"]
    col_names = [f"{o}_{b}" for o in origins for b in brackets]
    
    final_est = pd.DataFrame(index=est.index)
    final_se = pd.DataFrame(index=se.index)
    
    # R indices mapping to these brackets
    # all: 1, 2, 4-11 (R) -> 0, 1, 3-10 (Python)
    # citizen: 34, 35, 37-46 (R) -> 33, 34, 36-45 (Python)
    # foreign: 47-56 (R) -> 46-55 (Python)
    
    data_map = {
        "all": [0, 1] + list(range(3, 11)),
        "citizen_born_out_us": [33, 34] + list(range(36, 44)),
        "foreign_born": list(range(44, 54)),
    }
    
    for origin, idxs in data_map.items():
        for i, idx in enumerate(idxs):
            final_est[f"{origin}_{brackets[i]}"] = est.iloc[:, idx]
            final_se[f"{origin}_{brackets[i]}"] = se.iloc[:, idx]
            
    in_state = [11, 12] + list(range(14, 22))
    out_state = [22, 23] + list(range(25, 33))
    for i in range(10):
        final_est[f"us_born_{brackets[i]}"] = est.iloc[:, in_state[i]] + est.iloc[:, out_state[i]]
        final_se[f"us_born_{brackets[i]}"] = np.sqrt(se.iloc[:, in_state[i]]**2 + se.iloc[:, out_state[i]]**2)
        
    return final_est[col_names], final_se[col_names]

def transform_poverty_pop(est: pd.DataFrame, se: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Transforms B06012 place of birth by poverty status."""
    origins = ["all", "citizen_born_out_us", "foreign_born", "us_born"]
    levels = ["total", "0_lt100pct_pov_lvl", "100_lt150pct_pov_lvl", "gt150pct_pov_lvl"]
    col_names = [f"{o}_{l}" for o in origins for l in levels]
    
    final_est = pd.DataFrame(index=est.index)
    final_se = pd.DataFrame(index=se.index)
    
    data_map = {
        "all": list(range(0, 4)),
        "citizen_born_out_us": list(range(12, 16)),
        "foreign_born": list(range(16, 20)),
    }
    
    for origin, idxs in data_map.items():
        for i, idx in enumerate(idxs):
            final_est[f"{origin}_{levels[i]}"] = est.iloc[:, idx]
            final_se[f"{origin}_{levels[i]}"] = se.iloc[:, idx]
            
    for i in range(4):
        final_est[f"us_born_{levels[i]}"] = est.iloc[:, 4+i] + est.iloc[:, 8+i]
        final_se[f"us_born_{levels[i]}"] = np.sqrt(se.iloc[:, 4+i]**2 + se.iloc[:, 8+i]**2)
        
    return final_est[col_names], final_se[col_names]
