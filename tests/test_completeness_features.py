"""Tests for production-completeness features (NPV + adapters + perf artifacts)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pytest

import config as cfg
from domain.materials import generate_material_profiles
from domain.scenarios import calculate_custom_scenario, calculate_scenario_impacts, generate_company_scenarios_df
from ingestion.factory import get_data_adapter
from ingestion.sqlite_adapter import SQLiteAdapter


@pytest.fixture()
def materials_df() -> pd.DataFrame:
    return generate_material_profiles()


def test_scenario_results_include_npv(materials_df: pd.DataFrame):
    scenarios_df = generate_company_scenarios_df()
    results = calculate_scenario_impacts(scenarios_df, materials_df)
    assert all(hasattr(r, "npv_net_benefit_ngn") for r in results)


def test_custom_scenario_discounted_metrics(materials_df: pd.DataFrame):
    result = calculate_custom_scenario(materials_df, {"Sugar": 1200})
    assert isinstance(result.npv_net_benefit_ngn, float)


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
