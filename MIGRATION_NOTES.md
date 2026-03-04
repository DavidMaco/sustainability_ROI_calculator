# Migration Notes — v1 → v2

## Legacy → New Module Mapping

| Legacy File | New Location | Notes |
|---|---|---|
| `generate_sustainability_data.py` | `domain/materials.py` + `domain/scenarios.py` + `pipeline/runner.py` | Split into pure domain logic + orchestration |
| `analyze_sustainability.py` | `domain/scenarios.py` + `domain/recommendations.py` + Streamlit pages | Split into services + presentation |
| Root-level CSV outputs | `data/` directory | All artifacts now under `data/` |
| Hardcoded economic constants | `config.py` (env-overridable) | Carbon tax, water cost, waste cost now configurable |
| `materials_mix` as Python dict string in CSV | JSON string in CSV | `CsvAdapter` normalises on read/write |

## Formula Preservation

All ROI formulas are **unchanged** in structure; v2.0.1 corrected the unit conversions:

- `Net Annual Benefit = Operational Savings − Cost Increase`
- `Operational Savings = Carbon Tax Savings + Water Savings + Waste Savings`
- `Carbon Tax Savings = (carbon_saved_kg / 1000) × ₦50,000/ton`
- `Water Cost Savings = (water_saved_liters / 1000) × ₦150/1000L`
- `Waste Savings = (waste_reduced_kg / 1000) × ₦80,000/ton`
- `ROI % = Net Benefit / |Cost Increase| × 100`
- `Payback = |Cost Increase| / Operational Savings`

## Breaking Changes
- Output files now live in `data/` (not project root)
- `materials_mix` column in `company_scenarios.csv` is now valid JSON (not Python repr)
- Python 3.12+ required (was unspecified)

## How to Run
```bash
# CLI batch mode
python -m pipeline.runner

# Streamlit UI
streamlit run streamlit_app.py
```
