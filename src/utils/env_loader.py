# src/utils/env_loader.py
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict

class EnvironmentLoader:
    def __init__(self, env_file: str = None):
        """
        Initialize environment loader
        
        Args:
            env_file: Path to .env file. If None, will look in default locations
        """
        self.env_file = env_file or self._find_env_file()
        self._load_env()

    def _find_env_file(self) -> str:
        """Find .env file in various locations."""
        possible_locations = [
            Path.cwd() / '.env',
            Path.cwd().parent / '.env',
            Path.home() / '.limoce' / '.env',
            Path('/etc/limoce/.env')
        ]
        
        for location in possible_locations:
            if location.is_file():
                return str(location)
        
        raise FileNotFoundError("No .env file found")

    def _load_env(self):
        """Load environment variables from .env file."""
        load_dotenv(self.env_file)

    @property
    def docker_config(self) -> Dict:
        """Get Docker configuration."""
        return {
            'host': os.getenv('DOCKER_HOST', 'unix://var/run/docker.sock'),
            'api_version': os.getenv('DOCKER_API_VERSION', '1.41'),
            'tls_verify': bool(int(os.getenv('DOCKER_TLS_VERIFY', '0')))
        }

    @property
    def network_config(self) -> Dict:
        """Get network configuration."""
        return {
            'host': os.getenv('LIMOCE_HOST', 'localhost'),
            'port': int(os.getenv('LIMOCE_PORT', '8080')),
            'api_version': os.getenv('LIMOCE_API_VERSION', 'v1')
        }

    @property
    def database_config(self) -> Dict:
        """Get database configuration."""
        return {
            'mongodb_uri': os.getenv('MONGODB_URI', 'mongodb://localhost:27017'),
            'mongodb_database': os.getenv('MONGODB_DATABASE', 'ycsb'),
            'cassandra_hosts': os.getenv('CASSANDRA_HOSTS', 'localhost'),
            'cassandra_port': int(os.getenv('CASSANDRA_PORT', '9042'))
        }

    @property
    def resource_limits(self) -> Dict:
        """Get resource limit configuration."""
        return {
            'cpu_quota': int(os.getenv('DEFAULT_CONTAINER_CPU_QUOTA', '100000')),
            'memory_limit': os.getenv('DEFAULT_CONTAINER_MEMORY_LIMIT', '512m'),
            'network_mode': os.getenv('DEFAULT_CONTAINER_NETWORK_MODE', 'bridge')
        }

    @property
    def migration_config(self) -> Dict:
        """Get migration configuration."""
        return {
            'checkpoint_dir': os.getenv('CHECKPOINT_BASE_DIR', '/tmp/checkpoints'),
            'timeout': int(os.getenv('MIGRATION_TIMEOUT', '300')),
            'heartbeat_interval': int(os.getenv('HEARTBEAT_INTERVAL', '5')),
            'max_retries': int(os.getenv('MAX_RETRY_ATTEMPTS', '3'))
        }

    @property
    def metrics_config(self) -> Dict:
        """Get metrics configuration."""
        return {
            'prometheus_port': int(os.getenv('PROMETHEUS_PORT', '9090')),
            'enabled': bool(int(os.getenv('ENABLE_METRICS', '1'))),
            'interval': int(os.getenv('METRICS_INTERVAL', '15'))
        }

    @property
    def logging_config(self) -> Dict:
        """Get logging configuration."""
        return {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'file': os.getenv('LOG_FILE', '/var/log/limoce/limoce.log'),
            'debug': bool(int(os.getenv('ENABLE_DEBUG', '0')))
        }

    @property
    def security_config(self) -> Dict:
        """Get security configuration."""
        return {
            'ssl_cert': os.getenv('SSL_CERT_PATH', '/etc/limoce/ssl/cert.pem'),
            'ssl_key': os.getenv('SSL_KEY_PATH', '/etc/limoce/ssl/key.pem'),
            'enable_ssl': bool(int(os.getenv('ENABLE_SSL', '0')))
        }

    @property
    def benchmark_config(self) -> Dict:
        """Get benchmark configuration."""
        return {
            'results_dir': os.getenv('BENCHMARK_RESULTS_DIR', '/var/lib/limoce/results'),
            'enable_visualization': bool(int(os.getenv('ENABLE_VISUALIZATION', '1'))),
            'plot_format': os.getenv('PLOT_FORMAT', 'png'),
            'ycsb_home': os.getenv('YCSB_HOME', '/opt/ycsb'),
            'ycsb_version': os.getenv('YCSB_VERSION', '0.17.0')
        }