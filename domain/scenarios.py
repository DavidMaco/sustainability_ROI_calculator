"""Scenario impact calculations — pure functions, no I/O."""

from __future__ import annotations

import json
from ast import literal_eval
from typing import Any

import pandas as pd

import config as cfg
from domain.models import CustomScenarioResult, ScenarioResult, SummaryMetrics

# ─── Predefined company scenarios ────────────────────────────────────

COMPANY_SCENARIOS: list[dict] = [
    {
        "company_name": "Premium Beverages Nigeria Ltd",
        "industry": "Beverage Manufacturing",
        "annual_revenue_ngn": 85_000_000_000,
        "current_sustainability_score": 42,
        "target_sustainability_score": 75,
        "target_year": 2030,
        "annual_procurement_spend_ngn": 25_000_000_000,
        "current_carbon_footprint_tons": 45_000,
        "target_carbon_reduction_pct": 50,
        "materials_mix": {
            "Sugar": 5000,
            "Plastic Bottles (PET)": 3000,
            "Aluminum Cans": 1500,
            "Cardboard Cartons": 800,
            "Electricity (Grid)": 50000,
            "Transportation Fuel": 200000,
        },
    },
    {
        "company_name": "Golden Grains Foods",
        "industry": "Food Processing",
        "annual_revenue_ngn": 42_000_000_000,
        "current_sustainability_score": 38,
        "target_sustainability_score": 70,
        "target_year": 2030,
        "annual_procurement_spend_ngn": 18_000_000_000,
        "current_carbon_footprint_tons": 28_000,
        "target_carbon_reduction_pct": 45,
        "materials_mix": {
            "Flour": 8000,
            "Palm Oil": 1200,
            "Cardboard Cartons": 2000,
            "Plastic Bottles (PET)": 500,
            "Electricity (Grid)": 35000,
            "Transportation Fuel": 150000,
        },
    },
    {
        "company_name": "Sweet Treats Manufacturing",
        "industry": "Confectionery",
        "annual_revenue_ngn": 28_000_000_000,
        "current_sustainability_score": 35,
        "target_sustainability_score": 65,
        "target_year": 2030,
        "annual_procurement_spend_ngn": 12_000_000_000,
        "current_carbon_footprint_tons": 18_000,
        "target_carbon_reduction_pct": 40,
        "materials_mix": {
            "Sugar": 4000,
            "Cocoa": 800,
            "Palm Oil": 600,
            "Cardboard Cartons": 1200,
            "Plastic Bottles (PET)": 300,
            "Aluminum Cans": 200,
            "Electricity (Grid)": 25000,
            "Transportation Fuel": 100000,
        },
    },
]


def _projected_cashflow(base_cashflow: float, year: int, growth_rate: float) -> float:
    return base_cashflow * ((1 + growth_rate) ** (year - 1))


def _discount(value: float, year: int, discount_rate: float) -> float:
    return value / ((1 + discount_rate) ** year)


def _npv(base_cashflow: float, years: int, discount_rate: float, growth_rate: float) -> float:
    return sum(
        _discount(_projected_cashflow(base_cashflow, y, growth_rate), y, discount_rate) for y in range(1, years + 1)
    )


def _discounted_payback_years(
    cost_increase: float, annual_savings: float, years: int, discount_rate: float, growth_rate: float
) -> float | None:
    if cost_increase <= 0:
        return 0.0
    if annual_savings <= 0:
        return None

    cumulative = 0.0
    for y in range(1, years + 1):
        cumulative += _discount(_projected_cashflow(annual_savings, y, growth_rate), y, discount_rate)
        if cumulative >= cost_increase:
            return float(y)
    return None


def generate_company_scenarios_df() -> pd.DataFrame:
    """Return the predefined company scenarios as a DataFrame."""
    return pd.DataFrame(COMPANY_SCENARIOS)


