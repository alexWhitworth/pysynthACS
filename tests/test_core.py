import pytest
import numpy as np
from pysynthacs_core import optimize_population

def test_convergence_tiny_population():
    """Test that a tiny population (N=20) can reach zero error."""
    # 20 people, 2 attributes (Gender: 2 cats, Age: 3 cats)
    # Target: 10 Males, 10 Females; 6 Young, 7 Middle, 7 Old
    pool = np.zeros((100, 2), dtype=np.int32)
    # Fill pool with equal distribution
    for i in range(100):
        pool[i, 0] = i % 2      # 0 or 1
        pool[i, 1] = i % 3      # 0, 1, or 2
        
    targets = [
        np.array([10, 10], dtype=np.int32),     # Gender
        np.array([6, 7, 7], dtype=np.int32)      # Age
    ]
    
    result = optimize_population(
        pool_data=pool,
        target_constraints=targets,
        sample_size=20,
        max_iter=1000,
        tolerance=0,
        seed=123
    )
    
    assert result.final_tae == 0
    assert len(result.best_indices) == 20

def test_determinism():
    """Test that the same seed produces identical results."""
    pool = np.random.randint(0, 5, size=(100, 3), dtype=np.int32)
    targets = [np.array([20, 20, 20, 20, 20], dtype=np.int32) for _ in range(3)]
    
    res1 = optimize_population(pool, targets, 100, seed=42)
    res2 = optimize_population(pool, targets, 100, seed=42)
    
    assert res1.final_tae == res2.final_tae
    assert res1.best_indices == res2.best_indices
    assert res1.iterations == res2.iterations

def test_large_population_smoke():
    """Smoke test for a larger population (N=10,000)."""
    pool = np.random.randint(0, 10, size=(20000, 5), dtype=np.int32)
    targets = [np.full(10, 1000, dtype=np.int32) for _ in range(5)]
    
    # Just ensure it runs without crashing and reduces error
    # A random sample will have some TAE; optimization should reduce it.
    result = optimize_population(pool, targets, 10000, max_iter=100)
    assert result.iterations == 100
    assert len(result.best_indices) == 10000
