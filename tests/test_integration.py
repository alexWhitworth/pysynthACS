import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from pysynthacs.core.population import PopulationPuller
from pysynthacs_core import optimize_population

@pytest.mark.integration
def test_live_census_pull_and_optimize():
    """
    Integration test: Pulls real data for Marin County, CA (06041)
    and runs a sample optimization.
    """
    # 1. Setup API Key from root api_key.txt
    api_key_path = Path("api_key.txt")
    if not api_key_path.exists():
        pytest.skip("api_key.txt not found, skipping integration test.")
        
    with open(api_key_path, "r") as f:
        api_key = f.read().strip()
    
    import pysynthacs
    pysynthacs.set_api_key(api_key)
    
    # 2. Pull real population data (Marin County, CA)
    # Marin County: state 06, county 041
    # We'll pull a subset of tables to keep it fast
    puller = PopulationPuller(
        year=2022, 
        geography={"state": "06", "county": "041"}
    )
    
    # Restrict to just a few tables for the test to avoid huge downloads
    puller.config = puller.config.__class__(
        **{**puller.config.__dict__, 'table_ids': ["B01001", "B01002"]}
    )
    
    print("\nFetching real Census data for Marin County...")
    result = puller.run()
    
    # 3. Verify real data structure
    assert "age_by_sex" in result.estimates
    df_age = result.estimates["age_by_sex"]
    assert not df_age.empty
    
    # 4. Run Rust Optimization on real data slice
    # Goal: Match the age/sex marginals from Marin County
    # n_sample is the real population count
    n_sample = int(df_age["total"].iloc[0])
    
    # Create a small synthetic pool (e.g., 5000 people)
    n_pool = 5000
    n_attr = 1 
    
    # Categories 0-48 (match the 49 age/sex bins, skipping 'total' at index 0)
    pool = np.random.randint(0, 48, size=(n_pool, n_attr), dtype=np.int32)
    
    # Target counts from real Census data (drop 'total' column)
    # Note: df_age column 0 is 'total', columns 1-49 are the bins
    real_targets = df_age.iloc[0, 1:49].values.astype(np.float64)
    # Normalize real targets to a smaller sample size for the test (e.g., 500)
    test_sample_size = 500
    normalized_targets = (real_targets / real_targets.sum() * test_sample_size).astype(np.int32)
    # Adjust for rounding to ensure sum exactly matches test_sample_size
    diff = test_sample_size - normalized_targets.sum()
    normalized_targets[0] += diff
    
    targets = [normalized_targets]
    
    print(f"Running optimization for test sample size: {test_sample_size} (normalized from {n_sample})...")
    opt_result = optimize_population(
        pool_data=pool,
        target_constraints=targets,
        sample_size=test_sample_size,
        max_iter=5000 
    )
    
    assert opt_result.final_tae >= 0
    assert len(opt_result.best_indices) == test_sample_size
    print(f"Integration Success: Final TAE = {opt_result.final_tae}")
