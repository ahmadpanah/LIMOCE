# src/__init__.py
from .container_manager import ContainerManager
from .network_manager import NetworkManager
from .migration_coordinator import MigrationCoordinator
from .benchmark import DynYCSB, BenchmarkMetrics, MetricsCollector
from .utils import setup_logging

__version__ = '0.1.0'

__all__ = [
    'ContainerManager',
    'NetworkManager',
    'MigrationCoordinator',
    'DynYCSB',
    'BenchmarkMetrics',
    'MetricsCollector',
    'setup_logging'
]

# Configure default logging
setup_logging()