"""End-to-end pipeline runner (CLI batch mode)."""

from __future__ import annotations

import logging
import sys
import time

import pandas as pd

import config as cfg
from domain.materials import generate_material_profiles
from domain.recommendations import build_material_comparison_table
from domain.scenarios import (
    calculate_scenario_impacts,
    compute_summary_metrics,
    generate_company_scenarios_df,
)
from ingestion.base import DataAdapter
from ingestion.csv_adapter import CsvAdapter

logger = logging.getLogger(__name__)


def run_pipeline(adapter: DataAdapter | None = None) -> None:
    """Generate data, compute impacts, and persist all artifacts."""
    cfg.validate_runtime_settings()
    adapter = adapter or CsvAdapter()
    start = time.perf_counter()

    logger.info("Step 1/4 — Generating material sustainability profiles")
    materials_df = generate_material_profiles()
    logger.info(
        "  Created %d material options across %d categories",
        len(materials_df),
        materials_df["material_category"].nunique(),
    )

    logger.info("Step 2/4 — Creating company scenarios")
    scenarios_df = generate_company_scenarios_df()
    logger.info("  Created %d company scenarios", len(scenarios_df))

    logger.info("Step 3/4 — Calculating ROI and environmental impact")
    results = calculate_scenario_impacts(scenarios_df, materials_df)
    results_df = pd.DataFrame([r.model_dump() for r in results])
    summary = compute_summary_metrics(results)
    logger.info("  Calculated impact analysis for %d scenarios", len(results))

    logger.info("Step 4/4 — Persisting artifacts")
    adapter.save_materials(materials_df)
    adapter.save_scenarios(scenarios_df)
    adapter.save_results(results_df)
    adapter.save_summary(summary.model_dump())
    adapter.save_calculator_template(build_material_comparison_table(materials_df))

    elapsed = time.perf_counter() - start
    logger.info("Pipeline complete in %.2fs — artifacts in %s", elapsed, adapter.data_dir)

    # Console summary — use errors="replace" to handle ₦ on Windows cp1252 terminals
    def _safe_print(*args: object, **kwargs: object) -> None:
        text = " ".join(str(a) for a in args)
        try:
            print(text, **kwargs)
        except UnicodeEncodeError:
            print(text.encode("ascii", errors="replace").decode("ascii"), **kwargs)

    _safe_print("\n" + "=" * 80)
    _safe_print("SUSTAINABILITY ROI CALCULATOR — PIPELINE RESULTS")
    _safe_print("=" * 80)
    for r in results:
        _safe_print(f"\n{r.company_name} ({r.industry})")
        _safe_print(f"  Cost Increase: {cfg.CURRENCY_SYMBOL}{r.cost_increase_ngn:,.0f} ({r.cost_increase_pct:.1f}%)")
        _safe_print(f"  Carbon Reduction: {r.carbon_reduction_tons:,.0f} tons ({r.carbon_reduction_pct:.1f}%)")
        _safe_print(f"  Operational Savings: {cfg.CURRENCY_SYMBOL}{r.total_operational_savings_ngn:,.0f}/year")
        _safe_print(f"  NET IMPACT: {cfg.CURRENCY_SYMBOL}{r.net_annual_impact_ngn:,.0f}/year")
        _safe_print(f"  ROI: {r.roi_pct:.1f}%  |  Payback: {r.payback_period_years:.1f} years")
        _safe_print(f"  Achieves Target: {'YES' if r.achieves_target else 'NO'}")
    _safe_print("\n" + "=" * 80)
    _safe_print("Pipeline complete — all artifacts saved to:", adapter.data_dir)
    _safe_print("=" * 80)


if __name__ == "__main__":
    run_pipeline()
