"""Pydantic models defining all data contracts."""

from __future__ import annotations

from pydantic import BaseModel, Field


class MaterialProfile(BaseModel):
    material_category: str
    option_type: str  # "Traditional" | "Sustainable"
    material_name: str
    unit_of_measure: str = "Ton"
    carbon_emissions_per_unit: float = Field(ge=0)
    water_consumption_per_unit: float = Field(ge=0)
    waste_generated_per_unit: float = Field(ge=0)
    base_price_ngn_per_unit: float = Field(ge=0)
    sustainability_certification: str = "None"
    recyclability_pct: float = Field(ge=0, le=100)
    biodegradability: bool = False
    price_premium_pct: float | None = None


class CompanyScenario(BaseModel):
    company_name: str
    industry: str
    annual_revenue_ngn: float
    current_sustainability_score: float
    target_sustainability_score: float
    target_year: int
    annual_procurement_spend_ngn: float
    current_carbon_footprint_tons: float
    target_carbon_reduction_pct: float
    materials_mix: dict[str, float]  # {material_category: annual_quantity}


class ScenarioResult(BaseModel):
    company_name: str
    industry: str
    traditional_annual_cost_ngn: float
    sustainable_annual_cost_ngn: float
    cost_increase_ngn: float
    cost_increase_pct: float
    carbon_emissions_baseline_tons: float
    carbon_emissions_sustainable_tons: float
    carbon_reduction_tons: float
    carbon_reduction_pct: float
    water_saved_million_liters: float
    waste_reduced_tons: float
    carbon_tax_savings_ngn: float
    water_cost_savings_ngn: float
    waste_disposal_savings_ngn: float
    total_operational_savings_ngn: float
    net_annual_impact_ngn: float
    npv_net_benefit_ngn: float
    project_irr_pct: float | None = None
    roi_pct: float
    payback_period_years: float
    discounted_payback_years: float | None = None
    achieves_target: bool


class CustomScenarioResult(BaseModel):
    cost_increase: float
    cost_increase_pct: float
    carbon_saved_tons: float
    water_saved_million_liters: float
    waste_reduced_tons: float
    carbon_tax_savings_ngn: float
    water_cost_savings_ngn: float
    waste_disposal_savings_ngn: float
    operational_savings: float
    net_impact: float
    npv_net_benefit_ngn: float
    project_irr_pct: float | None = None
    roi_pct: float
    payback_years: float | None = None
    discounted_payback_years: float | None = None


class SummaryMetrics(BaseModel):
    total_cost_increase: float
    total_carbon_reduction_tons: float
    total_operational_savings: float
    total_net_benefit: float
    total_npv_net_benefit: float
    avg_project_irr_pct: float | None = None
    avg_roi_pct: float
    avg_payback_years: float
