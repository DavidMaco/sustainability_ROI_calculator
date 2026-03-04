"""Material sustainability profiles — generation and lookup."""

from __future__ import annotations

import random

import numpy as np
import pandas as pd

import config as cfg

# ─── Raw data definitions (authoritative source of truth) ────────────

RAW_MATERIALS = [
    {
        "category": "Sugar",
        "traditional": {
            "name": "Conventional Sugar",
            "carbon_kg_per_ton": 450,
            "water_liters_per_ton": 1500,
            "waste_kg_per_ton": 120,
        },
        "sustainable": {
            "name": "Organic Fair Trade Sugar",
            "carbon_kg_per_ton": 280,
            "water_liters_per_ton": 900,
            "waste_kg_per_ton": 60,
        },
        "price_premium_pct": 18,
    },
    {
        "category": "Palm Oil",
        "traditional": {
            "name": "Conventional Palm Oil",
            "carbon_kg_per_ton": 3500,
            "water_liters_per_ton": 2000,
            "waste_kg_per_ton": 200,
        },
        "sustainable": {
            "name": "RSPO Certified Palm Oil",
            "carbon_kg_per_ton": 1800,
            "water_liters_per_ton": 1200,
            "waste_kg_per_ton": 80,
        },
        "price_premium_pct": 25,
    },
    {
        "category": "Cocoa",
        "traditional": {
            "name": "Standard Cocoa",
            "carbon_kg_per_ton": 2800,
            "water_liters_per_ton": 25000,
            "waste_kg_per_ton": 150,
        },
        "sustainable": {
            "name": "Rainforest Alliance Cocoa",
            "carbon_kg_per_ton": 1600,
            "water_liters_per_ton": 18000,
            "waste_kg_per_ton": 70,
        },
        "price_premium_pct": 22,
    },
    {
        "category": "Flour",
        "traditional": {
            "name": "Standard Wheat Flour",
            "carbon_kg_per_ton": 380,
            "water_liters_per_ton": 1200,
            "waste_kg_per_ton": 90,
        },
        "sustainable": {
            "name": "Organic Wheat Flour",
            "carbon_kg_per_ton": 240,
            "water_liters_per_ton": 800,
            "waste_kg_per_ton": 45,
        },
        "price_premium_pct": 15,
    },
]

PACKAGING_MATERIALS = [
    {
        "category": "Plastic Bottles (PET)",
        "traditional": {
            "name": "Virgin PET",
            "carbon_kg_per_ton": 3200,
            "water_liters_per_ton": 180,
            "waste_kg_per_ton": 50,
        },
        "sustainable": {
            "name": "Recycled PET (rPET)",
            "carbon_kg_per_ton": 1400,
            "water_liters_per_ton": 90,
            "waste_kg_per_ton": 20,
        },
        "price_premium_pct": 12,
    },
    {
        "category": "Cardboard Cartons",
        "traditional": {
            "name": "Standard Cardboard",
            "carbon_kg_per_ton": 950,
            "water_liters_per_ton": 50000,
            "waste_kg_per_ton": 80,
        },
        "sustainable": {
            "name": "FSC Certified Recycled Board",
            "carbon_kg_per_ton": 580,
            "water_liters_per_ton": 25000,
            "waste_kg_per_ton": 30,
        },
        "price_premium_pct": 8,
    },
    {
        "category": "Glass Bottles",
        "traditional": {
            "name": "Virgin Glass",
            "carbon_kg_per_ton": 850,
            "water_liters_per_ton": 300,
            "waste_kg_per_ton": 100,
        },
        "sustainable": {
            "name": "Recycled Glass (70%)",
            "carbon_kg_per_ton": 520,
            "water_liters_per_ton": 180,
            "waste_kg_per_ton": 40,
        },
        "price_premium_pct": 5,
    },
    {
        "category": "Aluminum Cans",
        "traditional": {
            "name": "Virgin Aluminum",
            "carbon_kg_per_ton": 11500,
            "water_liters_per_ton": 150,
            "waste_kg_per_ton": 60,
        },
        "sustainable": {
            "name": "Recycled Aluminum",
            "carbon_kg_per_ton": 650,
            "water_liters_per_ton": 45,
            "waste_kg_per_ton": 15,
        },
        "price_premium_pct": -3,
    },
]

