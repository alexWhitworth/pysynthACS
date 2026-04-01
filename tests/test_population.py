import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
from pysynthacs.core.population import PopulationPuller
from pysynthacs.core.base import PullConfig

@pytest.fixture
def mock_census_df():
    """Creates a mock DataFrame similar to what censusdis would return."""
    # Table B01001 has 49 variables
    b01001_cols = [f"B01001_{i:03d}E" for i in range(1, 50)] + \
                  [f"B01001_{i:03d}M" for i in range(1, 50)]
    # Table B01002 has 3 variables
    b01002_cols = [f"B01002_{i:03d}E" for i in range(1, 4)] + \
                  [f"B01002_{i:03d}M" for i in range(1, 4)]
    # Table B02001 has 7 variables
    b02001_cols = [f"B02001_{i:03d}E" for i in range(1, 10)] + \
                  [f"B02001_{i:03d}M" for i in range(1, 10)]
    
    all_cols = b01001_cols + b01002_cols + b02001_cols
    df = pd.DataFrame(np.random.randint(0, 1000, size=(1, len(all_cols))), columns=all_cols)
    return df

from pysynthacs.transforms.population import (
    transform_age_by_sex,
    transform_pop_by_race,
    transform_med_age
)

def test_transform_age_by_sex():
    """Verify B01001 transformation renaming."""
    df = pd.DataFrame(np.zeros((1, 49)))
    se = pd.DataFrame(np.zeros((1, 49)))
    
    est, se_res = transform_age_by_sex(df, se)
    assert est.columns[0] == "total"
    assert est.columns[1] == "m"
    assert est.columns[2] == "m_u5"
    assert est.columns[25] == "f"
    assert est.columns[48] == "f_85up"

def test_transform_pop_by_race():
    """Verify B02001 race percentages and SEs."""
    # 9 columns (we only use first 7)
    df = pd.DataFrame({
        "total": [100.0],
        "white": [60.0],
        "black": [20.0],
        "nat_amer": [5.0],
        "asian": [10.0],
        "pac_isl": [2.0],
        "other": [3.0],
        "extra1": [0],
        "extra2": [0]
    })
    se = pd.DataFrame(np.ones((1, 9))) # All SEs are 1.0
    
    est, se_res = transform_pop_by_race(df, se)
    
    assert est.loc[0, "pct_white"] == 0.6
    assert est.loc[0, "pct_black_AA"] == 0.2
    # Verify SE calculation for a percentage
    # formula: sqrt(se_num^2 - (pct^2 * se_total^2)) / total
    # for white: sqrt(1^2 - (0.6^2 * 1^2)) / 100 = sqrt(1 - 0.36) / 100 = 0.8 / 100 = 0.008
    assert pytest.approx(se_res.loc[0, "pct_white"]) == 0.008

@patch("censusdis.data.download")
def test_population_puller_process(mock_download, mock_census_df):
    mock_download.return_value = mock_census_df
    
    config = PullConfig(
        year=2022,
        span=5,
        geography={"state": "06"},
        table_ids=["B01001", "B01002", "B02001"]
    )
    
    puller = PopulationPuller(config)
    result = puller.run()
    
    assert isinstance(result.estimates, dict)
    assert "age_by_sex" in result.estimates
    assert "median_age_by_sex" in result.estimates
    assert "pop_by_race" in result.estimates
    
    # Check dimensions
    assert result.estimates["age_by_sex"].shape[1] == 49
    assert result.estimates["median_age_by_sex"].shape[1] == 3
    assert result.estimates["pop_by_race"].shape[1] == 7 + 6 # 7 original + 6 percentages
    
    # Check column names
    assert "total" in result.estimates["age_by_sex"].columns
    assert "m_u5" in result.estimates["age_by_sex"].columns
    assert "pct_white" in result.estimates["pop_by_race"].columns
