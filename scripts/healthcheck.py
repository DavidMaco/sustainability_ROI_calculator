"""Container health check for app and artifact readiness."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config as cfg

REQUIRED_ARTIFACTS = [
    "sustainability_materials_comparison.csv",
    "company_scenarios.csv",
    "sustainability_roi_analysis.csv",
    "sustainability_summary.json",
    "sustainability_calculator_template.csv",
]


def check_artifacts(data_dir: Path) -> tuple[bool, list[str]]:
    missing = [name for name in REQUIRED_ARTIFACTS if not (data_dir / name).exists()]
    return (len(missing) == 0, missing)


def check_http(url: str) -> bool:
    try:
        with urlopen(url, timeout=3) as resp:  # nosec B310
            return 200 <= resp.status < 300
    except (URLError, TimeoutError):
        return False


def main() -> int:
    data_ok, missing = check_artifacts(cfg.DATA_DIR)
    health_url = os.getenv("SUST_HEALTHCHECK_URL", "http://127.0.0.1:8501/_stcore/health")
    http_ok = check_http(health_url)

    payload = {
        "data_ok": data_ok,
        "http_ok": http_ok,
        "missing_artifacts": missing,
        "data_dir": str(cfg.DATA_DIR),
    }
    print(json.dumps(payload))

    if data_ok and http_ok:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
