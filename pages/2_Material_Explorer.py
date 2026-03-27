"""Material Explorer — compare traditional vs sustainable options."""

import plotly.express as px
import streamlit as st

from domain.recommendations import build_material_comparison_table, identify_quick_wins
from ingestion.csv_adapter import CsvAdapter
from security import require_login, require_role
from ui_theme import BRAND_GREEN, apply_theme

st.set_page_config(page_title="Material Explorer", page_icon="🔍", layout="wide")
apply_theme()
require_login()
require_role("viewer")

st.title("🔍 Material Explorer")
st.caption("Side-by-side comparison of traditional vs sustainable material options across all categories.")

adapter = CsvAdapter()
materials_df = adapter.load_materials()
comparison = build_material_comparison_table(materials_df)

# ─── Quick wins first (most actionable) ──────────────────────────────
qw = identify_quick_wins(materials_df)
if not qw.empty:
    st.subheader("🎯 Quick Wins")
    st.caption("Materials with ≤ 10% price premium and high carbon reduction — switch these first.")
    qw_cols = st.columns(len(qw))
    for idx, (_, row) in enumerate(qw.iterrows()):
        is_saving = row["price_premium_pct"] <= 0
        with qw_cols[idx]:
            st.markdown(
                f"**{'💚' if is_saving else '🟡'} {row['material']}**\n\n"
                f"→ {row['sustainable_option']}  \n"
                f"Price: **{row['price_premium_pct']:+.1f}%** · "
                f"Carbon: **−{row['carbon_reduction_pct']:.0f}%**"
            )
    st.markdown("---")

# ─── Carbon reduction chart ──────────────────────────────────────────
st.subheader("Carbon Reduction Potential by Material")
fig = px.bar(
    comparison.sort_values("Carbon Reduction (%)", ascending=True),
    x="Carbon Reduction (%)",
    y="Material Category",
    orientation="h",
    color="Price Premium (%)",
    color_continuous_scale=[[0, BRAND_GREEN], [0.5, "#facc15"], [1, "#ef4444"]],
)
fig.update_layout(
    height=400,
    margin=dict(t=20, b=20),
    coloraxis_colorbar=dict(title="Premium %", thickness=14),
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ─── Comparison table (collapsed by default to reduce clutter) ───────
with st.expander("📋 Full Comparison Table", expanded=False):
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

# ─── Download ────────────────────────────────────────────────────────
st.download_button(
    "📥 Download Comparison CSV",
    comparison.to_csv(index=False),
    "sustainability_material_comparison.csv",
    "text/csv",
)
