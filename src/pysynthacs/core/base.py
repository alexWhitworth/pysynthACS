from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import pandas as pd
import censusdis.data as ced

@dataclass(frozen=True)
class PullConfig:
    """Immutable configuration for an ACS data pull."""
    year: int
    span: int
    geography: Dict[str, Any]
    table_ids: List[str]
    api_key: Optional[str] = None

from typing import Dict, List, Optional, Any, Union

@dataclass(frozen=True)
class AcsResult:
    """Immutable result of an ACS data pull."""
    estimates: Union[pd.DataFrame, Dict[str, pd.DataFrame]]
    standard_errors: Union[pd.DataFrame, Dict[str, pd.DataFrame]]
    metadata: Dict[str, Any]
    config: PullConfig

class BasePuller(ABC):
    """Abstract base class for all ACS data pullers."""
    def __init__(self, config: PullConfig):
        self.config = config

    def fetch_raw(self) -> pd.DataFrame:
        """
        Fetches raw data from the Census API using censusdis.
        """
        # censusdis.download returns a DataFrame with the requested variables.
        # It typically includes both estimates (E) and margins of error (M).
        # We need to ensure we fetch both.
        variables = []
        for table in self.config.table_ids:
            # This is a simplified logic. 
            # Subclasses might need to specify the exact variables.
            # But censusdis can often handle table IDs directly or we can expand them.
            variables.append(table)
        
        # Note: censusdis.download uses 'download_variables'
        # We might need to map table IDs to variable lists if censusdis doesn't handle them.
        # For now, let's assume table_ids are valid for ced.download or we'll refine this.
        
        df = ced.download(
            dataset="acs/acs5", # Defaulting to ACS5, can be parameterized
            vintage=self.config.year,
            download_variables=self.config.table_ids,
            **self.config.geography
        )
        return df

    @abstractmethod
    def process(self, df: pd.DataFrame) -> AcsResult:
        """
        Processes the raw DataFrame into structured estimates and standard errors.
        """
        pass

    def run(self) -> AcsResult:
        """
        Orchestrates the fetch and process steps.
        """
        raw_df = self.fetch_raw()
        return self.process(raw_df)
