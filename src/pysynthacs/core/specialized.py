import pandas as pd
from typing import Dict, Any, List
from pysynthacs.core.base import BasePuller, AcsResult, PullConfig

class SpecializedPuller(BasePuller):
    """
    A flexible puller for smaller ACS table groups (Transit, Mobility, etc.).
    """
    def __init__(self, table_ids: List[str], name: str, config: PullConfig = None, **kwargs):
        if config is None:
            config = PullConfig(
                year=kwargs.get("year", 2022),
                span=kwargs.get("span", 5),
                geography=kwargs.get("geography", {}),
                table_ids=table_ids,
                api_key=kwargs.get("api_key")
            )
        self.name = name
        super().__init__(config)

    def process(self, df: pd.DataFrame) -> AcsResult:
        estimates_dict = {}
        se_dict = {}

        for table in self.config.table_ids:
            est_cols = sorted([c for c in df.columns if c.startswith(table) and c.endswith("E")])
            moe_cols = sorted([c for c in df.columns if c.startswith(table) and c.endswith("M")])
            
            if est_cols:
                estimates_dict[table] = df[est_cols].copy()
                se_dict[table] = df[moe_cols].copy() / 1.645

        return AcsResult(
            estimates=estimates_dict,
            standard_errors=se_dict,
            metadata={"source": "ACS5", "group": self.name},
            config=self.config
        )
