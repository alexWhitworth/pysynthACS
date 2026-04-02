import pandas as pd
from typing import Dict, Any
from pysynthacs.core.base import BasePuller, AcsResult, PullConfig
from pysynthacs.transforms.household import (
    transform_hh_type_r,
    transform_hh_type_units,
    transform_hh_inc,
    transform_hh_occ,
    transform_hh_tenure,
    transform_health_ins
)

class HouseholdPuller(BasePuller):
    """
    Puller for ACS household and housing data.
    Equivalent to R's pull_household().
    """
    TABLE_IDS = ["B09019", "B11011", "B19081", "B25002", "B25003", "B25004", "B25010", 
                 "B25024", "B25056", "B25058", "B25071", "B27001"]

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
        Processes the household data.
        """
        estimates_dict = {}
        se_dict = {}

        for table in self.config.table_ids:
            est_cols = sorted([c for c in df.columns if c.startswith(table) and c.endswith("E")])
            moe_cols = sorted([c for c in df.columns if c.startswith(table) and c.endswith("M")])
            
            if not est_cols:
                continue

            est_table = df[est_cols].copy()
            se_table = df[moe_cols].copy() / 1.645
            
            if table == "B09019":
                est_table, se_table = transform_hh_type_r(est_table, se_table)
            elif table == "B11011":
                est_table, se_table = transform_hh_type_units(est_table, se_table)
            elif table == "B19081":
                est_table, se_table = transform_hh_inc(est_table, se_table)
            elif table == "B25002":
                est_table, se_table = transform_hh_occ(est_table, se_table)
            elif table == "B25003":
                est_table, se_table = transform_hh_tenure(est_table, se_table)
            elif table == "B27001":
                est_table, se_table = transform_health_ins(est_table, se_table)
            
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
        mapping = {
            "B09019": "hh_type_by_relationship",
            "B11011": "hh_type_by_units",
            "B19081": "mean_hh_inc_quintiles",
            "B25002": "hh_occ_status",
            "B25003": "hh_tenure",
            "B25004": "hh_vacancy_status",
            "B25010": "avg_hh_size",
            "B25024": "units_in_structure",
            "B25056": "contract_rent",
            "B25058": "med_rent",
            "B25071": "med_rent_v_inc",
            "B27001": "hh_ins_by_sex_age"
        }
        return mapping.get(table_id, table_id)
