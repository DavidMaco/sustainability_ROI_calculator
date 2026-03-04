"""Strategic recommendations engine."""

from __future__ import annotations

import pandas as pd


def identify_quick_wins(materials_df: pd.DataFrame, premium_threshold: float = 10.0) -> pd.DataFrame:
    """Find materials with low/negative premium and high carbon reduction."""
    wins: list[dict] = []
    for category in materials_df["material_category"].unique():
        cat = materials_df[materials_df["material_category"] == category]
        sust = cat[cat["option_type"] == "Sustainable"].iloc[0]
        trad = cat[cat["option_type"] == "Traditional"].iloc[0]

        premium = sust.get("price_premium_pct")
        if premium is None or pd.isna(premium) or premium > premium_threshold:
            continue

        carbon_reduction_pct = (
            (trad["carbon_emissions_per_unit"] - sust["carbon_emissions_per_unit"])
            / trad["carbon_emissions_per_unit"]
            * 100
            if trad["carbon_emissions_per_unit"] > 0
            else 0.0
        )

        wins.append(
            {
                "material": category,
                "sustainable_option": sust["material_name"],
                "price_premium_pct": premium,
                "carbon_reduction_pct": round(carbon_reduction_pct, 1),
            }
        )

    return pd.DataFrame(wins).sort_values("price_premium_pct") if wins else pd.DataFrame()


def build_material_comparison_table(materials_df: pd.DataFrame) -> pd.DataFrame:
    """Build the simplified comparison table (replaces legacy export_calculator_tool)."""
    rows: list[dict] = []
    for category in materials_df["material_category"].unique():
        cat = materials_df[materials_df["material_category"] == category]
        trad = cat[cat["option_type"] == "Traditional"].iloc[0]
        sust = cat[cat["option_type"] == "Sustainable"].iloc[0]

        carbon_red = (
            (trad["carbon_emissions_per_unit"] - sust["carbon_emissions_per_unit"])
            / trad["carbon_emissions_per_unit"]
            * 100
            if trad["carbon_emissions_per_unit"] > 0
            else 0.0
        )

        rows.append(
            {
                "Material Category": category,
                "Traditional Option": trad["material_name"],
                "Sustainable Option": sust["material_name"],
                "Unit": trad["unit_of_measure"],
                "Traditional Price (₦)": trad["base_price_ngn_per_unit"],
                "Sustainable Price (₦)": sust["base_price_ngn_per_unit"],
                "Price Premium (%)": sust.get("price_premium_pct", 0),
                "Traditional Carbon (kg)": trad["carbon_emissions_per_unit"],
                "Sustainable Carbon (kg)": sust["carbon_emissions_per_unit"],
                "Carbon Reduction (%)": round(carbon_red, 1),
                "Water Saved (liters)": trad["water_consumption_per_unit"] - sust["water_consumption_per_unit"],
                "Waste Reduced (kg)": trad["waste_generated_per_unit"] - sust["waste_generated_per_unit"],
            }
        )
    return pd.DataFrame(rows)
