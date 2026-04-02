import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
from pysynthacs.core.education import EducationPuller
from pysynthacs.core.household import HouseholdPuller
from pysynthacs.core.specialized import SpecializedPuller
from pysynthacs.core.base import PullConfig

@pytest.fixture
def mock_edu_df():
    # B14001: 9 vars, B14003: 55 vars, B15001: 81 vars, B15002: 35 vars
    # (Simplified for testing)
    cols = []
    for t, n in [("B14001", 10), ("B14003", 56), ("B15001", 82), ("B15002", 36)]:
        cols += [f"{t}_{i:03d}E" for i in range(1, n+1)]
        cols += [f"{t}_{i:03d}M" for i in range(1, n+1)]
    return pd.DataFrame(np.zeros((1, len(cols))), columns=cols)

@patch("censusdis.data.download")
def test_education_puller(mock_download, mock_edu_df):
    mock_download.return_value = mock_edu_df
    puller = EducationPuller(year=2022, geography={"state": "06"})
    result = puller.run()
    assert "edu_attain25" in result.estimates
    assert "edu_enroll" in result.estimates

@patch("censusdis.data.download")
def test_household_puller(mock_download):
    # Minimal mock for B09019 (needs at least 37 columns based on drops)
    cols = [f"B09019_{i:03d}E" for i in range(1, 40)] + \
           [f"B09019_{i:03d}M" for i in range(1, 40)]
    mock_df = pd.DataFrame(np.zeros((1, len(cols))), columns=cols)
    mock_download.return_value = mock_df
    
    puller = HouseholdPuller(year=2022, geography={"state": "06"}, table_ids=["B09019"])
    result = puller.run()
    assert "hh_type_by_relationship" in result.estimates

def test_specialized_puller():
    # Specialized puller doesn't need a mock if we test .process() directly
    df = pd.DataFrame({
        "B08301_001E": [100], "B08301_001M": [16.45],
        "B08301_002E": [80],  "B08301_002M": [16.45]
    })
    puller = SpecializedPuller(table_ids=["B08301"], name="transit")
    result = puller.process(df)
    assert "B08301" in result.estimates
    assert result.standard_errors["B08301"].iloc[0, 0] == 10.0 # 16.45 / 1.645
