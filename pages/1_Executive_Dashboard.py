"""Executive Dashboard — aggregate and per-company results."""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import config as cfg
from ingestion.csv_adapter import CsvAdapter

st.set_page_config(page_title="Executive Dashboard", page_icon="📊", layout="wide")
st.title("📊 Executive Dashboard")

adapter = CsvAdapter()
results_df = adapter.load_results()

# ─── Aggregate KPIs ──────────────────────────────────────────────────
st.subheader("Aggregate Impact")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Cost Increase", f"{cfg.CURRENCY_SYMBOL}{results_df['cost_increase_ngn'].sum():,.0f}")
c2.metric("Carbon Reduction (tons)", f"{results_df['carbon_reduction_tons'].sum():,.0f}")
c3.metric("Operational Savings", f"{cfg.CURRENCY_SYMBOL}{results_df['total_operational_savings_ngn'].sum():,.0f}")
c4.metric("Net Benefit", f"{cfg.CURRENCY_SYMBOL}{results_df['net_annual_impact_ngn'].sum():,.0f}")
c5.metric("Avg Payback", f"{results_df['payback_period_years'].mean():.2f} yrs")

st.markdown("---")

# ─── Per-company breakdown ───────────────────────────────────────────
st.subheader("Company-Level Results")

fig_cost = px.bar(
    results_df,
    x="company_name",
    y=["traditional_annual_cost_ngn", "sustainable_annual_cost_ngn"],
    barmode="group",
    title="Annual Procurement Cost: Traditional vs Sustainable",
    labels={"value": f"Cost ({cfg.CURRENCY_SYMBOL})", "company_name": ""},
)
fig_cost.update_layout(legend_title_text="Option")
st.plotly_chart(fig_cost, use_container_width=True)

fig_carbon = px.bar(
    results_df,
    x="company_name",
    y=["carbon_emissions_baseline_tons", "carbon_emissions_sustainable_tons"],
    barmode="group",
    title="Carbon Emissions: Baseline vs Sustainable (tons)",
    labels={"value": "Tons CO₂", "company_name": ""},
    color_discrete_sequence=["#ef4444", "#22c55e"],
)
fig_carbon.update_layout(legend_title_text="Scenario")
st.plotly_chart(fig_carbon, use_container_width=True)

# ─── Savings breakdown ───────────────────────────────────────────────
st.subheader("Operational Savings Breakdown")
savings_cols = ["carbon_tax_savings_ngn", "water_cost_savings_ngn", "waste_disposal_savings_ngn"]
savings_labels = ["Carbon Tax", "Water Cost", "Waste Disposal"]

cols = st.columns(len(results_df))
for idx, (_, row) in enumerate(results_df.iterrows()):
    with cols[idx]:
        st.markdown(f"**{row['company_name']}**")
        fig = go.Figure(
            go.Pie(
                labels=savings_labels,
                values=[row[c] for c in savings_cols],
                hole=0.4,
            )
        )
        fig.update_layout(height=300, margin=dict(t=20, b=20), showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

# ─── Detail table ────────────────────────────────────────────────────
with st.expander("Full Results Table"):
    st.dataframe(results_df, use_container_width=True)

# ─── Download ────────────────────────────────────────────────────────
st.download_button(
    "📥 Download Results CSV",
    results_df.to_csv(index=False),
    "sustainability_roi_results.csv",
    "text/csv",
)
