"""Material Explorer — compare traditional vs sustainable options."""

import plotly.express as px
import streamlit as st

from domain.recommendations import build_material_comparison_table, identify_quick_wins
from ingestion.csv_adapter import CsvAdapter

st.set_page_config(page_title="Material Explorer", page_icon="🔍", layout="wide")
st.title("🔍 Material Explorer")

adapter = CsvAdapter()
materials_df = adapter.load_materials()
comparison = build_material_comparison_table(materials_df)

# ─── Comparison table ────────────────────────────────────────────────
st.subheader("Material Comparison")
st.dataframe(
    comparison.style.format(
        {
            "Carbon Reduction (%)": "{:.1f}",
            "Price Premium (%)": "{:+.1f}",
            "Traditional Price (₦)": "{:,.0f}",
            "Sustainable Price (₦)": "{:,.0f}",
            "Water Saved (liters)": "{:,.0f}",
            "Waste Reduced (kg)": "{:,.0f}",
        }
    ),
    use_container_width=True,
)

# ─── Carbon reduction chart ──────────────────────────────────────────
st.subheader("Carbon Reduction Potential")
fig = px.bar(
    comparison.sort_values("Carbon Reduction (%)", ascending=True),
    x="Carbon Reduction (%)",
    y="Material Category",
    orientation="h",
    title="Carbon Reduction Potential by Material",
    color="Price Premium (%)",
    color_continuous_scale=["#22c55e", "#facc15", "#ef4444"],
)
fig.update_layout(height=450)
st.plotly_chart(fig, use_container_width=True)

# ─── Quick wins ──────────────────────────────────────────────────────
st.subheader("🎯 Quick Wins (≤10% premium)")
qw = identify_quick_wins(materials_df)
if not qw.empty:
    for _, row in qw.iterrows():
        emoji = "💚" if row["price_premium_pct"] <= 0 else "🟡"
        st.markdown(
            f"{emoji} **{row['material']}** → {row['sustainable_option']}  \n"
            f"  Price: {row['price_premium_pct']:+.1f}% · Carbon: −{row['carbon_reduction_pct']:.1f}%"
        )
else:
    st.info("No quick wins below threshold.")

# ─── Download ────────────────────────────────────────────────────────
st.markdown("---")
st.download_button(
    "📥 Download Comparison CSV",
    comparison.to_csv(index=False),
    "sustainability_material_comparison.csv",
    "text/csv",
)
