"""
Sustainability ROI Calculator — Main Streamlit App
"""

import streamlit as st

st.set_page_config(
    page_title="Sustainability ROI Calculator",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────
st.markdown(
    """<style>
    .main .block-container { padding-top: 1rem; max-width: 1400px; }
    .stMetric { background: #f0fdf4; border-radius: 8px; padding: 12px; border-left: 4px solid #22c55e; }
    h1 { color: #166534; }
</style>""",
    unsafe_allow_html=True,
)

# ─── Sidebar ─────────────────────────────────────────────────────────
st.sidebar.markdown("### 🌱 Sustainability ROI Calculator")
st.sidebar.caption("v2.0.2 · Python 3.12+")
st.sidebar.markdown("---")
st.sidebar.markdown("""
**Pages**
- 📊 Executive Dashboard
- 🔍 Material Explorer
- 🧮 Custom Scenario Builder
""")

# ─── Ensure data exists ─────────────────────────────────────────────
import config as cfg
from ingestion.csv_adapter import CsvAdapter

adapter = CsvAdapter()
data_ready = (cfg.DATA_DIR / "sustainability_roi_analysis.csv").exists()

if not data_ready:
    st.warning("No data found. Generating baseline data…")
    from pipeline.runner import run_pipeline

    run_pipeline(adapter)
    st.rerun()

# ─── Landing Page ────────────────────────────────────────────────────
st.title("🌱 Sustainability ROI Calculator for Manufacturing")
st.markdown("""
**Proving ESG delivers financial returns, not just environmental impact.**

This tool quantifies the true cost and benefit of sustainable procurement choices
for Nigerian FMCG manufacturers. Navigate to a page using the sidebar.
""")

# Quick stats

results_df = adapter.load_results()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Companies Analyzed", f"{len(results_df)}")
col2.metric("Avg Carbon Reduction", f"{results_df['carbon_reduction_pct'].mean():.0f}%")
col3.metric("Avg ROI", f"{results_df['roi_pct'].mean():,.0f}%")
col4.metric(
    "Total Net Benefit",
    f"{cfg.CURRENCY_SYMBOL}{results_df['net_annual_impact_ngn'].sum():,.0f}",
)

st.markdown("---")
st.markdown(
    """
### Key Insight
> Sustainability delivers strong carbon reduction, but direct annual ROI can be
> negative unless policy incentives or avoided risk costs are included.

### ROI Formula
```
Net Annual Benefit = Operational Savings − Procurement Cost Increase
  where Operational Savings = Carbon Tax Avoidance + Water Savings + Waste Savings
```

### Economic Assumptions (configurable)
| Parameter | Value |
|---|---|
| Carbon Tax | ₦{carbon_tax:,.0f}/ton |
| Water Cost | ₦{water_cost:,.0f}/1000L |
| Waste Disposal | ₦{waste_cost:,.0f}/ton |
""".format(
        carbon_tax=cfg.CARBON_TAX_NGN_PER_TON,
        water_cost=cfg.WATER_COST_NGN_PER_1000L,
        waste_cost=cfg.WASTE_COST_NGN_PER_TON,
    )
)
