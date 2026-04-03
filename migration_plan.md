# Migration Plan: synthACS to pysynthACS

This document outlines the architectural plan for migrating the `synthACS` R package to Python (`pysynthACS`). The migration focuses on modernizing the codebase using a mixed Functional Programming (FP) and Object-Oriented Programming (OOP) design, leveraging `pandas`, `censusdis`, and `Parquet`.

## 1. System Overview

`pysynthACS` is a Python package for generating synthetic populations from U.S. Census Bureau American Community Survey (ACS) data. It automates the fetching, cleaning, and transformation of demographic data into a format suitable for spatial microsimulation and synthetic reconstruction.

## 2. Tech Stack & Dependencies

- **Language**: Python 3.13+
- **Data Engine**: `pandas`, `numpy`, `xarray`
- **Census API**: `censusdis` (replaces R `acs` library)
- **Data Storage**: `Parquet` (replaces R `.rda` files)
- **High Performance**: Rust via `PyO3` for simulation logic (replaces Rcpp)
- **Core Design**: Frozen `dataclasses` for immutable configurations and results.
- **Testing**: `pytest`, `pytest-cov`
- **Linting/Types**: `ruff`, `mypy`

## 3. Core Architectural Patterns

### Mixed FP/OOP Design
- **OOP (Orchestration)**: Classes (e.g., `BasePuller`, `SyntheticGenerator`) manage stateful operations like API communication and workflow orchestration.
- **FP (Data Transformation)**: Pure functions handle data cleaning, renaming, and mathematical transformations. This ensures testability and prevents side effects.
- **Immutability**: Frozen `dataclasses` store configurations (`PullConfig`) and resulting datasets (`AcsResult`).

## 4. Phase 1: Data Migration & ACS Puller Refactor [COMPLETED]

### 4.1. Data Migration (`data/` folder)
The static data currently stored as `.rda` files in `synthACS/data/` has been migrated to `pysynthACS/src/pysynthacs/data/`.

- **Format**: All `.rda` files were converted to `.parquet`.
- **Status**: [DONE]

### 4.2. ACS Puller Refactor (`pull_*.R`)
The `pull_*.R` functions have been refactored into a class hierarchy.

- **Status**: `BasePuller`, `PopulationPuller`, `EducationPuller`, `HouseholdPuller`, and `SpecializedPuller` implemented. [DONE]

## 5. Phase 2: High-Performance Optimization Engine [COMPLETED]

### 5.1. Rust Backend (`pysynthacs-core`) [IMPLEMENTED]
The simulated annealing logic has been moved to a Rust extension using `PyO3` and `maturin`.

- **Current Status**: Core logic implemented in `src/lib.rs`.
- **Features**: Scale-agnostic fractional jumps, Re-annealing temperature spikes, Delta-TAE optimization.
- **Default Settings**: `max_iter=50,000`.
- **Status**: [DONE]

### 5.2. Attribute Mapping & Disaggregation
- **Integer Encoding**: Python-side pre-processing to convert categorical Census labels into integer indices for the Rust engine.
- **Status**: Integrated into core logic and verified via integration tests. [DONE]

## 6. Phase 3: Synthetic Data Structures & API [COMPLETED]
Refactoring the complex R S4 classes into modern Python structures.

- **Data Containers**: `MacroData` (xarray-backed) and `MicroData` (pandas-backed) implemented.
- **Adapter**: `acs_result_to_macro_data` adapter for automatic xarray conversion.
- **API Design**: `SyntheticGenerator` orchestrator class implemented.
- **Vectorization**: Uses `xarray` for labeled multi-dimensional selection and alignment.
- **Status**: [DONE]

## 7. Phase 4: Validation, Visualization & Performance [COMPLETED]
Ensuring the tool is robust and provides diagnostic capabilities.

- **Diagnostics**:
  - Port `calculate_TAE` (Total Absolute Error). [DONE]
  - Implement `track_tae_path` to record error reduction during annealing. [DONE]
  - Add `validate_marginals` to compare synthetic vs. macro distributions. [DONE]
- **Visualization (via plotnine/matplotlib)**:
  - `plot_tae_convergence()`: Visualizing the optimization path. [DONE]
  - `plot_spatial_choropleth()`: Mapping results using `geopandas` integration. [DONE]
  - `plot_demographic_fit()`: Bar charts comparing synthetic marginals to Census targets. [DONE]
  - `plot_simulation_quantiles()`: "Fan charts" for birth/death simulation outcomes. [DONE]
- **Simulation Engine**:
  - `simulate_births()` and `simulate_deaths()` logic ported and verified. [DONE]
- **Benchmarking**: Comparative performance testing against the original R implementation. [DONE]

