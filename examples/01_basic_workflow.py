import pandas as pd
import numpy as np
from pathlib import Path
import pysynthacs
from pysynthacs.core.generator import SyntheticGenerator
from pysynthacs.core.data import MicroData
from pysynthacs.core.diagnostics import validate_marginals
from pysynthacs.viz.plotting import plot_tae_convergence, plot_demographic_fit

def run_example():
    """
    End-to-end example using real Census data for Marin County, CA.
    """
    # 1. Setup API Key (Optional: set via ENV or set_api_key)
    api_key_path = Path("api_key.txt")
    if api_key_path.exists():
        with open(api_key_path, "r") as f:
            pysynthacs.set_api_key(f.read().strip())
    else:
        print("api_key.txt not found. Please set CENSUS_API_KEY environment variable.")
        return

    # 2. Pull Macro Data (Marin County, CA)
    print("Step 1: Pulling Census data for Marin County...")
    gen = SyntheticGenerator(year=2022)
    macro = gen.pull_macro(geography={"state": "06", "county": "041"})
    
    # 3. Load/Create Candidate Pool (MicroData)
    # For this example, we create a synthetic pool of 10,000 individuals
    print("Step 2: Preparing candidate pool...")
    n_pool = 10000
    pool_df = pd.DataFrame({
        "id": range(n_pool),
        "category": np.random.randint(0, 48, n_pool) # Matching the 48 age/sex bins
    })
    micro = MicroData(data=pool_df)
    
    # 4. Generate Synthetic Population
    print("Step 3: Optimizing synthetic population (Rust Core)...")
    # We'll use a small subset of iterations for the example
    # Set return_diagnostics=True to get the TAE path for plotting
    synthetic_pop, diags = gen.generate(macro, micro, max_iter=10000, return_diagnostics=True)
    
    print(f"Generated synthetic population with {len(synthetic_pop)} individuals.")
    
    # 5. Diagnostics
    print("Step 4: Running diagnostics...")
    comp_df = validate_marginals(synthetic_pop, macro)
    print("\nSample Fit Comparison:")
    print(comp_df.head())
    
    # 6. Visualization
    print("Step 5: Visualizing results...")
    # Get diagnostics for the first geography
    geo = macro.geography[0]
    result = diags[geo]
    
    # These generate plot objects from plotnine
    convergence_plot = plot_tae_convergence(result.tae_path)
    fit_plot = plot_demographic_fit(comp_df)
    
    print(f"Successfully generated plots for {geo}.")
    print(f"Final TAE: {result.final_tae}")
    print("Done! Plots can be saved using convergence_plot.save() and fit_plot.save().")

if __name__ == "__main__":
    run_example()
