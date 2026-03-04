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

from ui_theme import apply_theme  # noqa: E402

apply_theme()

# ─── Sidebar ─────────────────────────────────────────────────────────
st.sidebar.markdown("### 🌱 Sustainability ROI")
st.sidebar.caption("v2.0.2 · Python 3.12+")

# ─── Ensure data exists ─────────────────────────────────────────────
import config as cfg  # noqa: E402
from ingestion.csv_adapter import CsvAdapter  # noqa: E402

adapter = CsvAdapter()
data_ready = (cfg.DATA_DIR / "sustainability_roi_analysis.csv").exists()

if not data_ready:
    st.warning("No data found. Generating baseline data…")
    from pipeline.runner import run_pipeline

    run_pipeline(adapter)
    st.rerun()

# ─── Landing Page ────────────────────────────────────────────────────
st.title("🌱 Sustainability ROI Calculator")
st.caption(
    "Quantify the financial and environmental impact of sustainable procurement for Nigerian FMCG manufacturers."
)

results_df = adapter.load_results()

# ── Quick Stats ──────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Companies", f"{len(results_df)}")
col2.metric("Avg Carbon Reduction", f"{results_df['carbon_reduction_pct'].mean():.0f}%")
col3.metric("Avg ROI", f"{results_df['roi_pct'].mean():,.0f}%")
col4.metric(
    "Total Net Benefit",
    f"{cfg.CURRENCY_SYMBOL}{results_df['net_annual_impact_ngn'].sum():,.0f}",
)

st.markdown("---")

# ── Key Insight (concise) ────────────────────────────────────────────
st.info(
    "**Key Insight:** Sustainability delivers ~82% carbon reduction, but direct annual ROI "
    "is negative (~−50%) under current assumptions. Business viability depends on policy "
    "incentives, avoided risk, and strategic value.",
    icon="💡",
)

# ── How it Works + Assumptions — side-by-side, collapsed ─────────────
left, right = st.columns(2)

with left:
    with st.expander("📐 ROI Formula", expanded=False):
        st.code(
            "Net Annual Benefit = Operational Savings − Cost Increase\n"
            "  Operational Savings = Carbon Tax + Water + Waste Savings",
            language=None,
        )

with right:
    with st.expander("⚙️ Economic Assumptions", expanded=False):
        st.markdown(
            "| Parameter | Value |\n|:---|---:|\n"
            f"| Carbon Tax | ₦{cfg.CARBON_TAX_NGN_PER_TON:,.0f}/ton |\n"
            f"| Water Cost | ₦{cfg.WATER_COST_NGN_PER_1000L:,.0f}/1 000 L |\n"
            f"| Waste Disposal | ₦{cfg.WASTE_COST_NGN_PER_TON:,.0f}/ton |"
        )
