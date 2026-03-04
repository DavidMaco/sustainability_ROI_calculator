"""Unit tests for domain calculation logic."""

import pandas as pd
import pytest

from domain.materials import generate_material_profiles
from domain.recommendations import build_material_comparison_table, identify_quick_wins
from domain.scenarios import (
    calculate_custom_scenario,
    calculate_scenario_impacts,
    compute_summary_metrics,
    generate_company_scenarios_df,
)

# ─── Fixtures ────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def materials_df() -> pd.DataFrame:
    return generate_material_profiles()


@pytest.fixture(scope="module")
def scenarios_df() -> pd.DataFrame:
    return generate_company_scenarios_df()


# ─── Material generation ─────────────────────────────────────────────


def test_materials_deterministic(materials_df: pd.DataFrame):
    """Same seed must produce identical output."""
    df2 = generate_material_profiles()
    pd.testing.assert_frame_equal(materials_df, df2)


def test_materials_has_expected_categories(materials_df: pd.DataFrame):
    expected = {
        "Sugar",
        "Palm Oil",
        "Cocoa",
        "Flour",
        "Plastic Bottles (PET)",
        "Cardboard Cartons",
        "Glass Bottles",
        "Aluminum Cans",
        "Electricity (Grid)",
        "Transportation Fuel",
    }
    assert set(materials_df["material_category"].unique()) == expected


def test_materials_pairs(materials_df: pd.DataFrame):
    """Each category must have exactly one Traditional and one Sustainable row."""
    for cat in materials_df["material_category"].unique():
        subset = materials_df[materials_df["material_category"] == cat]
        assert set(subset["option_type"]) == {"Traditional", "Sustainable"}
        assert len(subset) == 2


def test_prices_positive(materials_df: pd.DataFrame):
    assert (materials_df["base_price_ngn_per_unit"] > 0).all()


def test_emissions_non_negative(materials_df: pd.DataFrame):
    for col in ["carbon_emissions_per_unit", "water_consumption_per_unit", "waste_generated_per_unit"]:
        assert (materials_df[col] >= 0).all()


# ─── Scenario impacts ───────────────────────────────────────────────


def test_scenario_impacts_count(materials_df, scenarios_df):
    results = calculate_scenario_impacts(scenarios_df, materials_df)
    assert len(results) == len(scenarios_df)


def test_scenario_impacts_positive_carbon_reduction(materials_df, scenarios_df):
    results = calculate_scenario_impacts(scenarios_df, materials_df)
    for r in results:
        assert r.carbon_reduction_tons > 0, f"{r.company_name} should reduce carbon"


def test_scenario_impacts_positive_savings(materials_df, scenarios_df):
    results = calculate_scenario_impacts(scenarios_df, materials_df)
    for r in results:
        assert r.total_operational_savings_ngn > 0


def test_summary_metrics(materials_df, scenarios_df):
    results = calculate_scenario_impacts(scenarios_df, materials_df)
    summary = compute_summary_metrics(results)
    assert summary.total_carbon_reduction_tons > 0
    assert summary.total_operational_savings > 0
    assert summary.avg_payback_years > 0


# ─── Custom scenario ────────────────────────────────────────────────


def test_custom_scenario_single_material(materials_df):
    result = calculate_custom_scenario(materials_df, {"Sugar": 1000})
    assert result.carbon_saved_tons > 0
    assert result.operational_savings > 0


def test_custom_scenario_empty_mix(materials_df):
    result = calculate_custom_scenario(materials_df, {})
    assert result.cost_increase == 0
    assert result.roi_pct == 0


def test_custom_scenario_negative_premium_material(materials_df):
    """Aluminum has negative premium — cost_increase should be negative."""
    result = calculate_custom_scenario(materials_df, {"Aluminum Cans": 1000})
    assert result.cost_increase < 0, "Recycled aluminum should be cheaper"


# ─── Recommendations ────────────────────────────────────────────────


def test_quick_wins_non_empty(materials_df):
    qw = identify_quick_wins(materials_df)
    assert len(qw) > 0, "Should find at least one quick win"


def test_comparison_table_shape(materials_df):
    table = build_material_comparison_table(materials_df)
    assert len(table) == materials_df["material_category"].nunique()
    assert "Carbon Reduction (%)" in table.columns


# ─── ROI sanity checks (guard against unit-conversion regressions) ───


def test_scenario_roi_realistic(materials_df, scenarios_df):
    """ROI should be in a reasonable range — not 1000x inflated."""
    results = calculate_scenario_impacts(scenarios_df, materials_df)
    for r in results:
        assert r.roi_pct < 500, f"{r.company_name} ROI {r.roi_pct:.0f}% is implausibly high (unit-conversion bug?)"


def test_custom_and_scenario_savings_consistent(materials_df):
    """Both scenario functions should produce comparable savings for the same input."""
    test_mix = {"Sugar": 5000}
    custom_result = calculate_custom_scenario(materials_df, test_mix)
    scenario_df = pd.DataFrame(
        [
            {
                "company_name": "Test Co",
                "industry": "Test",
                "annual_revenue_ngn": 1_000_000_000,
                "current_sustainability_score": 50,
                "target_sustainability_score": 75,
                "target_year": 2030,
                "annual_procurement_spend_ngn": 500_000_000,
                "current_carbon_footprint_tons": 10_000,
                "target_carbon_reduction_pct": 50,
                "materials_mix": test_mix,
            }
        ]
    )
    scenario_result = calculate_scenario_impacts(scenario_df, materials_df)[0]

    # Both should agree on operational savings within 1% (same formulas, different paths)
    assert abs(scenario_result.total_operational_savings_ngn - custom_result.operational_savings) < abs(
        custom_result.operational_savings * 0.01
    ), "Scenario and custom functions disagree on operational savings — possible unit-conversion mismatch"


# ─── Input validation ────────────────────────────────────────────────


def test_invalid_material_raises_error(materials_df):
    """Unknown material category should raise ValueError, not IndexError."""
    with pytest.raises(ValueError, match="not found in materials data"):
        calculate_custom_scenario(materials_df, {"NonexistentMaterial": 100})
