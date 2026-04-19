"""Monte Carlo sensitivity analysis for ROI assumptions."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import config as cfg


def _projected_cashflow(base_cashflow: float, year: int, growth_rate: float) -> float:
    return base_cashflow * ((1 + growth_rate) ** (year - 1))


def _npv(base_cashflow: float, years: int, discount_rate: float, growth_rate: float) -> float:
    return sum(
        _projected_cashflow(base_cashflow, year, growth_rate) / ((1 + discount_rate) ** year)
        for year in range(1, years + 1)
    )


def run_monte_carlo(
    results_df: pd.DataFrame,
    *,
    simulations: int,
    seed: int,
    rate_std_dev: float,
    discount_std_dev: float,
) -> tuple[pd.DataFrame, dict[str, float]]:
    """Run simulation over key economic assumptions and return samples + bounds."""
    rng = np.random.default_rng(seed)

    sample_rows: list[dict[str, float]] = []

    for sim in range(simulations):
        carbon_mult = max(0.01, float(rng.normal(1.0, rate_std_dev)))
        water_mult = max(0.01, float(rng.normal(1.0, rate_std_dev)))
        waste_mult = max(0.01, float(rng.normal(1.0, rate_std_dev)))
        discount_rate = float(np.clip(rng.normal(cfg.DISCOUNT_RATE, discount_std_dev), 0.001, 0.99))

        scenario_net_annual = (
            results_df["carbon_tax_savings_ngn"] * carbon_mult
            + results_df["water_cost_savings_ngn"] * water_mult
            + results_df["waste_disposal_savings_ngn"] * waste_mult
            - results_df["cost_increase_ngn"]
        )
        total_net_annual = float(scenario_net_annual.sum())
        total_npv = _npv(
            total_net_annual,
            years=cfg.ANALYSIS_YEARS,
            discount_rate=discount_rate,
            growth_rate=cfg.ANNUAL_NET_BENEFIT_GROWTH_RATE,
        )

        sample_rows.append(
            {
                "simulation": sim + 1,
                "carbon_multiplier": carbon_mult,
                "water_multiplier": water_mult,
                "waste_multiplier": waste_mult,
                "discount_rate": discount_rate,
                "net_annual_benefit_ngn": total_net_annual,
                "npv_net_benefit_ngn": total_npv,
            }
        )

    samples_df = pd.DataFrame(sample_rows)

    bounds = {
        "p05_net_annual_benefit_ngn": float(samples_df["net_annual_benefit_ngn"].quantile(0.05)),
        "p50_net_annual_benefit_ngn": float(samples_df["net_annual_benefit_ngn"].quantile(0.50)),
        "p95_net_annual_benefit_ngn": float(samples_df["net_annual_benefit_ngn"].quantile(0.95)),
        "p05_npv_net_benefit_ngn": float(samples_df["npv_net_benefit_ngn"].quantile(0.05)),
        "p50_npv_net_benefit_ngn": float(samples_df["npv_net_benefit_ngn"].quantile(0.50)),
        "p95_npv_net_benefit_ngn": float(samples_df["npv_net_benefit_ngn"].quantile(0.95)),
        "simulations": float(simulations),
    }
    return samples_df, bounds


def persist_monte_carlo_outputs(
    samples_df: pd.DataFrame, bounds: dict[str, float], output_dir: Path
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    samples_path = output_dir / "monte_carlo_samples.csv"
    bounds_path = output_dir / "monte_carlo_bounds.json"

    samples_df.to_csv(samples_path, index=False)
    bounds_path.write_text(json.dumps(bounds, indent=2), encoding="utf-8")
    return samples_path, bounds_path