## 8. Phase 5: JSS Replication & Advanced Examples [COMPLETED]
Providing a full suite of examples and advanced plotting based on the JSS paper replication code.

- **Key Workflows (examples/)**:
  - `01_basic_workflow.py`: Pulling data for a single county and generating a population. [DONE]
  - `02_large_scale_optimization.py`: Demonstrating the `SyntheticGenerator` across all tracts in a county. [DONE]
  - `03_attribute_augmentation.py`: Adding specialized attributes (e.g., `transit_work`) to a synthetic population. [DONE]
  - `04_demographic_simulation.py`: Simulating births/deaths over multiple iterations. [DONE]
- **Advanced Plotting**:
  - `plot_spatial_choropleth()`: Mapping births/deaths by census tract using `geopandas`. [DONE]
  - `plot_simulation_quantiles()`: "Fan charts" or boxed whiskers for simulation outcomes. [DONE]

## 9. Phase 6: Code Coverage & CI [PENDING]
Implementing automated testing oversight and CI/CD integration.

- **Configuration**: Set up `pytest-cov` in `pyproject.toml`.
- **Enforcement**: Establish an 80% coverage threshold.
- **CI/CD**: Integrate with GitHub Actions and Codecov for automated reporting.
- **Rust Coverage**: Investigate `llvm-cov` for memory-safe core logic monitoring.

## 10. Testing Strategy [COMPLETED]

To ensure a reliable migration from R, `pysynthACS` employs a multi-layered testing strategy using `pytest`.

### 10.1. Rust Core Testing (`tests/test_core.py`)
- **Status**: Verified convergence, determinism, and scaling. [DONE]

### 10.2. ACS Puller & Transformation Testing (`tests/test_population.py`, `tests/test_all_pullers.py`)
- **Status**: Verified transformation logic for Population, Education, and Household pullers. [DONE]

### 10.3. Data Integrity Testing (`tests/test_data_migration.py`)
- **Status**: Verified all 9 core datasets are readable and structured correctly. [DONE]

### 10.4. Integration Testing (`tests/test_integration.py`)
- **Status**: Verified end-to-end flow with real Census API data. [DONE]

## 11. Performance Estimation & Code Examples

The transition to Rust for the core simulated annealing algorithm provides significant performance gains over the original R implementation.

### 11.1. Estimated Speedup
We estimate a **100x to 1000x speedup** for the optimization phase compared to the original R implementation.

| Aspect | R Implementation | Rust Implementation (`pysynthacs-core`) |
| :--- | :--- | :--- |
| **Execution** | Interpreted (Slow Loops) | Compiled Machine Code (Zero Overhead) |
| **Error Update** | $O(N)$ or $O(Cells)$ recalculation | **$O(1)$ Delta-TAE Update** |
| **Memory** | High (Copies dataframes each iteration) | Zero-cost (In-place updates, no copying) |
| **Throughput** | ~10-100 iterations / sec | **~1,000,000+ iterations / sec** |

### 11.2. Code Example: Delta-TAE Logic (Rust)
Instead of recalculating the total error for the entire population, Rust only calculates the *change* caused by the swapped individuals.

```rust
// Subtract old person's contribution from the specific category
new_tae -= (current_totals[attr][old_cat] - target[old_cat]).abs();
current_totals[attr][old_cat] -= 1;
new_tae += (current_totals[attr][old_cat] - target[old_cat]).abs();

// Add new person's contribution
new_tae -= (current_totals[attr][new_cat] - target[new_cat]).abs();
current_totals[attr][new_cat] += 1;
new_tae += (current_totals[attr][new_cat] - target[new_cat]).abs();
```

### 11.3. Code Example: Modern API (Python)
The high-level API hides the complexity of data alignment and Rust orchestration.

```python
# Multi-dimensional selection via xarray
la_males = macro.data.sel(geo="06037", gender="m")

# High-speed optimization
synthetic_pop = generator.generate(macro, micro, max_iter=50000)
```

## 12. Implementation Roadmap (Current Status)

1. **Setup Data Directory**: [DONE]
2. **One-time Migration**: [DONE]
3. **Core Interfaces**: [DONE]
4. **Initial Pullers (Pop, Edu, HH, etc.)**: [DONE]
5. **Rust Core Engine**: [DONE]
6. **Global API Key Config**: [DONE]
7. **Unit & Integration Testing**: [DONE]
8. **Phase 3 (Data Cubes/xarray)**: [DONE]
9. **Phase 4 (Validation & Diagnostics)**: [DONE]
10. **Phase 5 (Advanced Examples & JSS Replication)**: [IN PROGRESS]
11. **Phase 6 (Code Coverage & CI Integration)**: [PENDING]
