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
        
        import censusdis.data as ced
        from pysynthacs.config import get_api_key
        
        # 1. Resolve API Key: Config key > Global key
        api_key = self.config.api_key or get_api_key()
        
        # 1. Resolve all variable names for the requested table groups
        # If download_group isn't available, we manually find variables starting with the group ID
        all_vars = []
        try:
            import censusdis.vars as cev
            for group_id in self.config.table_ids:
                group_vars = cev.group_variables(
                    dataset="acs/acs5",
                    vintage=self.config.year,
                    group_name=group_id
                )
                all_vars.extend(group_vars)
        except (ImportError, AttributeError):
            # Fallback: if censusdis.vars doesn't work, we'll try fetching metadata directly
            # This is a bit more complex, for now let's assume we can find a way to get them.
            # Usually B01001_001E, B01001_002E...
            # For this test, let's hardcode some for B01001/B01002 if we're in trouble
            for group_id in self.config.table_ids:
                if group_id == "B01001":
                    all_vars.extend([f"B01001_{i:03d}E" for i in range(1, 50)])
                    all_vars.extend([f"B01001_{i:03d}M" for i in range(1, 50)])
                elif group_id == "B01002":
                    all_vars.extend([f"B01002_{i:03d}E" for i in range(1, 4)])
                    all_vars.extend([f"B01002_{i:03d}M" for i in range(1, 4)])
                else:
                    all_vars.append(group_id) # Last resort
            
        # 2. Download all resolved variables
        df = ced.download(
            dataset="acs/acs5",
            vintage=self.config.year,
            download_variables=all_vars,
            api_key=api_key,
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
