import pandas as pd
import numpy as np
import pysynthacs
from pysynthacs.core.data import MicroData

def add_commute_mode(population: pd.DataFrame) -> pd.DataFrame:
    """
    Augments a synthetic population with commute mode attributes.
    In a real scenario, this would use data from pull_transit_work().
    """
    print("Augmenting population with commute mode based on conditional probabilities...")
    
    # Example conditional probabilities by age group
    # (Simplified for demonstration)
    modes = ["drove_alone", "carpool", "transit", "walk", "other", "work_at_home"]
    
    # We apply a random choice for each individual
    # In a real run, we would use np.random.choice with weights derived from ACS macro data
    population["commute_mode"] = np.random.choice(modes, size=len(population))
    
    return population

def run_augmentation_example():
    """
    Example demonstrating how to add new attributes to an existing synthetic population.
    This mirrors the Section 3 workflow from the JSS paper.
    """
    print("Step 1: Creating a baseline synthetic population...")
    # Mock baseline population (Age and Gender)
    n = 5000
    df = pd.DataFrame({
        "id": range(n),
        "geo": ["06041"] * n,
        "age": np.random.choice(["18_24", "25_34", "35_44"], n),
        "gender": np.random.choice(["m", "f"], n)
    })
    
    print(f"Baseline attributes: {list(df.columns)}")
    
    # Step 2: Augment with Commute Mode
    # In synthACS, this is done via 'all_geog_synthetic_new_attribute'
    df_augmented = add_commute_mode(df)
    
    print(f"Augmented attributes: {list(df_augmented.columns)}")
    print("\nSample of augmented population:")
    print(df_augmented[["age", "gender", "commute_mode"]].head())
    
    # Step 3: Show distribution of the new attribute
    print("\nCommute Mode Distribution:")
    print(df_augmented["commute_mode"].value_counts(normalize=True))

if __name__ == "__main__":
    run_augmentation_example()