ENERGY_SOURCES = [
    {
        "category": "Electricity (Grid)",
        "traditional": {
            "name": "Coal/Gas Grid Power",
            "carbon_kg_per_mwh": 820,
            "water_liters_per_mwh": 2000,
            "waste_kg_per_mwh": 5,
        },
        "sustainable": {
            "name": "Solar/Wind Power",
            "carbon_kg_per_mwh": 50,
            "water_liters_per_mwh": 100,
            "waste_kg_per_mwh": 1,
        },
        "price_premium_pct": -5,
        "unit": "MWh",
    },
    {
        "category": "Transportation Fuel",
        "traditional": {
            "name": "Diesel",
            "carbon_kg_per_liter": 2.7,
            "water_liters_per_liter": 1.5,
            "waste_kg_per_liter": 0.05,
        },
        "sustainable": {
            "name": "Biodiesel (B20)",
            "carbon_kg_per_liter": 2.0,
            "water_liters_per_liter": 1.2,
            "waste_kg_per_liter": 0.03,
        },
        "price_premium_pct": 10,
        "unit": "Liter",
    },
]

ALL_MATERIAL_DEFS = RAW_MATERIALS + PACKAGING_MATERIALS + ENERGY_SOURCES


# Explicit mapping from metric name → key prefix patterns
_METRIC_KEY_PREFIXES: dict[str, str] = {
    "carbon": "carbon_",
    "water": "water_",
    "waste": "waste_",
}


def _extract_metric(d: dict, metric: str) -> float:
    """Pull carbon/water/waste value from a material dict by matching key prefix."""
    prefix = _METRIC_KEY_PREFIXES.get(metric)
    if prefix is None:
        raise ValueError(f"Unknown metric '{metric}'. Expected one of: {list(_METRIC_KEY_PREFIXES)}")
    for k, v in d.items():
        if k.startswith(prefix):
            return float(v)
    return 0.0


def generate_material_profiles() -> pd.DataFrame:
    """Generate the canonical material comparison table. Deterministic with cfg.RANDOM_SEED."""
    np.random.seed(cfg.RANDOM_SEED)
    random.seed(cfg.RANDOM_SEED)

    rows: list[dict] = []
    for item in ALL_MATERIAL_DEFS:
        unit = item.get("unit", "Ton")
        trad = item["traditional"]
        sust = item["sustainable"]

        rows.append(
            {
                "material_category": item["category"],
                "option_type": "Traditional",
                "material_name": trad["name"],
                "unit_of_measure": unit,
                "carbon_emissions_per_unit": _extract_metric(trad, "carbon"),
                "water_consumption_per_unit": _extract_metric(trad, "water"),
                "waste_generated_per_unit": _extract_metric(trad, "waste"),
                "base_price_ngn_per_unit": 0.0,
                "sustainability_certification": "None",
                "recyclability_pct": random.randint(10, 30),
                "biodegradability": False,
                "price_premium_pct": None,
            }
        )
        rows.append(
            {
                "material_category": item["category"],
                "option_type": "Sustainable",
                "material_name": sust["name"],
                "unit_of_measure": unit,
                "carbon_emissions_per_unit": _extract_metric(sust, "carbon"),
                "water_consumption_per_unit": _extract_metric(sust, "water"),
                "waste_generated_per_unit": _extract_metric(sust, "waste"),
                "base_price_ngn_per_unit": 0.0,
                "sustainability_certification": random.choice(
                    ["Organic", "Fair Trade", "RSPO", "FSC", "B-Corp", "Rainforest Alliance"]
                ),
                "recyclability_pct": random.randint(70, 95),
                "biodegradability": random.choice([True, False, True]),
                "price_premium_pct": item["price_premium_pct"],
            }
        )

    df = pd.DataFrame(rows)
    df["base_price_ngn_per_unit"] = df["base_price_ngn_per_unit"].astype(float)

    # Assign prices per category (deterministic via seed)
    for category in df["material_category"].unique():
        base_price = random.uniform(50_000, 500_000)
        mask_trad = (df["material_category"] == category) & (df["option_type"] == "Traditional")
        df.loc[mask_trad, "base_price_ngn_per_unit"] = base_price

        sust_row = df[(df["material_category"] == category) & (df["option_type"] == "Sustainable")]
        if len(sust_row) > 0:
            premium = sust_row.iloc[0].get("price_premium_pct")
            if premium is None or pd.isna(premium):
                premium = 0
            df.loc[sust_row.index, "base_price_ngn_per_unit"] = base_price * (1 + premium / 100)

    df["base_price_ngn_per_unit"] = df["base_price_ngn_per_unit"].round(2)
    return df
