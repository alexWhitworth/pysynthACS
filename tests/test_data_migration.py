import pytest
import pandas as pd
from pathlib import Path

def test_parquet_migration_integrity():
    """Verify that the migrated parquet files exist and are readable."""
    data_dir = Path("src/pysynthacs/data")
    parquet_files = list(data_dir.glob("*.parquet"))
    
    assert len(parquet_files) >= 9 # We had 9 .rda files
    
    # Check a specific file for expected content
    # TFR.rda (Total Fertility Rate) should have specific columns
    tfr_path = data_dir / "TFR.parquet"
    assert tfr_path.exists()
    
    df = pd.read_parquet(tfr_path)
    assert not df.empty
    # Expect columns like 'year', 'state', or similar based on synthACS original data
    assert len(df.columns) > 0
    
    # Check adjDR (Adjusted Death Rates)
    adj_dr_path = data_dir / "adjDR.parquet"
    assert adj_dr_path.exists()
    df_dr = pd.read_parquet(adj_dr_path)
    assert not df_dr.empty
