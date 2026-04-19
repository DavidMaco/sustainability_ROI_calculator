# 🌱 Sustainability ROI Calculator

## Convert Sustainable Procurement into a Defensible Business Case

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Tests](https://img.shields.io/badge/Tests-21%20Passing-22C55E?style=for-the-badge&logo=pytest&logoColor=white)](#-testing)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Release-v2.0.2-purple?style=for-the-badge)](CHANGELOG.md)

The Sustainability ROI Calculator is a decision-support analytics platform that quantifies the financial and environmental outcomes of moving from conventional materials to sustainable alternatives. It is designed for Nigerian FMCG manufacturers that need clear evidence before approving procurement strategy changes.

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

## 💡 Why This Exists

Many sustainability programs are approved on policy grounds but delayed at budget review. This project addresses that gap by producing measurable impact and financial outcomes that decision-makers can evaluate directly.

### Key Business Question

If an organization adopts sustainable materials, will the transition produce acceptable financial returns while improving environmental performance?

### What the Model Quantifies

- Procurement cost increase
- Carbon reduction percentage
- Operational savings
- Net annual ROI
- Estimated payback period

> [!IMPORTANT]
> Under the current demonstration assumptions, the model indicates substantial environmental improvement (about 82% carbon reduction) and negative direct annual ROI (about 49.6% loss). The analysis remains actionable because strategic viability can improve through policy incentives, avoided risk exposure, and long-term positioning.

## ✨ Key Features

### 🔬 Deterministic Engine

Seed-based execution ensures reproducible outputs across runs and supports full auditability of reported figures.

### 🛡️ Typed Contracts

Pydantic models enforce data integrity across ingestion, computation, and reporting.

### 🔌 Pluggable Adapters

The `DataAdapter` interface allows storage backends to be exchanged cleanly, including CSV, relational databases, APIs, and cloud object stores.

### 📊 Executive Dashboard

The Streamlit interface presents aggregate KPI summaries and company-level analysis with interactive Plotly visualizations.

### 🧮 Custom Scenario Builder

Analysts can adjust procurement mix and economic assumptions in real time without writing code.

### 🧪 Regression Protection

The test suite validates formulas, unit conversions, and output structure to reduce model drift and unintended regressions.

### 🔐 Access Control (RBAC)

Built-in authentication supports `viewer`, `analyst`, and `admin` roles. The app can load users from Streamlit secrets or environment variables.

In production, weak placeholder passwords are rejected. For managed deployments, mount a JSON secret file and set `SUST_AUTH_USERS_FILE`.

### 🗃 Artifact Backups

Each pipeline run can generate timestamped zip backups and checksum manifests under `data/backups/` for auditability and rollback.

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- `pip`

### 1. Clone and install

```bash
git clone https://github.com/DavidMaco/sustainability_ROI_calculator.git
cd sustainability_ROI_calculator
pip install -r requirements.txt
```

### 2. Run the data pipeline

```bash
python -m pipeline.runner
```

This command generates artifacts in `data/` and prints a summary in the terminal.

### 3. Launch the app

```bash
streamlit run streamlit_app.py
```

The app opens at `http://localhost:8501` with these pages:

- **📊 Executive Dashboard**: Aggregate KPIs, cost comparisons, and savings breakdown.
- **🔍 Material Explorer**: Side-by-side material analysis and quick-win identification.
- **🧮 Custom Scenario**: Assumption tuning with immediate ROI feedback.

## 🏗 Architecture

```text
streamlit_app.py + pages/
        │
        ▼
domain/ (pure calculation logic and models)
        │
        ▼
ingestion/ (DataAdapter abstraction and concrete implementations)
        │
        ▼
pipeline/runner.py (batch orchestration)
        │
        ▼
data/ (generated artifacts)
```

### File map

- `config.py`: Centralized configuration with environment overrides.
- `domain/models.py`: Pydantic contracts for typed data flow.
- `domain/materials.py`: Seeded material profile generation.
- `domain/scenarios.py`: ROI and impact calculations.
- `domain/recommendations.py`: Quick-win and comparison logic.
- `ingestion/base.py`: Abstract adapter interface.
- `ingestion/csv_adapter.py`: CSV and JSON persistence implementation.
- `ingestion/sqlite_adapter.py`: SQLite read/write persistence implementation.
- `ingestion/external_api_adapter.py`: Read-only HTTP API connector implementation.
- `ingestion/factory.py`: Runtime adapter selection (`csv`, `sqlite`, `api`).
- `pipeline/runner.py`: End-to-end CLI workflow.
- `streamlit_app.py`: Application entry point and data readiness behavior.
- `pages/`: Streamlit page modules.
- `tests/`: Unit and integration tests.

## ⚙ Configuration

Runtime and economic assumptions are environment-configurable.

- `SUST_CARBON_TAX` (default `50000`): Carbon tax rate in ₦ per ton.
- `SUST_WATER_COST` (default `150`): Water cost in ₦ per 1000 liters.
- `SUST_WASTE_COST` (default `80000`): Waste disposal cost in ₦ per ton.
- `SUST_ENV` (default `development`): Runtime environment (`development`, `staging`, `production`).
- `SUST_RANDOM_SEED` (default `42`): Random seed for deterministic generation.
- `SUST_DATA_DIR` (default `data`): Output artifact directory.
- `SUST_LOG_LEVEL` (default `INFO`): Logging level.
- `SUST_DATA_BACKEND` (default `csv`): Data adapter backend (`csv`, `sqlite`, `api`).
- `SUST_SQLITE_DB_PATH` (default `data/sustainability_roi.db`): SQLite artifact path.
- `SUST_EXTERNAL_API_BASE_URL` (default `http://127.0.0.1:8080`): API adapter base URL.
- `SUST_ANALYSIS_YEARS` (default `5`): Multi-year discounted cash-flow horizon.
- `SUST_DISCOUNT_RATE` (default `0.12`): Discount rate for NPV.
- `SUST_NET_BENEFIT_GROWTH_RATE` (default `0.03`): Annual net-benefit growth assumption.
- `SUST_OPTIMIZATION_BUDGET_INCREASE_NGN` (default `250000000`): Max allowed annual procurement cost increase for switch optimization.
- `SUST_OPTIMIZATION_MIN_CARBON_REDUCTION_PCT` (default `20`): Minimum required portfolio carbon reduction target.
- `SUST_MONTE_CARLO_SIMULATIONS` (default `1000`): Number of sensitivity simulations.
- `SUST_MONTE_CARLO_RATE_STD_DEV` (default `0.15`): Std-dev for carbon/water/waste savings multipliers.
- `SUST_MONTE_CARLO_DISCOUNT_STD_DEV` (default `0.02`): Std-dev for simulated discount rates.

In production mode (`SUST_ENV=production`), runtime assumption guardrails are enabled.

### ROI formulas

```text
Net Annual Benefit = Operational Savings - Procurement Cost Increase

Operational Savings = Carbon Tax Avoidance + Water Savings + Waste Savings
  Carbon Tax Avoidance = (carbon_saved_kg / 1000) * CARBON_TAX_NGN_PER_TON
  Water Savings        = (water_saved_l / 1000) * WATER_COST_NGN_PER_1000L
  Waste Savings        = (waste_reduced_kg / 1000) * WASTE_COST_NGN_PER_TON

ROI %   = Net Benefit / |Cost Increase| * 100
Payback = |Cost Increase| / Operational Savings

NPV = sum_{year=1..ANALYSIS_YEARS}
        (Net Annual Benefit * (1 + NET_BENEFIT_GROWTH_RATE)^(year-1)) / (1 + DISCOUNT_RATE)^year
```

## 📦 Output Artifacts

The pipeline generates the following files in `data/`:

- `sustainability_materials_comparison.csv`: Material category baseline and sustainable alternatives.
- `company_scenarios.csv`: Predefined FMCG company scenarios.
- `sustainability_roi_analysis.csv`: Company-level ROI and impact outputs.
- `sustainability_summary.json`: Aggregated headline metrics.
- `sustainability_calculator_template.csv`: Analyst-facing template for comparisons.
- `sustainable_switch_optimization.csv`: Constraint-aware switch recommendations under budget and carbon targets.
- `monte_carlo_samples.csv`: Sensitivity simulation samples for net benefit and NPV.
- `monte_carlo_bounds.json`: P05/P50/P95 uncertainty bounds for annual net benefit and NPV.

## 🧪 Testing

```bash
pytest tests/ -q
pytest tests/ -v
ruff check . --config pyproject.toml
black --check --config pyproject.toml .
```

Current tests cover:

- Deterministic material generation and structural invariants.
- Scenario calculations and unit conversion correctness.
- Custom scenario consistency with batch processing.
- Input validation behavior for unsupported materials.
- End-to-end artifact generation and determinism.
- JSON serialization and deserialization integrity.

### Operations checks

```bash
# App + data readiness health check
python scripts/healthcheck.py

# Baseline concurrent load probe
python scripts/load_test.py

# Metrics and readiness endpoint (for central observability)
python scripts/metrics_server.py
```

Metrics server endpoints:

- `/healthz`: JSON readiness response and missing artifact list
- `/metrics`: Prometheus-style gauges for data readiness, backups, and summary KPIs

### Container deployment

```bash
# Build and run
docker compose up --build
```

Before enabling auth in production, create `.streamlit/secrets.toml` from `.streamlit/secrets.toml.example` and set real credentials.

### Kubernetes deployment baseline

```bash
kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/base/configmap.yaml
kubectl apply -f k8s/base/secret.example.yaml
kubectl apply -f k8s/base/pvc.yaml
kubectl apply -f k8s/base/deployment.yaml
kubectl apply -f k8s/base/service.yaml
kubectl apply -f k8s/base/hpa.yaml
kubectl apply -f k8s/base/ingress.yaml
```

Update hostnames, image tags, and secret values before using manifests in non-local environments.

### Kubernetes overlays (staging and production)

```bash
# Preview manifests
kubectl kustomize k8s/overlays/staging
kubectl kustomize k8s/overlays/production

# Apply environment-specific manifests
kubectl apply -k k8s/overlays/staging
kubectl apply -k k8s/overlays/production
```

The deployment includes a Fluent Bit sidecar that tails application logs from `/var/log/app`.
Production overlay routes logs to Loki via `k8s/overlays/production/patch-fluent-bit-loki.yaml`.

Security hardening included in base manifests:

- Dedicated service account with token automount disabled
- Pod and container security contexts (non-root, dropped Linux capabilities)
- Default-deny network policy with explicit ingress and egress allow lists

CI now enforces runtime gates by starting Streamlit, checking `/_stcore/health`, and running both `scripts/healthcheck.py` and `scripts/load_test.py` with latency/failure thresholds.
It validates Kubernetes base, overlays, and policy manifests using `kubectl kustomize` + `kubeconform` (offline schema validation), and publishes performance trend summaries.

## 🔄 CI/CD

GitHub Actions runs on each push and pull request targeting `main`:

```text
Lint (ruff) -> Format (black) -> Pipeline Smoke Test -> Artifact Validation -> Tests (pytest) -> Upload Artifacts
```

Workflow definition: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

## 🗺 Roadmap

- [x] External data connectors (API and SQLite adapters)
- [x] Multi-year discounted cash flow analysis (NPV and discounted payback)
- [x] Constraint-aware scenario optimization
- [x] Authentication and RBAC for hosted deployments
- [x] Operational observability and health reporting
- [x] Containerization and Kubernetes deployment manifests
- [x] Monte Carlo sensitivity analysis on key assumptions

## 📖 Documentation

- [`CHANGELOG.md`](CHANGELOG.md): Version history and release detail.
- [`PRODUCTION_READINESS.md`](PRODUCTION_READINESS.md): Deployment readiness checklist.
- [`MIGRATION_NOTES.md`](MIGRATION_NOTES.md): Migration guidance and formula references.

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feat/my-feature`.
3. Install development dependencies: `pip install -r requirements-dev.txt`.
4. Implement and validate your changes.
5. Run quality gates: `ruff check .`, `black .`, and `pytest tests/`.
6. Commit with [Conventional Commits](https://www.conventionalcommits.org/).
7. Open a pull request.

## 📝 License

[MIT](LICENSE) © David Igbonaju, 2026.
