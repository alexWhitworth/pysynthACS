# Migration Plan: synthACS to pysynthACS

This document outlines the architectural plan for migrating the `synthACS` R package to Python (`pysynthACS`). The migration focuses on modernizing the codebase using a mixed Functional Programming (FP) and Object-Oriented Programming (OOP) design, leveraging `pandas`, `censusdis`, and `Parquet`.

## 1. System Overview

`pysynthACS` is a Python package for generating synthetic populations from U.S. Census Bureau American Community Survey (ACS) data. It automates the fetching, cleaning, and transformation of demographic data into a format suitable for spatial microsimulation and synthetic reconstruction.

## 2. Tech Stack & Dependencies

- **Language**: Python 3.13+
- **Data Engine**: `pandas`, `numpy`
- **Census API**: `censusdis` (replaces R `acs` library)
- **Data Storage**: `Parquet` (replaces R `.rda` files)
- **High Performance**: Rust via `PyO3` for simulation logic (replaces Rcpp)
- **Core Design**: Frozen `dataclasses` for immutable configurations and results.
- **Testing**: `pytest`
- **Linting/Types**: `ruff`, `mypy`

## 3. Core Architectural Patterns

### Mixed FP/OOP Design
- **OOP (Orchestration)**: Classes (e.g., `BasePuller`) manage stateful operations like API communication and workflow orchestration.
- **FP (Data Transformation)**: Pure functions handle data cleaning, renaming, and mathematical transformations. This ensures testability and prevents side effects.
- **Immutability**: Frozen `dataclasses` store configurations (`PullConfig`) and resulting datasets (`AcsResult`).

## 4. Phase 1: Data Migration & ACS Puller Refactor [COMPLETED]

### 4.1. Data Migration (`data/` folder)
The static data currently stored as `.rda` files in `synthACS/data/` has been migrated to `pysynthACS/src/pysynthacs/data/`.

- **Format**: All `.rda` files were converted to `.parquet`.
- **Status**: [DONE]

### 4.2. ACS Puller Refactor (`pull_*.R`)
The `pull_*.R` functions are being refactored into a class hierarchy.

- **Status**: `BasePuller` and `PopulationPuller` implemented. [DONE]

## 5. Phase 2: High-Performance Optimization Engine [IN PROGRESS]

### 5.1. Rust Backend (`pysynthacs-core`) [IMPLEMENTED]
The simulated annealing logic has been moved to a Rust extension using `PyO3` and `maturin`.

- **Current Status**: Core logic implemented in `src/lib.rs`.
- **Features**: Scale-agnostic fractional jumps, Re-annealing temperature spikes, Delta-TAE optimization.
- **Default Settings**: `max_iter=50,000`.

### 5.2. Attribute Mapping & Disaggregation [PENDING]
- **Integer Encoding**: Python-side pre-processing to convert categorical Census labels into integer indices for the Rust engine.

## 6. Phase 3: Synthetic Data Structures & API [PENDING]
Refactoring the complex R S4 classes into modern Python structures.

- **Data Containers**: Use `dataclasses` or `attrs` for `MacroData`, `MicroData`, and `SyntheticPopulation`.
- **API Design**: Create a high-level `SyntheticGenerator` class that orchestrates the pullers from Phase 1 and the optimization engine from Phase 2.
- **Vectorization**: Store multi-dimensional census data using `xarray` or consolidated `pandas` structures.

## 7. Phase 4: Validation, Visualization & Performance [PENDING]
Ensuring the tool is robust and provides diagnostic capabilities.

- **Diagnostics**: Porting `calculate_TAE` (Total Absolute Error) and `plot_TAEpath`.
- **Visualization**: Using `matplotlib` or `plotly` for diagnostic plots.
- **Benchmarking**: Comparative performance testing against the original R implementation.
- **Documentation**: Finalize docstrings and user guides.

## 8. Testing Strategy

To ensure a reliable migration from R, `pysynthACS` employs a multi-layered testing strategy using `pytest`.

### 8.1. Rust Core Testing (`tests/test_core.py`)
- **Convergence**: Verify that the simulated annealing engine reaches zero error (`TAE=0`) on perfectly solvable synthetic test cases.
- **Determinism**: Ensure that providing a fixed `seed` results in bit-identical output across multiple runs.
- **Scale Stability**: Test behavior on extremely small populations (N=1) and large populations (N=100,000+) to ensure fractional jump logic scales correctly.
- **Edge Cases**: Validate handling of mismatched dimensions between pool data and target constraints.

### 8.2. ACS Puller & Transformation Testing (`tests/test_population.py`)
- **Mocked API**: Use `unittest.mock` to simulate Census API responses, allowing tests to run without network access or API keys.
- **Pure Function Validation**: Individually test the transformation functions (e.g., `transform_age_by_sex`) to verify that R-to-Python column mappings and aggregations are correct.
- **Standard Error Logic**: Verify the calculation of composite standard errors (`sqrt(sum(se^2))`).

### 8.3. Data Integrity Testing (`tests/test_data_migration.py`)
- **Parquet Validation**: Ensure all 9+ core datasets migrated from `.rda` are readable and maintain their structural integrity (columns, types).

## 9. Implementation Roadmap (Current Status)

1. **Setup Data Directory**: [DONE]
2. **One-time Migration**: [DONE]
3. **Core Interfaces**: [DONE]
4. **Initial Puller**: [DONE]
5. **Rust Core Engine**: [DONE]
6. **Unit Testing (Phase 1 & 2)**: [IN PROGRESS]
7. **Phase 3 (Data Cubes/xarray)**: [PENDING]
