import pandas as pd
import numpy as np
from typing import Dict, Any, List
from pysynthacs.core.base import BasePuller, AcsResult, PullConfig
from pysynthacs.transforms.population import (
    transform_age_by_sex, 
    transform_med_age, 
    transform_pop_by_race
)

class PopulationPuller(BasePuller):
    """
    Puller for ACS population data.
    Equivalent to R's pull_population().
    """
    TABLE_IDS = ["B01001", "B01002", "B02001", "B06007", "B06008", "B06009", "B06010", "B06011", "B06012"]

    def __init__(self, config: PullConfig = None, **kwargs):
        if config is None:
            config = PullConfig(
                year=kwargs.get("year", 2022),
                span=kwargs.get("span", 5),
                geography=kwargs.get("geography", {}),
                table_ids=self.TABLE_IDS,
                api_key=kwargs.get("api_key")
            )
        super().__init__(config)

    def process(self, df: pd.DataFrame) -> AcsResult:
        """
        Processes the population data by splitting into tables and applying transformations.
        """
        # Dictionary of tables (Estimate and Margin of Error separately)
        estimates_dict = {}
        se_dict = {}

        for table in self.config.table_ids:
            # Table extraction: we expect columns like B01001_001E, B01001_001M...
            est_cols = sorted([c for c in df.columns if c.startswith(table) and c.endswith("E")])
            moe_cols = sorted([c for c in df.columns if c.startswith(table) and c.endswith("M")])
            
            if not est_cols:
                continue

            est_table = df[est_cols].copy()
            se_table = df[moe_cols].copy() / 1.645
            
            # Apply specific transformation based on table ID
            if table == "B01001":
                est_table, se_table = transform_age_by_sex(est_table, se_table)
            elif table == "B01002":
                est_table, se_table = transform_med_age(est_table, se_table)
            elif table == "B02001":
                est_table, se_table = transform_pop_by_race(est_table, se_table)
            # Add other table handlers...
            
            table_name = self._get_table_name(table)
            estimates_dict[table_name] = est_table
            se_dict[table_name] = se_table

        return AcsResult(
            estimates=estimates_dict,
            standard_errors=se_dict,
            metadata={"source": "ACS5", "tables": self.config.table_ids},
            config=self.config
        )

    def _get_table_name(self, table_id: str) -> str:
        """Mapping table IDs to human-readable names."""
        mapping = {
            "B01001": "age_by_sex",
            "B01002": "median_age_by_sex",
            "B02001": "pop_by_race",
            "B06007": "birth_and_lang",
            "B06008": "marital_status",
            "B06009": "education",
            "B06010": "income",
            "B06011": "median_income",
            "B06012": "poverty_status"
        }
        return mapping.get(table_id, table_id)
