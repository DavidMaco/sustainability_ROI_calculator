"""Tests for production-completeness features (NPV + adapters + perf artifacts)."""

from __future__ import annotations

import json
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pandas as pd
import pytest

import config as cfg
from domain.materials import generate_material_profiles
from domain.monte_carlo import run_monte_carlo
from domain.optimization import optimize_switches
from domain.scenarios import calculate_custom_scenario, calculate_scenario_impacts, generate_company_scenarios_df
from ingestion.external_api_adapter import ExternalApiAdapter
from ingestion.factory import get_data_adapter
from ingestion.sqlite_adapter import SQLiteAdapter


@pytest.fixture()
def materials_df() -> pd.DataFrame:
    return generate_material_profiles()


def test_scenario_results_include_npv(materials_df: pd.DataFrame):
    scenarios_df = generate_company_scenarios_df()
    results = calculate_scenario_impacts(scenarios_df, materials_df)
    assert all(hasattr(r, "npv_net_benefit_ngn") for r in results)
    assert all(hasattr(r, "project_irr_pct") for r in results)


def test_custom_scenario_discounted_metrics(materials_df: pd.DataFrame):
    result = calculate_custom_scenario(materials_df, {"Sugar": 1200})
    assert isinstance(result.npv_net_benefit_ngn, float)
    assert hasattr(result, "project_irr_pct")


def test_sqlite_adapter_round_trip():
    temp_dir = Path(tempfile.mkdtemp(prefix="sroi_sqlite_test_"))
    db_path = temp_dir / "sroi.db"
    adapter = SQLiteAdapter(db_path=db_path)

    sample_df = pd.DataFrame([{"a": 1, "b": "x"}, {"a": 2, "b": "y"}])
    adapter.save_materials(sample_df)
    loaded = adapter.load_materials()

    pd.testing.assert_frame_equal(sample_df, loaded)


def test_factory_rejects_api_for_writes(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(cfg, "DATA_BACKEND", "api")
    with pytest.raises(RuntimeError, match="read-only"):
        get_data_adapter(require_writable=True)


def test_optimization_respects_budget(materials_df: pd.DataFrame):
    scenarios_df = generate_company_scenarios_df()
    recs = optimize_switches(
        materials_df,
        scenarios_df,
        budget_increase_limit_ngn=0,
        min_carbon_reduction_pct=0,
    )
    selected = recs[recs["selected"]]
    assert float(selected["cost_delta_ngn"].sum()) <= 0


def test_monte_carlo_generates_bounds(materials_df: pd.DataFrame):
    scenarios_df = generate_company_scenarios_df()
    results = calculate_scenario_impacts(scenarios_df, materials_df)
    results_df = pd.DataFrame([r.model_dump() for r in results])

    samples_df, bounds = run_monte_carlo(
        results_df,
        simulations=200,
        seed=42,
        rate_std_dev=0.1,
        discount_std_dev=0.01,
    )

    assert len(samples_df) == 200
    assert "p50_npv_net_benefit_ngn" in bounds
    assert bounds["p95_npv_net_benefit_ngn"] >= bounds["p05_npv_net_benefit_ngn"]


def test_external_api_adapter_contract_round_trip():
    payloads = {
        "/materials": [{"material_category": "Sugar", "option_type": "Traditional"}],
        "/scenarios": [{"company_name": "Test Co", "materials_mix": {"Sugar": 10}}],
        "/results": [{"company_name": "Test Co", "net_annual_impact_ngn": 12345}],
        "/summary": {"total_net_benefit": 12345},
    }

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            payload = payloads.get(self.path)
            if payload is None:
                self.send_response(404)
                self.end_headers()
                return
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base_url = f"http://127.0.0.1:{server.server_port}"
        adapter = ExternalApiAdapter(base_url)

        materials = adapter.load_materials()
        scenarios = adapter.load_scenarios()
        results = adapter.load_results()
        summary = adapter.load_summary()

        assert list(materials.columns) == ["material_category", "option_type"]
        assert list(scenarios.columns) == ["company_name", "materials_mix"]
        assert list(results.columns) == ["company_name", "net_annual_impact_ngn"]
        assert summary["total_net_benefit"] == 12345
    finally:
        server.shutdown()
        server.server_close()
