# pysynthACS

Python version of the `synthACS` R package. Modernized with `pandas`, `censusdis`, `xarray`, and `Rust`.

`pysynthACS` is a high-performance Python library for generating synthetic populations from U.S. Census Bureau American Community Survey (ACS) data. It automates the process of fetching demographic data, cleaning it, and performing spatial microsimulation using a high-speed Rust-based simulated annealing engine.

## Key Features
- **Modern ACS Interface**: Built on top of `censusdis` for efficient, reliable data fetching.
- **High Performance**: Core optimization engine implemented in Rust using `PyO3`, featuring:
  - Scale-agnostic fractional jump logic (handles tiny blocks to massive counties).
  - Modernized hybrid simulated annealing with re-annealing temperature spikes.
  - Delta-TAE optimization for near-instantaneous error updates.
- **Immutable Data Structures**: Utilizes frozen Python dataclasses for robust configuration and result management.
- **Global Configuration**: Easy API key management with `set_api_key()`.
- **Comprehensive Testing**: Full suite of unit and integration tests (100% pass rate).

## Installation

```bash
# Clone and install using uv (recommended)
uv pip install .
```

## Quick Start

```python
import pysynthacs
from pysynthacs.core.population import PopulationPuller

# Set your Census API key
pysynthacs.set_api_key("YOUR_CENSUS_API_KEY")

# 1. Pull population data for a specific geography
puller = PopulationPuller(
    year=2022, 
    span=5, 
    geography={"state": "06", "county": "041"} # Marin County, CA
)
result = puller.run()

# 2. Access estimates and standard errors
age_data = result.estimates["age_by_sex"]
print(age_data.head())
```

## Current Status
Successfully completed Phases 1 and 2 of the migration.
- [x] Phase 1: Data Migration & ACS Puller Core (Complete)
- [x] Phase 2: High-Performance Optimization Engine (Rust/PyO3) (Complete)
- [ ] Phase 3: Synthetic Data Structures & API (xarray integration) (Pending)
- [ ] Phase 4: Validation & Visualization (Pending)

## Documentation & Testing
To run the tests:
```bash
# Run all tests
PYTHONPATH=src uv run pytest tests/

# Run integration tests specifically
PYTHONPATH=src uv run pytest -s tests/test_integration.py
```
