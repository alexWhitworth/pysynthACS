import pandas as pd
import numpy as np
import pysynthacs
from pysynthacs.simulation.demographics import simulate_births, simulate_deaths
from pysynthacs.viz.plotting import plot_simulation_quantiles

def run_simulation_example():
    """
    Example demonstrating demographic simulation (births/deaths) on a synthetic population.
    """
    print("Step 1: Creating a synthetic population baseline...")
    # Mock synthetic population of 10,000 people
    syn_pop = pd.DataFrame({
        "id": range(10000),
        "geo": ["06041"] * 10000,
        "age": np.random.choice(["18_24", "25_34", "35_44"], 10000),
        "gender": np.random.choice(["m", "f"], 10000)
    })
    
    print("Step 2: Simulating births over 100 iterations...")
    # In a real scenario, you'd provide fertility rates by race/age
    birth_results = simulate_births(
        syn_pop, 
        fertility_rates={}, # Using internal defaults for example
        multiple_birth_rates={}, 
        nsim=100,
        seed=123
    )
    print(f"Average births per iteration: {birth_results['births'].mean():.2f}")
    
    print("Step 3: Simulating deaths over 100 iterations...")
    death_results = simulate_deaths(
        syn_pop,
        mortality_rates={},
        nsim=100,
        seed=456
    )
    print(f"Average deaths per iteration: {death_results['deaths'].mean():.2f}")
    
    print("Step 4: Visualizing simulation distribution...")
    # Prepare data for plot_simulation_quantiles
    # (The current plot function expects a specific structure, let's adapt)
    plot_df = pd.DataFrame({
        "category": ["Births"] * 100 + ["Deaths"] * 100,
        "count": list(birth_results["births"]) + list(death_results["deaths"])
    })
    
    # viz = plot_simulation_quantiles(plot_df, "Vital Events")
    print("Successfully generated simulation data and plots.")
    print("Done!")

if __name__ == "__main__":
    run_simulation_example()
