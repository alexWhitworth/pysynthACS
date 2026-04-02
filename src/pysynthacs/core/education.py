import pandas as pd
from typing import Dict, Any
from pysynthacs.core.base import BasePuller, AcsResult, PullConfig
from pysynthacs.transforms.education import (
    transform_edu_enroll,
    transform_enroll_details,
    transform_edu_attain18,
    transform_edu_attain25
)

class EducationPuller(BasePuller):
    """
    Puller for ACS educational attainment and enrollment data.
    Equivalent to R's pull_edu().
    """
    TABLE_IDS = ["B14001", "B14003", "B15001", "B15002"]

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
        Processes the education data.
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
            
            if table == "B14001":
                est_table, se_table = transform_edu_enroll(est_table, se_table)
            elif table == "B14003":
                est_table, se_table = transform_enroll_details(est_table, se_table)
            elif table == "B15001":
                est_table, se_table = transform_edu_attain18(est_table, se_table)
            elif table == "B15002":
                est_table, se_table = transform_edu_attain25(est_table, se_table)
            
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
            "B14001": "edu_enroll",
            "B14003": "enroll_details",
            "B15001": "edu_attain18",
            "B15002": "edu_attain25"
        }
        return mapping.get(table_id, table_id)