def calculate_scenario_impacts(scenarios_df: pd.DataFrame, materials_df: pd.DataFrame) -> list[ScenarioResult]:
    """Calculate financial and environmental impact for each company scenario.

    NOTE: Legacy code omitted kg→ton conversion for carbon/waste savings.
    Fixed in v2.0.1 — all savings now use consistent unit conversion.
    """
    available_categories = set(materials_df["material_category"].unique())
    results: list[ScenarioResult] = []

    for _, company in scenarios_df.iterrows():
        company_name = str(company["company_name"])
        industry = str(company["industry"])
        target_carbon_reduction_pct = float(company["target_carbon_reduction_pct"])

        mix: Any = company["materials_mix"]
        if isinstance(mix, str):
            try:
                mix = json.loads(mix)
            except json.JSONDecodeError:
                parsed = literal_eval(mix)
                if not isinstance(parsed, dict):
                    raise TypeError(f"Expected dict for materials_mix, got {type(parsed).__name__}")
                mix = parsed
        if not isinstance(mix, dict):
            raise TypeError(f"Expected dict for materials_mix, got {type(mix).__name__}")

        trad_cost = trad_carbon = trad_water = trad_waste = 0.0
        sust_cost = sust_carbon = sust_water = sust_waste = 0.0

        for material, quantity in mix.items():
            if material not in available_categories:
                raise ValueError(
                    f"Material '{material}' in scenario '{company_name}' "
                    f"not found in materials data. Available: {sorted(available_categories)}"
                )
            quantity = float(quantity)
            trad = materials_df[
                (materials_df["material_category"] == material) & (materials_df["option_type"] == "Traditional")
            ].iloc[0]
            sust = materials_df[
                (materials_df["material_category"] == material) & (materials_df["option_type"] == "Sustainable")
            ].iloc[0]

            trad_cost += trad["base_price_ngn_per_unit"] * quantity
            trad_carbon += trad["carbon_emissions_per_unit"] * quantity
            trad_water += trad["water_consumption_per_unit"] * quantity
            trad_waste += trad["waste_generated_per_unit"] * quantity

            sust_cost += sust["base_price_ngn_per_unit"] * quantity
            sust_carbon += sust["carbon_emissions_per_unit"] * quantity
            sust_water += sust["water_consumption_per_unit"] * quantity
            sust_waste += sust["waste_generated_per_unit"] * quantity

        cost_change = sust_cost - trad_cost
        carbon_saved = trad_carbon - sust_carbon
        water_saved = trad_water - sust_water
        waste_reduced = trad_waste - sust_waste

        # Operational savings — convert kg→tons before applying per-ton rates
        carbon_tax_savings = (carbon_saved / 1000) * cfg.CARBON_TAX_NGN_PER_TON
        water_cost_savings = (water_saved / 1000) * cfg.WATER_COST_NGN_PER_1000L
        waste_savings = (waste_reduced / 1000) * cfg.WASTE_COST_NGN_PER_TON

        operational_savings = carbon_tax_savings + water_cost_savings + waste_savings
        net_annual_impact = operational_savings - cost_change
        npv_net_benefit = _npv(
            net_annual_impact,
            years=cfg.ANALYSIS_YEARS,
            discount_rate=cfg.DISCOUNT_RATE,
            growth_rate=cfg.ANNUAL_NET_BENEFIT_GROWTH_RATE,
        )
        roi_pct = (net_annual_impact / abs(cost_change) * 100) if cost_change != 0 else 0.0
        payback_years = abs(cost_change) / operational_savings if operational_savings > 0 else 999.0
        discounted_payback = _discounted_payback_years(
            cost_change,
            operational_savings,
            years=cfg.ANALYSIS_YEARS,
            discount_rate=cfg.DISCOUNT_RATE,
            growth_rate=cfg.ANNUAL_NET_BENEFIT_GROWTH_RATE,
        )

        results.append(
            ScenarioResult(
                company_name=company_name,
                industry=industry,
                traditional_annual_cost_ngn=trad_cost,
                sustainable_annual_cost_ngn=sust_cost,
                cost_increase_ngn=cost_change,
                cost_increase_pct=(cost_change / trad_cost * 100) if trad_cost > 0 else 0.0,
                carbon_emissions_baseline_tons=trad_carbon / 1000,
                carbon_emissions_sustainable_tons=sust_carbon / 1000,
                carbon_reduction_tons=carbon_saved / 1000,
                carbon_reduction_pct=(carbon_saved / trad_carbon * 100) if trad_carbon > 0 else 0.0,
                water_saved_million_liters=water_saved / 1_000_000,
                waste_reduced_tons=waste_reduced / 1000,
                carbon_tax_savings_ngn=carbon_tax_savings,
                water_cost_savings_ngn=water_cost_savings,
                waste_disposal_savings_ngn=waste_savings,
                total_operational_savings_ngn=operational_savings,
                net_annual_impact_ngn=net_annual_impact,
                npv_net_benefit_ngn=npv_net_benefit,
                roi_pct=roi_pct,
                payback_period_years=min(payback_years, 20),
                discounted_payback_years=discounted_payback,
                achieves_target=(
                    (carbon_saved / trad_carbon * 100) >= target_carbon_reduction_pct if trad_carbon > 0 else False
                ),
            )
        )
    return results


