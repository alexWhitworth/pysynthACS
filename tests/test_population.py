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
