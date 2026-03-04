<div align="center">

# 🌱 Sustainability ROI Calculator

### Turn Green Procurement into a Measurable Business Case

<br/>

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Tests](https://img.shields.io/badge/Tests-21%20Passing-22C55E?style=for-the-badge&logo=pytest&logoColor=white)](#-testing)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Release-v2.0.2-purple?style=for-the-badge)](#changelog)

<br/>

A decision-support analytics engine that quantifies the **financial and environmental trade-offs** of switching from traditional to sustainable materials — purpose-built for Nigerian FMCG manufacturers.

<br/>

[**Quick Start**](#-quick-start) · [**Features**](#-key-features) · [**Architecture**](#-architecture) · [**Docs**](#-documentation)

---

</div>

<br/>

## 📋 Table of Contents

- [Why This Exists](#-why-this-exists)
- [Key Features](#-key-features)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Configuration](#-configuration)
- [Output Artifacts](#-output-artifacts)
- [Testing](#-testing)
- [CI/CD](#-cicd)
- [Roadmap](#-roadmap)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

<br/>

## 💡 Why This Exists

Sustainability initiatives are typically framed as compliance or CSR. **This tool reframes them as capital allocation decisions** by computing hard numbers:

<table>
<tr>
<td width="50%">

**The Question**

> _"If we switch to sustainable materials, does it make financial sense — or just environmental sense?"_

</td>
<td width="50%">

**What We Calculate**

| Metric | Example |
|:---|---:|
| Procurement cost increase | ₦2.1B |
| Carbon reduction | 82% |
| Operational savings | ₦1.05B/yr |
| Net annual ROI | −49.6% |
| Payback period | 4.2 years |

</td>
</tr>
</table>

> [!IMPORTANT]
> For current demo assumptions, the model shows **strong environmental gains** (~82% carbon reduction) with **negative direct annual ROI** (~−49.6%). This is the honest finding — business viability depends on policy incentives, avoided risk costs, and long-term strategic value.

<br/>

## ✨ Key Features

<table>
<tr>
<td align="center" width="33%">
  <h3>🔬</h3>
  <h4>Deterministic Engine</h4>
  Seed-based reproducibility ensures identical outputs across runs. Every number is auditable.
</td>
<td align="center" width="33%">
  <h3>🛡️</h3>
  <h4>Typed Contracts</h4>
  Pydantic models enforce data integrity from ingestion through calculation to output.
</td>
<td align="center" width="33%">
  <h3>🔌</h3>
  <h4>Pluggable Adapters</h4>
  Abstract <code>DataAdapter</code> interface — swap CSV for database, API, or cloud storage.
</td>
</tr>
<tr>
<td align="center" width="33%">
  <h3>📊</h3>
  <h4>Executive Dashboard</h4>
  Interactive Streamlit UI with Plotly charts — aggregate KPIs and per-company deep dives.
</td>
<td align="center" width="33%">
  <h3>🧮</h3>
  <h4>Custom Scenario Builder</h4>
  Adjust material volumes and economic assumptions in real time. No code required.
</td>
<td align="center" width="33%">
  <h3>🧪</h3>
  <h4>Regression-Protected</h4>
  21 tests guard formulas, unit conversions, and output structure. CI enforces on every push.
</td>
</tr>
</table>

<br/>

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- pip

### 1. Clone & install

```bash
git clone https://github.com/DavidMaco/sustainability_ROI_calculator.git
cd sustainability_ROI_calculator
pip install -r requirements.txt
```

### 2. Run the pipeline (CLI)

```bash
python -m pipeline.runner
```

This generates all data artifacts in `data/` and prints a summary to the console.

### 3. Launch the interactive app

```bash
streamlit run streamlit_app.py
```

Opens a multi-page Streamlit dashboard at `http://localhost:8501` with three pages:

| Page | Purpose |
|:---|:---|
| **📊 Executive Dashboard** | Aggregate KPIs, cost comparison charts, savings pie breakdown |
| **🔍 Material Explorer** | Side-by-side material comparison, carbon reduction potential, quick wins |
| **🧮 Custom Scenario** | Build your own procurement mix, adjust assumptions, see instant ROI |

<br/>

## 🏗 Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                    Streamlit Multi-Page UI                    │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐ │
│  │  Executive    │  │  Material    │  │  Custom Scenario   │ │
│  │  Dashboard    │  │  Explorer    │  │  Builder           │ │
│  └──────┬───────┘  └──────┬───────┘  └────────┬───────────┘ │
└─────────┼─────────────────┼────────────────────┼─────────────┘
          │                 │                    │
          ▼                 ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                     Domain Layer (pure logic)                │
│  materials.py · scenarios.py · recommendations.py · models  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              Ingestion Layer (DataAdapter ABC)               │
│  base.py (interface) ──────▶ csv_adapter.py (default impl)  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│           Pipeline Runner (CLI batch orchestration)          │
│  Generate → Calculate → Persist → Console summary           │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
                         data/ (artifacts)
```

### File Map

| File / Dir | Responsibility |
|:---|:---|
| `config.py` | Centralised configuration — all env-overridable |
| `domain/models.py` | Pydantic data contracts |
| `domain/materials.py` | Material profile generation (seeded) |
| `domain/scenarios.py` | ROI + impact calculations |
| `domain/recommendations.py` | Quick-win identification, comparison views |
| `ingestion/base.py` | Abstract `DataAdapter` interface |
| `ingestion/csv_adapter.py` | CSV/JSON read/write implementation |
| `pipeline/runner.py` | End-to-end CLI pipeline |
| `streamlit_app.py` | App entrypoint + data auto-generation |
| `pages/` | Streamlit sub-pages |
| `tests/` | Unit + integration test suite |

<br/>

## ⚙ Configuration

All economic assumptions and runtime settings can be overridden via environment variables:

| Variable | Default | Description |
|:---|---:|:---|
| `SUST_CARBON_TAX` | `50000` | Carbon tax rate (₦/ton) |
| `SUST_WATER_COST` | `150` | Water cost (₦/1000 liters) |
| `SUST_WASTE_COST` | `80000` | Waste disposal cost (₦/ton) |
| `SUST_ENV` | `development` | Runtime environment (`development` \| `staging` \| `production`) |
| `SUST_RANDOM_SEED` | `42` | Random seed for reproducibility |
| `SUST_DATA_DIR` | `data` | Output directory (relative to project root) |
| `SUST_LOG_LEVEL` | `INFO` | Logging level |

**Production mode** (`SUST_ENV=production`) enables runtime assertion guards on assumption values.

### ROI Formulas

```
Net Annual Benefit = Operational Savings − Procurement Cost Increase

Operational Savings = Carbon Tax Avoidance + Water Savings + Waste Savings
  Carbon Tax Avoidance  = (carbon_saved_kg / 1000) × CARBON_TAX_NGN_PER_TON
  Water Savings         = (water_saved_L  / 1000) × WATER_COST_NGN_PER_1000L
  Waste Savings         = (waste_reduced_kg / 1000) × WASTE_COST_NGN_PER_TON

ROI %   = Net Benefit / |Cost Increase| × 100
Payback = |Cost Increase| / Operational Savings
```

<br/>

## 📦 Output Artifacts

The pipeline generates these files in `data/`:

| File | Contents |
|:---|:---|
| `sustainability_materials_comparison.csv` | 10 material categories × 2 options (Traditional / Sustainable) |
| `company_scenarios.csv` | 3 predefined FMCG company scenarios |
| `sustainability_roi_analysis.csv` | Complete ROI results per company |
| `sustainability_summary.json` | Aggregate metrics |
| `sustainability_calculator_template.csv` | Material comparison template for analysts |

<br/>

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -q

# With verbose output
pytest tests/ -v

# Lint
ruff check . --config pyproject.toml

# Format check
black --check --config pyproject.toml .
```

**21 tests** covering:
- Material generation determinism and structural invariants
- Scenario impact calculations with unit-conversion regression guards
- Custom scenario builder consistency with batch scenario engine
- Input validation (unknown materials raise `ValueError`, not `IndexError`)
- Full pipeline artifact generation and determinism
- JSON serialisation round-trip integrity

<br/>

## 🔄 CI/CD

GitHub Actions runs on every push and PR to `main`:

```yaml
Lint (ruff) → Format (black) → Pipeline Smoke Test → Artifact Validation → Tests (pytest) → Upload Artifacts
```

See [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for the full workflow.

<br/>

## 🗺 Roadmap

- [ ] External data connectors (API / database adapters)
- [ ] Multi-year discounted cash flow (NPV / IRR analysis)
- [ ] Scenario optimizer under procurement constraints
- [ ] Authentication & RBAC for hosted UI deployment
- [ ] Observability (structured log aggregation, health endpoint)
- [ ] Docker containerisation + Kubernetes manifests
- [ ] Monte Carlo sensitivity analysis on assumption ranges

<br/>

## 📖 Documentation

| Document | Description |
|:---|:---|
| [`CHANGELOG.md`](CHANGELOG.md) | Version history with detailed change notes |
| [`PRODUCTION_READINESS.md`](PRODUCTION_READINESS.md) | Deployment readiness checklist |
| [`MIGRATION_NOTES.md`](MIGRATION_NOTES.md) | v1 → v2 migration guide and formula reference |

<br/>

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Install dev dependencies: `pip install -r requirements-dev.txt`
4. Make your changes
5. Run the quality gates: `ruff check .` · `black .` · `pytest tests/`
6. Commit using [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, etc.)
7. Open a Pull Request

<br/>

## 📝 License

[MIT](LICENSE) — David Igbonaju, 2026.