def calculate_custom_scenario(
    materials_df: pd.DataFrame,
    custom_mix: dict[str, float],
    carbon_tax_ngn_per_ton: float | None = None,
    water_cost_ngn_per_1000l: float | None = None,
    waste_cost_ngn_per_ton: float | None = None,
) -> CustomScenarioResult:
    """Calculate ROI for an arbitrary material mix.

    Preserves the exact formulas from legacy analyze_sustainability.py.
    """
    available_categories = set(materials_df["material_category"].unique())
    trad_cost = sust_cost = 0.0
    carbon_saved = water_saved = waste_reduced = 0.0

    for material, quantity in custom_mix.items():
        if material not in available_categories:
            raise ValueError(
                f"Material '{material}' not found in materials data. " f"Available: {sorted(available_categories)}"
            )
        quantity = float(quantity)
        trad = materials_df[
            (materials_df["material_category"] == material) & (materials_df["option_type"] == "Traditional")
        ].iloc[0]
        sust = materials_df[
            (materials_df["material_category"] == material) & (materials_df["option_type"] == "Sustainable")
        ].iloc[0]

        trad_cost += trad["base_price_ngn_per_unit"] * quantity
        sust_cost += sust["base_price_ngn_per_unit"] * quantity
        carbon_saved += (trad["carbon_emissions_per_unit"] - sust["carbon_emissions_per_unit"]) * quantity
        water_saved += (trad["water_consumption_per_unit"] - sust["water_consumption_per_unit"]) * quantity
        waste_reduced += (trad["waste_generated_per_unit"] - sust["waste_generated_per_unit"]) * quantity

    carbon_tax_rate = carbon_tax_ngn_per_ton if carbon_tax_ngn_per_ton is not None else cfg.CARBON_TAX_NGN_PER_TON
    water_cost_rate = water_cost_ngn_per_1000l if water_cost_ngn_per_1000l is not None else cfg.WATER_COST_NGN_PER_1000L
    waste_cost_rate = waste_cost_ngn_per_ton if waste_cost_ngn_per_ton is not None else cfg.WASTE_COST_NGN_PER_TON

    # Operational savings — consistent unit conversion across both functions
    carbon_tax_savings = (carbon_saved / 1000) * carbon_tax_rate  # kg → tons
    water_cost_savings = (water_saved / 1000) * water_cost_rate  # liters → thousands of liters
    waste_savings = (waste_reduced / 1000) * waste_cost_rate  # kg → tons

    operational_savings = carbon_tax_savings + water_cost_savings + waste_savings
    cost_increase = sust_cost - trad_cost
    net_impact = operational_savings - cost_increase
    npv_net_benefit = _npv(
        net_impact,
        years=cfg.ANALYSIS_YEARS,
        discount_rate=cfg.DISCOUNT_RATE,
        growth_rate=cfg.ANNUAL_NET_BENEFIT_GROWTH_RATE,
    )
    roi = (net_impact / abs(cost_increase) * 100) if cost_increase != 0 else 0.0
    payback = (cost_increase / operational_savings) if (cost_increase > 0 and operational_savings > 0) else None
    discounted_payback = _discounted_payback_years(
        cost_increase,
        operational_savings,
        years=cfg.ANALYSIS_YEARS,
        discount_rate=cfg.DISCOUNT_RATE,
        growth_rate=cfg.ANNUAL_NET_BENEFIT_GROWTH_RATE,
    )

    return CustomScenarioResult(
        cost_increase=cost_increase,
        cost_increase_pct=(cost_increase / trad_cost * 100) if trad_cost > 0 else 0.0,
        carbon_saved_tons=carbon_saved / 1000,
        water_saved_million_liters=water_saved / 1_000_000,
        waste_reduced_tons=waste_reduced / 1000,
        carbon_tax_savings_ngn=carbon_tax_savings,
        water_cost_savings_ngn=water_cost_savings,
        waste_disposal_savings_ngn=waste_savings,
        operational_savings=operational_savings,
        net_impact=net_impact,
        npv_net_benefit_ngn=npv_net_benefit,
        roi_pct=roi,
        payback_years=payback,
        discounted_payback_years=discounted_payback,
    )


def compute_summary_metrics(results: list[ScenarioResult]) -> SummaryMetrics:
    """Aggregate metrics across all scenario results."""
    n = len(results)
    return SummaryMetrics(
        total_cost_increase=sum(r.cost_increase_ngn for r in results),
        total_carbon_reduction_tons=sum(r.carbon_reduction_tons for r in results),
        total_operational_savings=sum(r.total_operational_savings_ngn for r in results),
        total_net_benefit=sum(r.net_annual_impact_ngn for r in results),
        total_npv_net_benefit=sum(r.npv_net_benefit_ngn for r in results),
        avg_roi_pct=sum(r.roi_pct for r in results) / n if n else 0.0,
        avg_payback_years=sum(r.payback_period_years for r in results) / n if n else 0.0,
    )
