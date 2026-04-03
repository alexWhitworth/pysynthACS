import pandas as pd
import xarray as xr
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import numpy as np

@dataclass(frozen=True)
class MacroData:
    """
    Multi-dimensional container for macro-demographic data.
    Wraps an xarray.Dataset.
    """
    data: xr.Dataset
    
    @property
    def geography(self) -> List[str]:
        """Returns the list of geographies in this dataset."""
        return list(self.data.coords["geo"].values)

    def get_marginal(self, dim: str) -> xr.DataArray:
        """Returns the marginal distribution for a specific dimension."""
        return self.data.sum(dim=[d for d in self.data.dims if d != dim])

    def to_parquet(self, path: str):
        """Serializes the data cube to a directory of parquet files or a single netCDF."""
        # xarray to netcdf is standard, but user requested parquet for pandas.
        # For xarray, we might prefer zarr or netcdf, but let's provide a way to 
        # export to a flattened dataframe if they want parquet.
        self.data.to_dataframe().to_parquet(path)

@dataclass(frozen=True)
class MicroData:
    """
    Container for candidate individuals (e.g., from PUMS).
    Wraps a pandas.DataFrame.
    """
    data: pd.DataFrame
    
    def __post_init__(self):
        if "p" not in self.data.columns:
            # Add uniform probability if not present
            object.__setattr__(self, 'data', self.data.assign(p=1.0/len(self.data)))

    def sample(self, n: int, seed: Optional[int] = None) -> pd.DataFrame:
        """Samples n individuals from the pool."""
        return self.data.sample(n=n, weights="p", random_state=seed, replace=True)
