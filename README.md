# pysynthACS

Python version of the `synthACS` R package. Modernized with `pandas`, `censusdis`, `xarray`, and `Rust`.

## Features
- **Modern ACS Interface**: Uses `censusdis` for efficient data fetching from the U.S. Census Bureau.
- **High Performance**: core simulation and optimization engine written in Rust (coming in Phase 2).
- **Immutable Data Structures**: Uses frozen Python dataclasses for robust configuration and result tracking.
- **Multi-dimensional Data**: Leveraging `xarray` for clean management of complex demographic cubes (coming in Phase 3).

## Installation
```bash
# Recommended: use uv
uv pip install .
```

## Status
Currently in Phase 1 of migration from R.
- [x] Phase 1: Data Migration & ACS Puller Core
- [ ] Phase 2: High-Performance Optimization Engine (Rust/PyO3)
- [ ] Phase 3: Synthetic Data Structures & API
- [ ] Phase 4: Validation & Visualization
