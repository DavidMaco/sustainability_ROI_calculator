"""Simple concurrent load probe for app health and basic latency tracking."""

from __future__ import annotations

import json
import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

TARGET_URL = os.getenv("SUST_LOAD_TARGET_URL", "http://127.0.0.1:8501/_stcore/health")
REQUESTS = int(os.getenv("SUST_LOAD_REQUESTS", "250"))
CONCURRENCY = int(os.getenv("SUST_LOAD_CONCURRENCY", "25"))
MAX_FAILURE_RATE_PCT = float(os.getenv("SUST_LOAD_MAX_FAILURE_RATE_PCT", "0"))
MAX_P95_LATENCY_MS = float(os.getenv("SUST_LOAD_MAX_P95_MS", "900"))
MAX_P99_LATENCY_MS = float(os.getenv("SUST_LOAD_MAX_P99_MS", "1500"))
METRICS_PATH = Path(os.getenv("SUST_LOAD_METRICS_PATH", "data/load_test_metrics.json"))
HISTORY_PATH = Path(os.getenv("SUST_LOAD_HISTORY_PATH", "data/load_test_history.jsonl"))


def hit_once() -> float:
    start = time.perf_counter()
    with urlopen(TARGET_URL, timeout=5) as resp:  # nosec B310
        if resp.status != 200:
            raise RuntimeError(f"Unexpected status: {resp.status}")
        _ = resp.read()
    return (time.perf_counter() - start) * 1000


def main() -> int:
    latencies: list[float] = []
    failures = 0

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        futures = [pool.submit(hit_once) for _ in range(REQUESTS)]
        for future in as_completed(futures):
            try:
                latencies.append(future.result())
            except Exception:
                failures += 1

    if not latencies:
        print("No successful requests.")
        return 1

    p50 = statistics.median(latencies)
    p95 = sorted(latencies)[int(0.95 * (len(latencies) - 1))]
    p99 = sorted(latencies)[int(0.99 * (len(latencies) - 1))]
    avg = statistics.mean(latencies)
    failure_rate = (failures / REQUESTS) * 100 if REQUESTS else 100.0

    metrics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target_url": TARGET_URL,
        "requests": REQUESTS,
        "concurrency": CONCURRENCY,
        "success": len(latencies),
        "failures": failures,
        "failure_rate_pct": failure_rate,
        "avg_latency_ms": avg,
        "p50_latency_ms": p50,
        "p95_latency_ms": p95,
        "p99_latency_ms": p99,
        "max_failure_rate_pct": MAX_FAILURE_RATE_PCT,
        "max_p95_latency_ms": MAX_P95_LATENCY_MS,
        "max_p99_latency_ms": MAX_P99_LATENCY_MS,
    }

    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(metrics) + "\n")

    print(f"Requests: {REQUESTS}")
    print(f"Concurrency: {CONCURRENCY}")
    print(f"Success: {len(latencies)}")
    print(f"Failures: {failures}")
    print(f"Failure rate: {failure_rate:.2f}%")
    print(f"Avg latency: {avg:.2f} ms")
    print(f"P50 latency: {p50:.2f} ms")
    print(f"P95 latency: {p95:.2f} ms")
    print(f"P99 latency: {p99:.2f} ms")

    if failure_rate > MAX_FAILURE_RATE_PCT:
        print(f"FAIL: failure rate {failure_rate:.2f}% exceeds threshold " f"{MAX_FAILURE_RATE_PCT:.2f}%")
        return 1
    if p95 > MAX_P95_LATENCY_MS:
        print(f"FAIL: p95 latency {p95:.2f} ms exceeds threshold " f"{MAX_P95_LATENCY_MS:.2f} ms")
        return 1
    if p99 > MAX_P99_LATENCY_MS:
        print(f"FAIL: p99 latency {p99:.2f} ms exceeds threshold " f"{MAX_P99_LATENCY_MS:.2f} ms")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
