# pysynthACS

Python version of the `synthACS` R package. Modernized with `pandas`, `censusdis`, `xarray`, and `Rust`.

`pysynthACS` is a high-performance Python library for generating synthetic populations from U.S. Census Bureau American Community Survey (ACS) data. It automates the process of fetching demographic data, cleaning it, and performing spatial microsimulation using a high-speed Rust-based simulated annealing engine.

## Key Features
- **Modern ACS Interface**: Built on top of `censusdis` for efficient, reliable data fetching.
- **High Performance (Rust)**: Core optimization engine implemented in Rust using `PyO3`. Provides a **100x-1000x speedup** over the original R implementation through:
  - **Delta-TAE Updates**: Constant time $O(1)$ error calculation during swaps.
  - **Zero-cost Memory**: In-place state updates without expensive data copying.
  - **Hybrid Annealing**: Scale-agnostic fractional jumps and periodic temperature spikes for robust convergence.
- **Multi-dimensional Data Cubes**: Powered by `xarray` for clean management of complex demographic data.
  - **Semantic Selection**: Access data by label (e.g., `gender="male"`) instead of column indices.
  - **Automatic Alignment**: Seamlessly combine datasets with different dimensions.
  - **Vectorized Operations**: Perform fast aggregations across specific demographic dimensions.
- **Immutable Data Structures**: Utilizes frozen Python dataclasses for robust configuration and result management.
- **Global Configuration**: Easy API key management with `set_api_key()`.
- **Comprehensive Testing**: Full suite of unit, integration, and performance tests (100% pass rate).

## Installation

```bash
# Clone and install using uv (recommended)
uv pip install .
```

## Quick Start

```python
import pysynthacs
from pysynthacs.core.generator import SyntheticGenerator
from pysynthacs.core.data import MicroData

# Set your Census API key
pysynthacs.set_api_key("YOUR_CENSUS_API_KEY")

# 1. Pull macro data for a specific geography
gen = SyntheticGenerator(year=2022)
macro = gen.pull_macro(geography={"state": "06", "county": "041"}) # Marin County, CA

# 2. Load your candidate pool (e.g. from PUMS)
pool_df = ... # Your pandas DataFrame with a 'category' column
micro = MicroData(data=pool_df)

# 3. Generate synthetic population
synthetic_pop = gen.generate(macro, micro, max_iter=50000)
print(synthetic_pop.head())
```

## Current Status
- [x] Phase 1: Data Migration & ACS Puller Core (Complete)
- [x] Phase 2: High-Performance Optimization Engine (Rust/PyO3) (Complete)
- [x] Phase 3: Synthetic Data Structures & API (xarray integration) (Complete)
- [x] Phase 4: Validation, Visualization & Simulation (Complete)
- [ ] Phase 5: JSS Replication & Advanced Examples (In Progress)
- [ ] Phase 6: Code Coverage & CI Integration (Pending)

## Documentation & Testing
To run the tests:
```bash
# Run all tests
PYTHONPATH=src uv run pytest tests/
```

## Citation

If you use `pysynthACS` in your research, please cite the following paper:

```bibtex
@Article{synthACS,
    title = {{synthACS}: Spatial MicroSimulation Modeling with Synthetic {A}merican {C}ommunity {S}urvey Data},
    author = {Alex Whitworth},
    journal = {Journal of Statistical Software},
    year = {2022},
    volume = {104},
    number = {7},
    pages = {1--30},
    doi = {10.18637/jss.v104.i07},
}
```
