"""Simple concurrent load probe for app health and basic latency tracking."""

from __future__ import annotations

import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen

TARGET_URL = "http://127.0.0.1:8501/_stcore/health"
REQUESTS = 200
CONCURRENCY = 20


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
    avg = statistics.mean(latencies)

    print(f"Requests: {REQUESTS}")
    print(f"Concurrency: {CONCURRENCY}")
    print(f"Success: {len(latencies)}")
    print(f"Failures: {failures}")
    print(f"Avg latency: {avg:.2f} ms")
    print(f"P50 latency: {p50:.2f} ms")
    print(f"P95 latency: {p95:.2f} ms")

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
