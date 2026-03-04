"""Integration tests — full pipeline end-to-end."""

import json
import shutil
import tempfile
from pathlib import Path

import pandas as pd
import pytest

import config as cfg
from ingestion.csv_adapter import CsvAdapter
from pipeline.runner import run_pipeline


@pytest.fixture()
def tmp_data_dir(monkeypatch) -> Path:
    """Create a temp directory and monkeypatch cfg.DATA_DIR so it resets after the test."""
    d = Path(tempfile.mkdtemp(prefix="sroi_test_")) / "data"
    d.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(cfg, "DATA_DIR", d)
    yield d
    shutil.rmtree(d.parent, ignore_errors=True)


def test_pipeline_produces_all_artifacts(tmp_data_dir: Path):
    """Full pipeline must create every expected file."""
    adapter = CsvAdapter(data_dir=tmp_data_dir)
    run_pipeline(adapter)

    expected_files = [
        "sustainability_materials_comparison.csv",
        "company_scenarios.csv",
        "sustainability_roi_analysis.csv",
        "sustainability_summary.json",
        "sustainability_calculator_template.csv",
    ]
    for fname in expected_files:
        assert (tmp_data_dir / fname).exists(), f"Missing: {fname}"


def test_pipeline_results_deterministic(tmp_data_dir: Path):
    """Two runs with same seed should produce identical results."""
    adapter = CsvAdapter(data_dir=tmp_data_dir)

    run_pipeline(adapter)
    r1 = pd.read_csv(tmp_data_dir / "sustainability_roi_analysis.csv")

    run_pipeline(adapter)
    r2 = pd.read_csv(tmp_data_dir / "sustainability_roi_analysis.csv")

    pd.testing.assert_frame_equal(r1, r2)


def test_summary_json_valid(tmp_data_dir: Path):
    """Summary JSON must be valid and contain expected keys."""
    adapter = CsvAdapter(data_dir=tmp_data_dir)
    run_pipeline(adapter)

    with open(tmp_data_dir / "sustainability_summary.json") as f:
        data = json.load(f)

    for key in ["total_cost_increase", "total_carbon_reduction_tons", "total_net_benefit", "avg_roi_pct"]:
        assert key in data, f"Missing key: {key}"


def test_scenarios_csv_has_json_materials_mix(tmp_data_dir: Path):
    """materials_mix in CSV must be valid JSON, not Python dict repr."""
    adapter = CsvAdapter(data_dir=tmp_data_dir)
    run_pipeline(adapter)

    df = pd.read_csv(tmp_data_dir / "company_scenarios.csv")
    for raw in df["materials_mix"]:
        parsed = json.loads(raw)  # Must not raise
        assert isinstance(parsed, dict)
