from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from pysynthacs.core.base import PullConfig
from pysynthacs.core.population import PopulationPuller
from pysynthacs.core.adapter import acs_result_to_macro_data
from pysynthacs.core.data import MacroData, MicroData
from pysynthacs_core import optimize_population, AnnealingResult

class SyntheticGenerator:
    """
    High-level orchestrator for synthetic population generation.
    """
    def __init__(self, year: int, span: int = 5, api_key: Optional[str] = None):
        self.year = year
        self.span = span
        self.api_key = api_key

    def pull_macro(self, geography: Dict[str, Any]) -> MacroData:
        """Pulls and processes macro-demographic data for a geography."""
        puller = PopulationPuller(
            year=self.year,
            span=self.span,
            geography=geography,
            api_key=self.api_key
        )
        result = puller.run()
        return acs_result_to_macro_data(result)

    def generate(self, 
                 macro: MacroData, 
                 micro: MicroData, 
                 max_iter: int = 50000, 
                 seed: int = 42) -> pd.DataFrame:
        """
        Generates a synthetic population by optimizing the micro pool 
        against the macro constraints.
        """
        # 1. Prepare constraints from MacroData
        # For now, let's focus on age/gender marginals
        ds = macro.data
        
        # Sum over geo to get target counts (assuming single geo for now or handling per geo)
        # In a real implementation, we would loop over geographies.
        geo_list = macro.geography
        final_populations = []
        
        for geo in geo_list:
            # Target age/gender distribution for this geo
            target_ds = ds.sel(geo=geo)
            
            # Flatten 2D (gender, age) into 1D for the Rust engine
            target_counts = target_ds["pop_count"].values.flatten().astype(np.int32)
            targets = [target_counts]
            
            # Sample size is the total population in this geo
            sample_size = int(target_ds["pop_count"].sum())
            
            # 2. Prepare micro data
            # Map micro categories to integer indices that match target_counts
            # (Simplified for now: assume micro.data has a 'category' col 0-47)
            if "category" not in micro.data.columns:
                raise ValueError("MicroData must contain a 'category' column mapped to Census bins.")
            
            pool_data = micro.data[["category"]].values.astype(np.int32)
            
            # 3. Optimize
            result: AnnealingResult = optimize_population(
                pool_data=pool_data,
                target_constraints=targets,
                sample_size=sample_size,
                max_iter=max_iter,
                seed=seed
            )
            
            # 4. Extract synthetic population
            synthetic_indices = result.best_indices
            geo_pop = micro.data.iloc[synthetic_indices].copy()
            geo_pop["geo"] = geo
            final_populations.append(geo_pop)
            
        return pd.concat(final_populations, ignore_index=True)
