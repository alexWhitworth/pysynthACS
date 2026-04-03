import pytest
import pandas as pd
import numpy as np
from pysynthacs.simulation.demographics import simulate_births, simulate_deaths

def test_simulate_births_basic():
    """Verify birth simulation output structure."""
    pop = pd.DataFrame({"id": range(100)})
    res = simulate_births(pop, {}, {}, nsim=10, seed=42)
    assert len(res) == 10
    assert "births" in res.columns
    assert res["births"].mean() > 0

def test_simulate_deaths_basic():
    """Verify death simulation output structure."""
    pop = pd.DataFrame({"id": range(100)})
    res = simulate_deaths(pop, {}, nsim=10, seed=42)
    assert len(res) == 10
    assert "deaths" in res.columns
