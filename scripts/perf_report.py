"""Generate CI-friendly performance trend summary from load-test metrics."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


def _read_metrics(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _format_markdown(metrics: dict) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return "\n".join(
        [
            "## Load Test Performance",
            "",
            f"Generated: {ts}",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| Requests | {metrics['requests']} |",
            f"| Concurrency | {metrics['concurrency']} |",
            f"| Success | {metrics['success']} |",
            f"| Failures | {metrics['failures']} |",
            f"| Failure Rate | {metrics['failure_rate_pct']:.2f}% |",
            f"| Average Latency | {metrics['avg_latency_ms']:.2f} ms |",
            f"| P50 Latency | {metrics['p50_latency_ms']:.2f} ms |",
            f"| P95 Latency | {metrics['p95_latency_ms']:.2f} ms |",
            f"| P99 Latency | {metrics['p99_latency_ms']:.2f} ms |",
        ]
    )


def main() -> int:
    metrics_path = Path(os.getenv("SUST_LOAD_METRICS_PATH", "data/load_test_metrics.json"))
    if not metrics_path.exists():
        raise FileNotFoundError(f"Load-test metrics file not found: {metrics_path}")

    metrics = _read_metrics(metrics_path)
    report = _format_markdown(metrics)
    print(report)

    summary_path = os.getenv("GITHUB_STEP_SUMMARY", "").strip()
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(report + "\n")

    trend_path = Path("data/load_test_trend.md")
    trend_path.write_text(report + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
