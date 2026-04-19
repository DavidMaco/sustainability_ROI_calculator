"""HTTP API adapter for read-only external data connectors."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import urlopen

import pandas as pd

from ingestion.base import DataAdapter


class ExternalApiAdapter(DataAdapter):
    """Load artifacts from external HTTP endpoints.

    Expected endpoint contract (JSON):
      GET {base}/materials  -> list[dict]
      GET {base}/scenarios  -> list[dict]
      GET {base}/results    -> list[dict]
      GET {base}/summary    -> dict

    This adapter is intentionally read-only. Save methods raise NotImplementedError.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/") + "/"

    def _get_json(self, path: str) -> object:
        url = urljoin(self.base_url, path)
        with urlopen(url, timeout=10) as response:  # nosec B310
            payload = response.read().decode("utf-8")
        return json.loads(payload)

    def _get_frame(self, path: str) -> pd.DataFrame:
        payload = self._get_json(path)
        if not isinstance(payload, list):
            raise TypeError(f"Expected list payload from {path!r}, got {type(payload).__name__}")
        return pd.DataFrame(payload)

    def load_materials(self) -> pd.DataFrame:
        return self._get_frame("materials")

    def load_scenarios(self) -> pd.DataFrame:
        return self._get_frame("scenarios")

    def load_results(self) -> pd.DataFrame:
        return self._get_frame("results")

    def load_summary(self) -> dict:
        payload = self._get_json("summary")
        if not isinstance(payload, dict):
            raise TypeError(f"Expected dict payload from 'summary', got {type(payload).__name__}")
        return payload

    def save_materials(self, df: pd.DataFrame) -> Path:
        raise NotImplementedError("ExternalApiAdapter is read-only")

    def save_scenarios(self, df: pd.DataFrame) -> Path:
        raise NotImplementedError("ExternalApiAdapter is read-only")

    def save_results(self, df: pd.DataFrame) -> Path:
        raise NotImplementedError("ExternalApiAdapter is read-only")

    def save_summary(self, data: dict) -> Path:
        raise NotImplementedError("ExternalApiAdapter is read-only")

    def save_calculator_template(self, df: pd.DataFrame) -> Path:
        raise NotImplementedError("ExternalApiAdapter is read-only")
