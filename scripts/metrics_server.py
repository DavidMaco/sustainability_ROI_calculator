"""Lightweight observability endpoint for health and Prometheus-style metrics."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import config as cfg
from scripts.healthcheck import check_artifacts

REQUIRED_FILES = [
    "sustainability_materials_comparison.csv",
    "company_scenarios.csv",
    "sustainability_roi_analysis.csv",
    "sustainability_summary.json",
    "sustainability_calculator_template.csv",
]


def _count_backups(data_dir: Path) -> int:
    return len(list((data_dir / "backups").glob("artifacts_*.zip")))


def _summary_fields(data_dir: Path) -> dict[str, float]:
    summary_path = data_dir / "sustainability_summary.json"
    if not summary_path.exists():
        return {}
    try:
        data = json.loads(summary_path.read_text(encoding="utf-8"))
        return {
            "total_cost_increase": float(data.get("total_cost_increase", 0.0)),
            "total_carbon_reduction_tons": float(data.get("total_carbon_reduction_tons", 0.0)),
            "total_net_benefit": float(data.get("total_net_benefit", 0.0)),
            "avg_roi_pct": float(data.get("avg_roi_pct", 0.0)),
        }
    except (ValueError, json.JSONDecodeError):
        return {}


def _metrics_payload() -> str:
    data_ok, missing = check_artifacts(cfg.DATA_DIR)
    summary = _summary_fields(cfg.DATA_DIR)
    backups = _count_backups(cfg.DATA_DIR)

    lines = [
        "# HELP sroi_data_ready Data artifacts are present (1=yes, 0=no)",
        "# TYPE sroi_data_ready gauge",
        f"sroi_data_ready {1 if data_ok else 0}",
        "# HELP sroi_missing_artifacts Number of missing required artifacts",
        "# TYPE sroi_missing_artifacts gauge",
        f"sroi_missing_artifacts {len(missing)}",
        "# HELP sroi_backup_archives Number of backup archives in data/backups",
        "# TYPE sroi_backup_archives gauge",
        f"sroi_backup_archives {backups}",
    ]

    for key, value in summary.items():
        metric = f"sroi_{key}"
        lines.extend(
            [
                f"# HELP {metric} Exported summary metric: {key}",
                f"# TYPE {metric} gauge",
                f"{metric} {value}",
            ]
        )

    return "\n".join(lines) + "\n"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path in {"/", "/healthz"}:
            data_ok, missing = check_artifacts(cfg.DATA_DIR)
            payload = {
                "status": "ok" if data_ok else "degraded",
                "data_ok": data_ok,
                "missing_artifacts": missing,
                "timestamp_utc": datetime.now(UTC).isoformat(),
            }
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200 if data_ok else 503)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == "/metrics":
            body = _metrics_payload().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        cfg.logger.info('metrics_server %s - "%s"', self.address_string(), format % args)


def main() -> int:
    host = cfg.METRICS_HOST
    port = cfg.METRICS_PORT
    server = ThreadingHTTPServer((host, port), Handler)
    cfg.logger.info("Metrics server started at http://%s:%s", host, port)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
