"""Adapter factory for selecting storage/connectors at runtime."""

from __future__ import annotations

import config as cfg
from ingestion.base import DataAdapter
from ingestion.csv_adapter import CsvAdapter
from ingestion.external_api_adapter import ExternalApiAdapter
from ingestion.sqlite_adapter import SQLiteAdapter


def get_data_adapter(*, require_writable: bool = False) -> DataAdapter:
    """Return the configured data adapter.

    Supported backends via ``SUST_DATA_BACKEND``:
      - ``csv`` (default)
      - ``sqlite``
      - ``api`` (read-only)
    """
    backend = cfg.DATA_BACKEND.strip().lower()

    if backend == "csv":
        return CsvAdapter(data_dir=cfg.DATA_DIR)
    if backend == "sqlite":
        return SQLiteAdapter(db_path=cfg.SQLITE_DB_PATH)
    if backend == "api":
        if require_writable:
            raise RuntimeError("SUST_DATA_BACKEND=api is read-only and cannot be used for pipeline writes")
        return ExternalApiAdapter(base_url=cfg.EXTERNAL_API_BASE_URL)

    raise ValueError(f"Unknown SUST_DATA_BACKEND={cfg.DATA_BACKEND!r}. Use csv, sqlite, or api.")
