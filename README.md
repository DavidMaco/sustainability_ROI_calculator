# Sustainability ROI Calculator for Manufacturing

<p align="center">
  <strong>Quantify the financial and environmental impact of sustainable procurement decisions.</strong>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img alt="Status" src="https://img.shields.io/badge/Status-v2.0.1-22C55E?style=for-the-badge" />
</p>

This project is a decision-support analytics engine for manufacturing procurement teams. It evaluates trade-offs between traditional and sustainable materials, estimates operational savings (carbon tax, water, waste), and exposes results through both:

- a reproducible CLI pipeline, and
- a multi-page Streamlit interface for executives and analysts.

---

## Why this exists

Sustainability initiatives are often framed as compliance or CSR. This tool reframes them as **capital allocation decisions** by computing:

- procurement cost increase,
- emissions and resource reductions,
- operational savings,
- net annual impact,
- ROI and payback.

For current demo assumptions, the model shows strong carbon reduction (~82%) with negative direct annual ROI (~-49.6%), highlighting that business viability depends on policy incentives, avoided risk, and strategic value.

---

## Key capabilities

- **Deterministic scenario engine** with seed-based reproducibility
- **Typed contracts** using Pydantic models
- **Pluggable ingestion layer** (`DataAdapter` abstraction)
- **Batch + UI workflows** from the same domain logic
- **Regression-protected formulas** via unit and integration tests
- **CI quality gates** for lint, formatting, pipeline smoke test, and pytest

---

## Project architecture

```text
config.py              -> central configuration (env-overridable)
domain/                -> pure business logic
  models.py            -> Pydantic data contracts
  materials.py         -> material profile generation
  scenarios.py         -> ROI + impact calculations
  recommendations.py   -> quick-wins and comparison views
ingestion/             -> adapter layer (CSV/JSON default)
  base.py              -> abstract interface
  csv_adapter.py       -> concrete implementation
pipeline/
  runner.py            -> CLI orchestration and artifact generation
streamlit_app.py       -> app entrypoint
pages/                 -> Streamlit sub-pages
tests/                 -> unit + integration tests
data/                  -> generated artifacts
```

---

## Quick start

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Run pipeline (CLI)

```bash
python -m pipeline.runner
```

### 3) Launch interactive app

```bash
streamlit run streamlit_app.py
```

---

## Output artifacts

Pipeline outputs are generated in `data/`:

- `sustainability_materials_comparison.csv`
- `company_scenarios.csv`
- `sustainability_roi_analysis.csv`
- `sustainability_summary.json`
- `sustainability_calculator_template.csv`

---

## Configuration

Override runtime assumptions with environment variables:

| Variable | Default | Description |
|---|---:|---|
| `SUST_CARBON_TAX` | 50000 | Carbon tax (₦/ton) |
| `SUST_WATER_COST` | 150 | Water cost (₦/1000L) |
| `SUST_WASTE_COST` | 80000 | Waste disposal cost (₦/ton) |
| `SUST_ENV` | `development` | Runtime environment |
| `SUST_RANDOM_SEED` | 42 | Reproducibility seed |

---

## Testing and quality

```bash
pytest tests -q
ruff check . --config pyproject.toml
black --check --config pyproject.toml .
```

Current status: **21 tests passing**.

---

## CI/CD

GitHub Actions workflow includes:

- lint check (`ruff`)
- format check (`black`)
- pipeline smoke test
- artifact existence validation
- pytest execution
- artifact upload

See `.github/workflows/ci.yml`.

---

## Roadmap

- external data connectors (API/DB adapters)
- multi-year discounted cash flow (NPV/IRR)
- scenario optimizer under constraints
- auth/RBAC for hosted UI
- observability + deployment hardening

---

## Additional documentation

- `PRODUCTION_READINESS.md`
- `MIGRATION_NOTES.md`
- `CHANGELOG.md`

---

## License

No license file is currently defined in this repository.
