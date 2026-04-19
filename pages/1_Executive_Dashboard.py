"""Executive Dashboard — aggregate and per-company results."""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import config as cfg
from ingestion.factory import get_data_adapter
from security import require_login, require_role
from ui_theme import CARBON_PAIR, COMPARISON_PAIR, SAVINGS_COLOURS, apply_theme

st.set_page_config(page_title="Executive Dashboard", page_icon="📊", layout="wide")
apply_theme()


def _init_page_state() -> None:
    """Ensure expected session keys exist before any widget or auth check."""
    st.session_state.setdefault("auth_ok", False)


_init_page_state()
require_login()
require_role("viewer")

st.title("📊 Executive Dashboard")
st.caption("Aggregate financial and environmental impact across all company scenarios.")

adapter = get_data_adapter()
results_df = adapter.load_results()

# ─── Aggregate KPIs (2-row layout to avoid cramping) ─────────────────
row1_c1, row1_c2, row1_c3 = st.columns(3)
row1_c1.metric("Total Cost Increase", f"{cfg.CURRENCY_SYMBOL}{results_df['cost_increase_ngn'].sum():,.0f}")
row1_c2.metric("Carbon Reduction", f"{results_df['carbon_reduction_tons'].sum():,.0f} tons")
row1_c3.metric("Operational Savings", f"{cfg.CURRENCY_SYMBOL}{results_df['total_operational_savings_ngn'].sum():,.0f}")

row2_c1, row2_c2, _ = st.columns(3)
row2_c1.metric("Net Benefit", f"{cfg.CURRENCY_SYMBOL}{results_df['net_annual_impact_ngn'].sum():,.0f}")
row2_c2.metric("Avg Payback", f"{results_df['payback_period_years'].mean():.1f} years")

if "npv_net_benefit_ngn" in results_df.columns:
    st.metric(
        f"{cfg.ANALYSIS_YEARS}-Year Discounted NPV",
        f"{cfg.CURRENCY_SYMBOL}{results_df['npv_net_benefit_ngn'].sum():,.0f}",
        help=(f"Discount rate: {cfg.DISCOUNT_RATE:.0%} · " f"Growth rate: {cfg.ANNUAL_NET_BENEFIT_GROWTH_RATE:.0%}"),
    )

st.markdown("---")

# ─── Per-company charts in tabs ──────────────────────────────────────
st.subheader("Company-Level Analysis")
tab_cost, tab_carbon, tab_savings = st.tabs(["💰 Cost Comparison", "🌿 Carbon Emissions", "📊 Savings Breakdown"])

# Short names for charts to prevent label overflow
short_names = results_df["company_name"].str.split(" ").str[:2].str.join(" ")
chart_df = results_df.assign(_short_name=short_names)

with tab_cost:
    fig_cost = px.bar(
        chart_df,
        x="_short_name",
        y=["traditional_annual_cost_ngn", "sustainable_annual_cost_ngn"],
        barmode="group",
        labels={"value": f"Cost ({cfg.CURRENCY_SYMBOL})", "_short_name": ""},
        color_discrete_sequence=COMPARISON_PAIR,
    )
    fig_cost.update_layout(
        legend_title_text="Option",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=40, b=40),
        height=420,
    )
    # Rename legend entries
    fig_cost.data[0].name = "Traditional"
    fig_cost.data[1].name = "Sustainable"
    st.plotly_chart(fig_cost, use_container_width=True)

with tab_carbon:
    fig_carbon = px.bar(
        chart_df,
        x="_short_name",
        y=["carbon_emissions_baseline_tons", "carbon_emissions_sustainable_tons"],
        barmode="group",
        labels={"value": "Tons CO₂", "_short_name": ""},
        color_discrete_sequence=CARBON_PAIR,
    )
    fig_carbon.update_layout(
        legend_title_text="Scenario",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=40, b=40),
        height=420,
    )
    fig_carbon.data[0].name = "Baseline"
    fig_carbon.data[1].name = "Sustainable"
    st.plotly_chart(fig_carbon, use_container_width=True)

with tab_savings:
    savings_cols = ["carbon_tax_savings_ngn", "water_cost_savings_ngn", "waste_disposal_savings_ngn"]
    savings_labels = ["Carbon Tax", "Water Cost", "Waste Disposal"]

    cols = st.columns(len(results_df))
    for idx, (_, row) in enumerate(results_df.iterrows()):
        with cols[idx]:
            # Use shortened name to reduce label overflow
            st.markdown(f"**{short_names.iloc[idx]}**")
            fig = go.Figure(
                go.Pie(
                    labels=savings_labels,
                    values=[row[c] for c in savings_cols],
                    hole=0.45,
                    marker_colors=SAVINGS_COLOURS,
                    textinfo="percent",
                    textposition="inside",
                )
            )
            fig.update_layout(
                height=280,
                margin=dict(t=10, b=10, l=10, r=10),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

    # Shared legend below pie charts
    legend_md = " · ".join(
        f"<span style='color:{colour}'>●</span> {label}" for colour, label in zip(SAVINGS_COLOURS, savings_labels)
    )
    st.markdown(f"<p style='text-align:center; font-size:0.85rem'>{legend_md}</p>", unsafe_allow_html=True)

st.markdown("---")

# ─── Detail table ────────────────────────────────────────────────────
with st.expander("📋 Full Results Table"):
    st.dataframe(results_df, use_container_width=True)

# ─── Download ────────────────────────────────────────────────────────
st.download_button(
    "📥 Download Results CSV",
    results_df.to_csv(index=False),
    "sustainability_roi_results.csv",
    "text/csv",
)
