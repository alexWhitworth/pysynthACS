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

## 4. Phase 1: Data Migration & ACS Puller Refactor

### 4.1. Data Migration (`data/` folder)
The static data currently stored as `.rda` files in `synthACS/data/` will be migrated to `pysynthACS/src/pysynthacs/data/`.

- **Format**: All `.rda` files will be converted to `.parquet`.
- **Engine**: `pyarrow` or `fastparquet` via `pandas.to_parquet()`.
- **Access**: A data-loader module (`pysynthacs.data.loaders`) will provide functional access to these datasets.

### 4.2. ACS Puller Refactor (`pull_*.R`)
The `pull_*.R` functions will be refactored into a class hierarchy using the following structure:

#### Configuration & Results (Frozen Dataclasses)
```python
@dataclass(frozen=True)
class PullConfig:
    year: int
    span: int
    geography: Dict[str, Any]
    table_ids: List[str]
    api_key: Optional[str] = None

@dataclass(frozen=True)
class AcsResult:
    estimates: pd.DataFrame
    standard_errors: pd.DataFrame
    metadata: Dict[str, Any]
    config: PullConfig
```

#### Puller Hierarchy
- `BasePuller`: Abstract base class handling API authentication and raw `censusdis` downloads.
- `PopulationPuller`: Fetches age, race, and basic demographic tables (B01001, B02001, etc.).
- `EducationPuller`: Fetches educational attainment and enrollment (B14001, B15001, etc.).
- `IncomePuller`: Fetches household and individual income data.

#### Functional Transformations
Each puller will delegate data cleaning to a set of pure functions in a `transforms` module.

## 5. Phase 2: High-Performance Optimization Engine

### 5.1. Rust Backend (`pysynthacs-core`)
The simulated annealing logic will be moved to a Rust extension using `PyO3` and `maturin`.

- **Engine**: Implement the Metropolis-Hastings loop in Rust for thread-safe, high-speed optimization.
- **Objective Function**: `calculate_tae` implemented in Rust, optimized for incremental updates (only calculating the delta from swapped individuals).
- **Concurrency**: Use `rayon` to parallelize optimization across multiple geographies simultaneously.

### 5.2. Attribute Mapping & Disaggregation
- **Integer Encoding**: Python-side pre-processing to convert categorical Census labels into integer indices for the Rust engine.
- **Numba/NumPy Helpers**: Use Numba for lightweight data preparation tasks that don't require the full Rust toolchain.

## 6. Phase 3: Synthetic Data Structures & API
Refactoring the complex R S4 classes into modern Python structures.

- **Data Containers**: Use `dataclasses` or `attrs` for `MacroData`, `MicroData`, and `SyntheticPopulation`.
- **API Design**: Create a high-level `SyntheticGenerator` class that orchestrates the pullers from Phase 1 and the optimization engine from Phase 2.
- **Vectorization**: Store multi-dimensional census data using `xarray` or consolidated `pandas` structures.

## 7. Phase 4: Validation, Visualization & Performance
Ensuring the tool is robust and provides diagnostic capabilities.

- **Diagnostics**: Porting `calculate_TAE` (Total Absolute Error) and `plot_TAEpath`.
- **Visualization**: Using `matplotlib` or `plotly` for diagnostic plots.
- **Benchmarking**: Comparative performance testing against the original R implementation.
- **Documentation**: Finalize docstrings and user guides.

## 8. Implementation Roadmap (Phase 1)

1. **Setup Data Directory**: Create `src/pysynthacs/data/`.
2. **One-time Migration**: Script to convert `.rda` files to `.parquet`.
3. **Core Interfaces**: Define `PullConfig`, `AcsResult`, and `BasePuller` in `src/pysynthacs/core/`.
4. **Initial Puller**: Implement `PopulationPuller` and its associated transformation functions.
5. **Unit Testing**: Add `pytest` cases for `PopulationPuller` using mocked API responses.
