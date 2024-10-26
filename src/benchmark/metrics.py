# src/benchmark/metrics.py
from dataclasses import dataclass
from typing import Dict, List
import pandas as pd

@dataclass
class BenchmarkMetrics:
    throughput: float
    latency_avg: float
    latency_95th: float
    latency_99th: float
    error_count: int

class MetricsCollector:
    def __init__(self):
        self.metrics: List[Dict] = []

    def add_metrics(self, 
                   timestamp, 
                   workload_type: str, 
                   metrics: BenchmarkMetrics):
        """Add metrics to collection."""
        self.metrics.append({
            'timestamp': timestamp,
            'workload_type': workload_type,
            'throughput': metrics.throughput,
            'latency_avg': metrics.latency_avg,
            'latency_95th': metrics.latency_95th,
            'latency_99th': metrics.latency_99th,
            'error_count': metrics.error_count
        })

    def get_dataframe(self) -> pd.DataFrame:
        """Convert metrics to pandas DataFrame."""
        return pd.DataFrame(self.metrics)