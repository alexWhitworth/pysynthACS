import pandas as pd
import numpy as np
from pathlib import Path
import pysynthacs
from pysynthacs.core.generator import SyntheticGenerator
from pysynthacs.core.data import MicroData
import time

def run_large_scale_example():
    """
    Demonstrates synthetic population generation across multiple geographies (all tracts in a county).
    This showcases the speed of the Rust optimization engine.
    """
    # 1. Setup API Key
    api_key_path = Path("api_key.txt")
    if api_key_path.exists():
        with open(api_key_path, "r") as f:
            pysynthacs.set_api_key(f.read().strip())
    else:
        print("api_key.txt not found. Please set CENSUS_API_KEY environment variable.")
        return

    # 2. Pull Macro Data for all tracts in Marin County, CA (06041)
    print("Step 1: Pulling Census data for all tracts in Marin County...")
    gen = SyntheticGenerator(year=2022)
    # Using '*' for tract pulls all tracts in the specified county
    start_time = time.time()
    macro = gen.pull_macro(geography={"state": "06", "county": "041", "tract": "*"})
    pull_time = time.time() - start_time
    
    num_tracts = len(macro.geography)
    print(f"Successfully pulled data for {num_tracts} census tracts in {pull_time:.2f} seconds.")
    
    # 3. Prepare a large candidate pool (MicroData)
    print("Step 2: Preparing candidate pool...")
    n_pool = 20000
    pool_df = pd.DataFrame({
        "id": range(n_pool),
        "category": np.random.randint(0, 48, n_pool) # Matching the 48 age/sex bins
    })
    micro = MicroData(data=pool_df)
    
    # 4. Generate Synthetic Populations for all tracts
    print(f"Step 3: Optimizing populations for {num_tracts} tracts (Rust Core)...")
    start_time = time.time()
    # We use a moderate max_iter to show speed across many areas
    full_synthetic_pop = gen.generate(macro, micro, max_iter=10000)
    opt_time = time.time() - start_time
    
    total_people = len(full_synthetic_pop)
    print(f"\nOptimization Results:")
    print(f"Total Geographies: {num_tracts}")
    print(f"Total Synthetic Population: {total_people:,}")
    print(f"Total Time: {opt_time:.2f} seconds")
    print(f"Average Time per Tract: {opt_time/num_tracts:.4f} seconds")
    
    print("\nSample of final synthetic population:")
    print(full_synthetic_pop.head())

if __name__ == "__main__":
    run_large_scale_example()
