"""
Sustainability ROI Calculator — Configuration Module

Priority: env vars → defaults.
All economic assumptions and paths are centralised here.
"""

import logging
import os
from pathlib import Path


def _is_truthy(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# ─── Runtime ─────────────────────────────────────────────────────────
ENV = os.getenv("SUST_ENV", "development").lower()  # development | staging | production
LOG_LEVEL = os.getenv("SUST_LOG_LEVEL", "INFO").upper()
LOG_JSON = _is_truthy(os.getenv("SUST_LOG_JSON"), default=False)

if LOG_JSON:
    format_str = '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
else:
    format_str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=format_str,
)
logger = logging.getLogger("sustainability_roi")

# ─── Paths ───────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / os.getenv("SUST_DATA_DIR", "data")
DATA_DIR.mkdir(exist_ok=True)

# ─── Economic Assumptions (overridable via env) ──────────────────────
CARBON_TAX_NGN_PER_TON = float(os.getenv("SUST_CARBON_TAX", "50000"))  # ₦50,000/ton
WATER_COST_NGN_PER_1000L = float(os.getenv("SUST_WATER_COST", "150"))  # ₦150/1000L
WASTE_COST_NGN_PER_TON = float(os.getenv("SUST_WASTE_COST", "80000"))  # ₦80,000/ton
CURRENCY_SYMBOL = os.getenv("SUST_CURRENCY", "₦")

# ─── Reproducibility ────────────────────────────────────────────────
RANDOM_SEED = int(os.getenv("SUST_RANDOM_SEED", "42"))

# ─── Security / Session ────────────────────────────────────────────
AUTH_ENABLED = _is_truthy(os.getenv("SUST_AUTH_ENABLED"), default=(ENV == "production"))
SESSION_TIMEOUT_MINUTES = int(os.getenv("SUST_SESSION_TIMEOUT_MINUTES", "30"))

# ─── Artifact Backup / Versioning ──────────────────────────────────
ENABLE_ARTIFACT_BACKUP = _is_truthy(os.getenv("SUST_ENABLE_ARTIFACT_BACKUP"), default=True)
ARTIFACT_BACKUP_RETENTION = int(os.getenv("SUST_ARTIFACT_BACKUP_RETENTION", "20"))

# ─── Observability Endpoint ─────────────────────────────────────────
METRICS_HOST = os.getenv("SUST_METRICS_HOST", "0.0.0.0")
METRICS_PORT = int(os.getenv("SUST_METRICS_PORT", "9108"))


def is_production() -> bool:
    return ENV == "production"


def validate_runtime_settings() -> None:
    """Guard for production deployments."""
    if not is_production():
        return
    assert CARBON_TAX_NGN_PER_TON > 0, "Carbon tax must be positive in production"
    assert WATER_COST_NGN_PER_1000L > 0, "Water cost must be positive in production"
    assert WASTE_COST_NGN_PER_TON > 0, "Waste cost must be positive in production"
    assert SESSION_TIMEOUT_MINUTES > 0, "Session timeout must be positive in production"
    assert ARTIFACT_BACKUP_RETENTION > 0, "Backup retention must be positive in production"
    assert METRICS_PORT > 0, "Metrics port must be positive in production"
    logger.info("Runtime settings validated for production")
