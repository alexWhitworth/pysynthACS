import pytest
import pandas as pd
import numpy as np
from pysynthacs.viz.plotting import plot_tae_convergence, plot_demographic_fit
from plotnine import ggplot

def test_plot_tae_convergence():
    """Verify TAE convergence plot generation."""
    tae_path = [100, 80, 50, 20, 10]
    p = plot_tae_convergence(tae_path)
    assert isinstance(p, ggplot)

def test_plot_demographic_fit():
    """Verify demographic fit plot generation."""
    df = pd.DataFrame({
        "geo": ["G1", "G1"],
        "attribute": ["age", "age"],
        "bin_idx": [0, 1],
        "macro_count": [10, 20],
        "syn_count": [11, 19],
        "abs_diff": [1, 1]
    })
    p = plot_demographic_fit(df)
    assert isinstance(p, ggplot)
