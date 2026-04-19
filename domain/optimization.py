"""Constraint-aware portfolio optimization for sustainable material switching."""

from __future__ import annotations

import json
from ast import literal_eval

import pandas as pd


def _parse_mix(value: object) -> dict[str, float]:
    if isinstance(value, dict):
        return {str(k): float(v) for k, v in value.items()}
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            parsed = literal_eval(value)
        if isinstance(parsed, dict):
            return {str(k): float(v) for k, v in parsed.items()}
    return {}


def optimize_switches(
    materials_df: pd.DataFrame,
    scenarios_df: pd.DataFrame,
    *,
    budget_increase_limit_ngn: float,
    min_carbon_reduction_pct: float,
) -> pd.DataFrame:
    """Select material-category switches under budget and carbon constraints.

    Strategy:
      1. Aggregate annual volume per material category from scenario mixes.
      2. Compute per-category impact of switching traditional -> sustainable.
      3. Always include non-positive cost deltas (win-win switches).
      4. Greedily include positive-cost switches by carbon reduction per naira.
    """
    volume_map: dict[str, float] = {}
    for _, row in scenarios_df.iterrows():
        mix = _parse_mix(row.get("materials_mix"))
        for material, qty in mix.items():
            volume_map[material] = volume_map.get(material, 0.0) + float(qty)

    categories = sorted(set(materials_df["material_category"].unique()) & set(volume_map.keys()))
    rows: list[dict[str, float | str | bool]] = []

    baseline_carbon_total = 0.0
    max_reduction_total = 0.0

    for material in categories:
        qty = float(volume_map[material])
        trad = materials_df[
            (materials_df["material_category"] == material) & (materials_df["option_type"] == "Traditional")
        ].iloc[0]
        sust = materials_df[
            (materials_df["material_category"] == material) & (materials_df["option_type"] == "Sustainable")
        ].iloc[0]

        delta_cost = (float(sust["base_price_ngn_per_unit"]) - float(trad["base_price_ngn_per_unit"])) * qty
        carbon_reduction_kg = (
            float(trad["carbon_emissions_per_unit"]) - float(sust["carbon_emissions_per_unit"])
        ) * qty
        carbon_reduction_tons = carbon_reduction_kg / 1000
        baseline_carbon_total += float(trad["carbon_emissions_per_unit"]) * qty / 1000
        max_reduction_total += carbon_reduction_tons

        density = 0.0
        if delta_cost > 0 and carbon_reduction_tons > 0:
            density = carbon_reduction_tons / delta_cost

        rows.append(
            {
                "material_category": material,
                "annual_volume": qty,
                "cost_delta_ngn": delta_cost,
                "carbon_reduction_tons": carbon_reduction_tons,
                "carbon_per_naira": density,
                "selected": False,
            }
        )

    candidates = pd.DataFrame(rows)
    if candidates.empty:
        return candidates

    cumulative_cost = 0.0

    # 1) Always include win-win (or neutral) switches.
    win_win_idx = candidates[candidates["cost_delta_ngn"] <= 0].index
    candidates.loc[win_win_idx, "selected"] = True
    cumulative_cost += float(candidates.loc[win_win_idx, "cost_delta_ngn"].sum())

    # 2) Greedy select positive-cost switches by carbon-per-naira.
    remaining_budget = budget_increase_limit_ngn - max(cumulative_cost, 0.0)
    positive_rows = sorted(
        [(idx, row) for idx, row in candidates[candidates["cost_delta_ngn"] > 0].iterrows()],
        key=lambda item: float(item[1]["carbon_per_naira"]),
        reverse=True,
    )
    for idx, row in positive_rows:
        delta = float(row["cost_delta_ngn"])
        if delta <= remaining_budget:
            candidates.at[idx, "selected"] = True
            remaining_budget -= delta
            cumulative_cost += delta

    selected = candidates[candidates["selected"]]
    selected_cost = float(selected["cost_delta_ngn"].sum()) if not selected.empty else 0.0
    selected_reduction = float(selected["carbon_reduction_tons"].sum()) if not selected.empty else 0.0

    achieved_pct = (selected_reduction / baseline_carbon_total * 100) if baseline_carbon_total > 0 else 0.0
    feasible = achieved_pct >= min_carbon_reduction_pct

    candidates["selected_cost_delta_total_ngn"] = selected_cost
    candidates["selected_carbon_reduction_total_tons"] = selected_reduction
    candidates["selected_carbon_reduction_pct"] = achieved_pct
    candidates["target_carbon_reduction_pct"] = min_carbon_reduction_pct
    candidates["constraint_feasible"] = feasible
    candidates["budget_increase_limit_ngn"] = budget_increase_limit_ngn
    candidates["max_possible_carbon_reduction_tons"] = max_reduction_total

    return candidates.sort_values(["selected", "carbon_per_naira"], ascending=[False, False]).reset_index(drop=True)
