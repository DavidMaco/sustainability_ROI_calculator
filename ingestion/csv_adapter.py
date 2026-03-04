"""CSV file adapter — default implementation."""

from __future__ import annotations

import json
from ast import literal_eval
from pathlib import Path

import pandas as pd

import config as cfg
from ingestion.base import DataAdapter


class CsvAdapter(DataAdapter):
    """Read/write all artifacts as CSV/JSON in cfg.DATA_DIR."""

    def __init__(self, data_dir: Path | None = None):
        self.data_dir = data_dir or cfg.DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)

    # ── Readers ──────────────────────────────────────────────────────

    def load_materials(self) -> pd.DataFrame:
        return pd.read_csv(self.data_dir / "sustainability_materials_comparison.csv")

    def load_scenarios(self) -> pd.DataFrame:
        df = pd.read_csv(self.data_dir / "company_scenarios.csv")
        # Normalise materials_mix from JSON string → dict
        if "materials_mix" in df.columns:
            def _parse_mix(value: object) -> object:
                if not isinstance(value, str):
                    return value
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    try:
                        parsed = literal_eval(value)
                        return parsed if isinstance(parsed, dict) else value
                    except (ValueError, SyntaxError):
                        return value

            df["materials_mix"] = df["materials_mix"].apply(_parse_mix)
        return df

    def load_results(self) -> pd.DataFrame:
        return pd.read_csv(self.data_dir / "sustainability_roi_analysis.csv")

    def load_summary(self) -> dict:
        with open(self.data_dir / "sustainability_summary.json") as f:
            return json.load(f)

    # ── Writers ──────────────────────────────────────────────────────

    def save_materials(self, df: pd.DataFrame) -> Path:
        path = self.data_dir / "sustainability_materials_comparison.csv"
        df.to_csv(path, index=False)
        return path

    def save_scenarios(self, df: pd.DataFrame) -> Path:
        path = self.data_dir / "company_scenarios.csv"
        out = df.copy()
        # Serialise materials_mix as proper JSON (not Python dict repr)
        if "materials_mix" in out.columns:
            out["materials_mix"] = out["materials_mix"].apply(lambda x: json.dumps(x) if isinstance(x, dict) else x)
        out.to_csv(path, index=False)
        return path

    def save_results(self, df: pd.DataFrame) -> Path:
        path = self.data_dir / "sustainability_roi_analysis.csv"
        df.to_csv(path, index=False)
        return path

    def save_summary(self, data: dict) -> Path:
        path = self.data_dir / "sustainability_summary.json"
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return path

    def save_calculator_template(self, df: pd.DataFrame) -> Path:
        path = self.data_dir / "sustainability_calculator_template.csv"
        df.to_csv(path, index=False)
        return path
