"""
Sustainability ROI Calculator — Main Streamlit App
"""

import threading

import streamlit as st

# Module-level lock: prevents concurrent pipeline generation when multiple
# users arrive simultaneously on a fresh deployment with no data yet.
_PIPELINE_LOCK = threading.Lock()

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
from ingestion.factory import get_data_adapter  # noqa: E402
from security import require_login, require_role  # noqa: E402

adapter = get_data_adapter()
require_login()
require_role("viewer")
data_ready = (cfg.DATA_DIR / "sustainability_roi_analysis.csv").exists()

if not data_ready:
    # Only one thread/session should run the pipeline at a time.
    # If another session is already generating data, this one waits and then
    # skips generation (the file will exist by the time the lock is released).
    with _PIPELINE_LOCK:
        # Re-check inside the lock: another session may have just written the data.
        if not (cfg.DATA_DIR / "sustainability_roi_analysis.csv").exists():
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
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Cost Increase", f"{cfg.CURRENCY_SYMBOL}{results_df['cost_increase_ngn'].sum():,.0f}")
    st.metric("Operational Savings", f"{cfg.CURRENCY_SYMBOL}{results_df['operational_savings_ngn'].sum():,.0f}")
with col2:
    st.metric("Carbon Reduction", f"{results_df['carbon_reduction_pct'].mean():.0f}%")
    st.metric("Net Benefits", f"{cfg.CURRENCY_SYMBOL}{results_df['net_benefits_ngn'].sum():,.0f}")

st.metric(
    "Total Net Benefit",
    f"{cfg.CURRENCY_SYMBOL}{results_df['net_annual_impact_ngn'].sum():,.0f}",
)

st.markdown("---")

# ── Decluttered Quick Wins ──────────────────────────────────────────
st.subheader("Quick Wins")
st.markdown(
    "Identify opportunities for immediate impact by focusing on high ROI materials and processes. "
    "Use the Material Explorer to evaluate options and prioritize actions."
)

# ── Key Insight Section ─────────────────────────────────────────────
st.header("Key Insight")
st.info(
    "**Key Insight:** Sustainability delivers ~82% carbon reduction, but direct annual ROI "
    "shows a loss of approximately 50% under current assumptions. Business viability depends on policy "
    "incentives, avoided risk, and strategic value.",
    icon="💡",
)

# ── How it Works + Assumptions — stacked ────────────────────────────
st.subheader("How it Works")
with st.expander("📐 ROI Formula", expanded=False):
    st.code(
        "Net Annual Benefit = Operational Savings − Cost Increase\n"
        "  Operational Savings = Carbon Tax + Water + Waste Savings",
        language=None,
    )

st.subheader("Economic Assumptions")
with st.expander("⚙️ Economic Assumptions", expanded=False):
    st.markdown(
        "| Parameter | Value |\n|:---|---:|\n"
        f"| Carbon Tax | ₦{cfg.CARBON_TAX_NGN_PER_TON:,.0f}/ton |\n"
        f"| Water Cost | ₦{cfg.WATER_COST_NGN_PER_1000L:,.0f}/1 000 L |\n"
        f"| Waste Disposal | ₦{cfg.WASTE_COST_NGN_PER_TON:,.0f}/ton |"
    )
