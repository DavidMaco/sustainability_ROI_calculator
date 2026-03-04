"""Custom Scenario Builder — interactive ROI calculator."""

from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import config as cfg
from domain.scenarios import calculate_custom_scenario
from ingestion.csv_adapter import CsvAdapter
from ui_theme import SAVINGS_COLOURS, apply_theme


@dataclass
class EconomicAssumptions:
    """Session-scoped economic assumptions (avoids mutating global config)."""

    carbon_tax: float = cfg.CARBON_TAX_NGN_PER_TON
    water_cost: float = cfg.WATER_COST_NGN_PER_1000L
    waste_cost: float = cfg.WASTE_COST_NGN_PER_TON


st.set_page_config(page_title="Custom Scenario", page_icon="🧮", layout="wide")
apply_theme()

st.title("🧮 Custom Scenario Builder")
st.caption("Enter your annual procurement volumes and adjust economic assumptions to see instant ROI.")

adapter = CsvAdapter()
materials_df = adapter.load_materials()
categories = sorted(materials_df["material_category"].unique())

# ─── Economic assumptions sidebar ────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Assumptions")
    carbon_tax = st.number_input("Carbon Tax (₦/ton)", value=cfg.CARBON_TAX_NGN_PER_TON, step=5000.0, key="ct")
    water_cost = st.number_input("Water Cost (₦/1000L)", value=cfg.WATER_COST_NGN_PER_1000L, step=10.0, key="wc")
    waste_cost = st.number_input("Waste Cost (₦/ton)", value=cfg.WASTE_COST_NGN_PER_TON, step=5000.0, key="wst")

assumptions = EconomicAssumptions(carbon_tax=carbon_tax, water_cost=water_cost, waste_cost=waste_cost)

# ─── Input form (grouped by type to reduce noise) ────────────────────
raw_materials = ["Sugar", "Palm Oil", "Cocoa", "Flour"]
packaging = ["Plastic Bottles (PET)", "Cardboard Cartons", "Glass Bottles", "Aluminum Cans"]
energy = ["Electricity (Grid)", "Transportation Fuel"]

custom_mix: dict[str, float] = {}


def _render_inputs(label: str, items: list[str]) -> None:
    """Render a group of material inputs inside an expander."""
    available = [c for c in items if c in categories]
    if not available:
        return
    with st.expander(label, expanded=True):
        cols = st.columns(2)
        for i, cat in enumerate(available):
            unit = materials_df[materials_df["material_category"] == cat].iloc[0]["unit_of_measure"]
            val = cols[i % 2].number_input(f"{cat} ({unit})", min_value=0.0, value=0.0, step=100.0, key=f"mat_{cat}")
            if val > 0:
                custom_mix[cat] = val


_render_inputs("🌾 Raw Materials", raw_materials)
_render_inputs("📦 Packaging", packaging)
_render_inputs("⚡ Energy & Transport", energy)

# ─── Calculate ───────────────────────────────────────────────────────
if st.button("Calculate ROI", type="primary", disabled=len(custom_mix) == 0):
    result = calculate_custom_scenario(
        materials_df,
        custom_mix,
        carbon_tax_ngn_per_ton=assumptions.carbon_tax,
        water_cost_ngn_per_1000l=assumptions.water_cost,
        waste_cost_ngn_per_ton=assumptions.waste_cost,
    )

    st.markdown("---")
    st.subheader("Results")

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Additional Cost",
        f"{cfg.CURRENCY_SYMBOL}{result.cost_increase:,.0f}",
        f"{result.cost_increase_pct:.1f}%",
    )
    c2.metric("Operational Savings", f"{cfg.CURRENCY_SYMBOL}{result.operational_savings:,.0f}/yr")
    c3.metric("Net Annual Benefit", f"{cfg.CURRENCY_SYMBOL}{result.net_impact:,.0f}/yr")

    c4, c5, c6 = st.columns(3)
    c4.metric("Carbon Saved", f"{result.carbon_saved_tons:,.0f} tons")
    c5.metric("ROI", f"{result.roi_pct:,.1f}%")
    payback_str = f"{result.payback_years:.1f} yrs" if result.payback_years else "Immediate"
    c6.metric("Payback Period", payback_str)

    # ── Savings breakdown — donut chart + table ──────────────────────
    st.markdown("#### Savings Breakdown")
    chart_col, table_col = st.columns([1, 1])

    savings_labels = ["Carbon Tax Avoidance", "Water Cost Savings", "Waste Disposal Savings"]
    savings_values = [result.carbon_tax_savings_ngn, result.water_cost_savings_ngn, result.waste_disposal_savings_ngn]

    with chart_col:
        fig = go.Figure(
            go.Pie(
                labels=savings_labels,
                values=savings_values,
                hole=0.5,
                marker_colors=SAVINGS_COLOURS,
                textinfo="percent+label",
                textposition="inside",
                insidetextorientation="radial",
            )
        )
        fig.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with table_col:
        breakdown = pd.DataFrame({"Category": savings_labels, "Amount (₦)": savings_values})
        st.dataframe(
            breakdown.style.format({"Amount (₦)": "{:,.0f}"}),
            use_container_width=True,
            hide_index=True,
        )

elif len(custom_mix) == 0:
    st.info("Enter at least one material quantity above, then click **Calculate ROI**.")
