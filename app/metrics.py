import time
from contextlib import contextmanager

from prometheus_client import Histogram, Counter, generate_latest

# Per-stage latency as a histogram — so we watch p50/p95/p99, not just averages.
STAGE_LATENCY = Histogram(
    "trip_stage_latency_seconds",
    "Latency of each platform stage",
    labelnames=["stage"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10],
)
LLM_CALLS = Counter("llm_calls_total", "LLM generation attempts", ["outcome"])


@contextmanager
def time_stage(stage: str):
    """Time a block and record it under the stage label."""
    started = time.monotonic()
    try:
        yield
    finally:
        STAGE_LATENCY.labels(stage=stage).observe(time.monotonic() - started)


def record_call(latency_s: float, ok: bool) -> None:
    LLM_CALLS.labels(outcome="ok" if ok else "error").inc()
    STAGE_LATENCY.labels(stage="llm").observe(latency_s)


def metrics_text() -> bytes:
    """Prometheus scrapes this; Grafana charts it."""
    return generate_latest()
