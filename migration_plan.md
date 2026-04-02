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

## 8. Testing Strategy [COMPLETED]

To ensure a reliable migration from R, `pysynthACS` employs a multi-layered testing strategy using `pytest`.

### 8.1. Rust Core Testing (`tests/test_core.py`)
- **Convergence**: Verified that the simulated annealing engine reaches zero error on simple cases.
- **Determinism**: Verified bit-identical output with fixed seeds.
- **Scale Stability**: Verified scaling from N=20 to large populations.
- **Status**: [DONE]

### 8.2. ACS Puller & Transformation Testing (`tests/test_population.py`, `tests/test_all_pullers.py`)
- **Mocked API**: Verified transformation logic for Population, Education, and Household pullers.
- **Status**: [DONE]

### 8.3. Data Integrity Testing (`tests/test_data_migration.py`)
- **Parquet Validation**: Verified all 9 core datasets are readable and structured correctly.
- **Status**: [DONE]

### 8.4. Integration Testing (`tests/test_integration.py`)
- **Live API**: Verified end-to-end flow pulling real data from Census API and optimizing it via Rust.
- **Status**: [DONE]

## 9. Implementation Roadmap (Current Status)

1. **Setup Data Directory**: [DONE]
2. **One-time Migration**: [DONE]
3. **Core Interfaces**: [DONE]
4. **Initial Pullers (Pop, Edu, HH, etc.)**: [DONE]
5. **Rust Core Engine**: [DONE]
6. **Global API Key Config**: [DONE]
7. **Unit & Integration Testing**: [DONE]
8. **Phase 3 (Data Cubes/xarray)**: [PENDING]
