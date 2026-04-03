from typing import Dict, Any, List, Optional, Union, Tuple
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
                 seed: int = 42,
                 return_diagnostics: bool = False) -> Union[pd.DataFrame, Tuple[pd.DataFrame, Dict[str, AnnealingResult]]]:
        """
        Generates a synthetic population by optimizing the micro pool 
        against the macro constraints.
        """
        # 1. Prepare constraints from MacroData
        ds = macro.data
        geo_list = macro.geography
        final_populations = []
        diagnostics = {}
        
        for geo in geo_list:
            # Target age/gender distribution for this geo
            target_ds = ds.sel(geo=geo)
            
            # Flatten 2D (gender, age) into 1D for the Rust engine
            target_counts = target_ds["pop_count"].values.flatten().astype(np.int32)
            targets = [target_counts]
            
            # Sample size is the total population in this geo
            sample_size = int(target_ds["pop_count"].sum())
            
            # 2. Prepare micro data
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
            diagnostics[geo] = result
            
        full_pop = pd.concat(final_populations, ignore_index=True)
        
        if return_diagnostics:
            return full_pop, diagnostics
        return full_pop
