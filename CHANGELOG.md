# Changelog

## [2.0.2] — 2026-03-04

### Fixed
- Hardened `materials_mix` JSON parsing in `calculate_scenario_impacts` — replaced
  fragile `.replace("'", '"')` with `ast.literal_eval` fallback (same strategy as
  `CsvAdapter`).
- Unified water savings formula in `calculate_custom_scenario` to match the clear
  `(water_saved / 1000) × rate` pattern used in `calculate_scenario_impacts`.
  Mathematically identical; eliminates confusing intermediate expressions.
- `_safe_print` promoted from nested function to module-level in `pipeline/runner.py`
  for testability and reuse.

### Added
- `LICENSE` — MIT license.
- `requirements-dev.txt` — separated dev/quality dependencies from runtime.
- Per-file ruff ignore for `F401` in `__init__.py` files (removed risky global ignore).
- Additional `.gitignore` entries: `Thumbs.db`, `*.env`, `*.log`, `.mypy_cache/`.

### Changed
- `MIGRATION_NOTES.md` formulas updated to reflect v2.0.1 unit-conversion corrections.
- `PRODUCTION_READINESS.md` updated to v2.0.2 with v2.0.1 fix items.
- README redesigned for visual impact with TOC, feature grid, architecture diagram,
  and contributing section.

## [2.0.1] — 2026-03-04

### Fixed
- **Critical**: Unit-conversion bug in `calculate_scenario_impacts` — carbon tax and waste
  disposal savings were overstated by 1,000× (missing kg→ton division). Both calculation
  paths now use consistent unit conversion.
- Config mutation in Streamlit Custom Scenario page — sidebar overrides no longer leak
  across sessions.
- Pipeline tests no longer mutate global `cfg.DATA_DIR` — uses `monkeypatch` instead.
- Unicode encoding crash on Windows terminals with Naira symbol (₦).

### Added
- `.gitignore` for generated artifacts, caches, and virtual environments.
- `conftest.py` at project root — eliminates fragile `sys.path.insert` in tests.
- `load_summary()` method on `DataAdapter` ABC and `CsvAdapter`.
- Input validation in `calculate_scenario_impacts` / `calculate_custom_scenario` —
  raises `ValueError` for unknown material categories.
- Regression guard tests: `test_scenario_roi_realistic`, `test_custom_and_scenario_savings_consistent`,
  `test_invalid_material_raises_error`.

### Changed
- `run_pipeline()` type hint widened from `CsvAdapter` to `DataAdapter`.
- `_extract_metric()` uses explicit prefix map instead of substring matching.
- Removed unused config vars `ANALYSIS_HORIZON_YEARS` and `DEMO_MODE`.
- Deleted stale legacy files from project root (preserved in `legacy/`).

## [2.0.0] — 2026-03-04

### Added
- Modular package architecture: `domain/`, `ingestion/`, `pipeline/`, `pages/`
- Typed data contracts via Pydantic (`domain/models.py`)
- Centralised configuration (`config.py`) with env-var overrides
- Pluggable ingestion layer with CSV adapter
- Streamlit multi-page app (Executive Dashboard, Material Explorer, Custom Scenario)
- Unit and integration test suite (`tests/`)
- CI/CD workflow (`.github/workflows/ci.yml`)
- Production readiness checklist
- Migration notes from v1

### Changed
- Python 3.12+ required
- All output artifacts now written to `data/` directory
- `materials_mix` serialised as JSON (not Python dict repr)
- Economic assumptions (carbon tax, water cost, waste cost) now configurable via env vars

### Removed
- Flat script execution from project root (preserved in `legacy/`)
