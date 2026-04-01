import pandas as pd
import numpy as np
from typing import List, Union

def sum_columns(df: pd.DataFrame, cols: List[str], new_col_name: str) -> pd.DataFrame:
    """Sums multiple columns and creates a new one."""
    df[new_col_name] = df[cols].sum(axis=1)
    return df

def sum_se_columns(se_df: pd.DataFrame, cols: List[str], new_col_name: str) -> pd.DataFrame:
    """Sums multiple standard error columns (sqrt of sum of squares)."""
    se_df[new_col_name] = np.sqrt((se_df[cols]**2).sum(axis=1))
    return se_df
