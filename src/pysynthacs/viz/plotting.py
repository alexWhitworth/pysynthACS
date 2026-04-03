import pandas as pd
import numpy as np
from typing import List, Optional, Any, Dict
from plotnine import (
    ggplot, aes, geom_line, geom_bar, geom_point,
    labs, theme_minimal, facet_wrap, scale_y_log10
)

def plot_tae_convergence(tae_path: List[int], track_interval: int = 10):
    """
    Plots the TAE reduction path from simulated annealing.
    """
    df = pd.DataFrame({
        "iteration": np.arange(len(tae_path)) * track_interval,
        "tae": tae_path
    })
    
    return (
        ggplot(df, aes(x="iteration", y="tae"))
        + geom_line(color="#2c3e50")
        + scale_y_log10()
        + theme_minimal()
        + labs(
            title="Optimization Convergence Path",
            subtitle="Total Absolute Error (TAE) over iterations",
            x="Iteration",
            y="TAE (Log Scale)"
        )
    )

def plot_demographic_fit(comparison_df: pd.DataFrame):
    """
    Plots a side-by-side comparison of macro vs synthetic counts.
    """
    # Reshape for plotting
    plot_df = comparison_df.melt(
        id_vars=["geo", "attribute", "bin_idx"],
        value_vars=["macro_count", "syn_count"],
        var_name="source",
        value_name="count"
    )
    
    return (
        ggplot(plot_df, aes(x="factor(bin_idx)", y="count", fill="source"))
        + geom_bar(stat="identity", position="dodge")
        + facet_wrap("~geo")
        + theme_minimal()
        + labs(
            title="Demographic Fit: Synthetic vs Macro",
            x="Demographic Bin",
            y="Population Count",
            fill="Data Source"
        )
    )

def plot_spatial_choropleth(df: pd.DataFrame, 
                            geo_df: Any, 
                            column: str, 
                            title: Optional[str] = None):
    """
    Generates a spatial choropleth map using geopandas.
    """
    import geopandas as gpd
    import matplotlib.pyplot as plt
    
    # Merge data with geometries
    # Assuming 'geo' in df matches 'GEOID' or similar in geo_df
    merged = geo_df.merge(df, left_on="GEOID", right_on="geo")
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    merged.plot(column=column, ax=ax, legend=True, cmap="Blues", 
                legend_kwds={'label': column, 'orientation': "horizontal"})
    
    if title:
        ax.set_title(title)
    ax.set_axis_off()
    return fig

def plot_simulation_quantiles(simulation_results: pd.DataFrame, 
                             attribute: str, 
                             title: Optional[str] = None):
    """
    Plots a 'fan chart' or distribution of simulation outcomes.
    """
    # Group by iteration or category and calculate quantiles
    # (To be refined based on simulation output structure)
    return (
        ggplot(simulation_results, aes(x="category", y="count"))
        + geom_point(alpha=0.1)
        + theme_minimal()
        + labs(title=title or f"Simulation Distribution: {attribute}")
    )
