"""Abstract ingestion interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd


class DataAdapter(ABC):
    """Contract for all data source adapters."""

    @abstractmethod
    def load_materials(self) -> pd.DataFrame: ...

    @abstractmethod
    def load_scenarios(self) -> pd.DataFrame: ...

    @abstractmethod
    def load_results(self) -> pd.DataFrame: ...

    @abstractmethod
    def load_summary(self) -> dict: ...

    @abstractmethod
    def save_materials(self, df: pd.DataFrame) -> Path: ...

    @abstractmethod
    def save_scenarios(self, df: pd.DataFrame) -> Path: ...

    @abstractmethod
    def save_results(self, df: pd.DataFrame) -> Path: ...

    @abstractmethod
    def save_summary(self, data: dict) -> Path: ...

    @abstractmethod
    def save_calculator_template(self, df: pd.DataFrame) -> Path: ...
