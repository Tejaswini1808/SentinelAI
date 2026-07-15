"""In-memory AI/ops metrics registry for the MVP (no external TSDB required)."""
import threading
import time
from collections import defaultdict
from contextlib import contextmanager


class MetricsRegistry:
    def __init__(self):
        self._lock = threading.Lock()
        self._timings_ms = defaultdict(list)
        self._counters = defaultdict(int)
        self._token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    @contextmanager
    def time_block(self, name: str):
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            with self._lock:
                self._timings_ms[name].append(elapsed_ms)

    def incr(self, name: str, amount: int = 1):
        with self._lock:
            self._counters[name] += amount

    def add_token_usage(self, usage: dict | None):
        if not usage:
            return
        with self._lock:
            for key in self._token_usage:
                self._token_usage[key] += usage.get(key, 0) or 0

    def snapshot(self) -> dict:
        with self._lock:
            timing_stats = {}
            for name, samples in self._timings_ms.items():
                if not samples:
                    continue
                timing_stats[name] = {
                    "count": len(samples),
                    "avg_ms": round(sum(samples) / len(samples), 2),
                    "p95_ms": round(sorted(samples)[int(len(samples) * 0.95) - 1], 2) if len(samples) >= 1 else None,
                    "last_ms": round(samples[-1], 2),
                }
            return {
                "timings": timing_stats,
                "counters": dict(self._counters),
                "token_usage": dict(self._token_usage),
            }


metrics = MetricsRegistry()
