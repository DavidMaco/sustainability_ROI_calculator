"""SQLite adapter for reading and writing pipeline artifacts."""

from __future__ import annotations

import json
import sqlite3
from ast import literal_eval
from pathlib import Path

import pandas as pd

from ingestion.base import DataAdapter


class SQLiteAdapter(DataAdapter):
    """Persist artifacts in a local SQLite database."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def load_materials(self) -> pd.DataFrame:
        with self._conn() as conn:
            return pd.read_sql_query("SELECT * FROM sustainability_materials_comparison", conn)

    def load_scenarios(self) -> pd.DataFrame:
        with self._conn() as conn:
            df = pd.read_sql_query("SELECT * FROM company_scenarios", conn)

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
        with self._conn() as conn:
            return pd.read_sql_query("SELECT * FROM sustainability_roi_analysis", conn)

    def load_summary(self) -> dict:
        with self._conn() as conn:
            row = conn.execute("SELECT payload_json FROM sustainability_summary LIMIT 1").fetchone()
        if not row:
            raise FileNotFoundError("No sustainability_summary row found in SQLite database")
        return json.loads(str(row[0]))

    def save_materials(self, df: pd.DataFrame) -> Path:
        with self._conn() as conn:
            df.to_sql("sustainability_materials_comparison", conn, if_exists="replace", index=False)
        return self.db_path

    def save_scenarios(self, df: pd.DataFrame) -> Path:
        out = df.copy()
        if "materials_mix" in out.columns:
            out["materials_mix"] = out["materials_mix"].apply(lambda x: json.dumps(x) if isinstance(x, dict) else x)
        with self._conn() as conn:
            out.to_sql("company_scenarios", conn, if_exists="replace", index=False)
        return self.db_path

    def save_results(self, df: pd.DataFrame) -> Path:
        with self._conn() as conn:
            df.to_sql("sustainability_roi_analysis", conn, if_exists="replace", index=False)
        return self.db_path

    def save_summary(self, data: dict) -> Path:
        payload = json.dumps(data)
        with self._conn() as conn:
            conn.execute("DROP TABLE IF EXISTS sustainability_summary")
            conn.execute("CREATE TABLE sustainability_summary (payload_json TEXT NOT NULL)")
            conn.execute("INSERT INTO sustainability_summary(payload_json) VALUES (?)", (payload,))
            conn.commit()
        return self.db_path

    def save_calculator_template(self, df: pd.DataFrame) -> Path:
        with self._conn() as conn:
            df.to_sql("sustainability_calculator_template", conn, if_exists="replace", index=False)
        return self.db_path
