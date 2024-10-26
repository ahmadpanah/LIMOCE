# src/container_manager.py
import docker
import logging
import json
import time
from typing import Dict, Optional, List
import subprocess
from prometheus_client import Gauge, Counter

class ContainerManager:
    def __init__(self, docker_host: str = "unix://var/run/docker.sock"):
        self.client = docker.DockerClient(base_url=docker_host)
        self.logger = logging.getLogger("limoce.container")
        
        # Prometheus metrics
        self.container_cpu_usage = Gauge('container_cpu_percent', 
                                       'Container CPU usage percentage')
        self.container_memory_usage = Gauge('container_memory_usage_bytes', 
                                          'Container memory usage in bytes')
        self.migration_duration = Gauge('container_migration_duration_seconds', 
                                      'Container migration duration')
        self.migration_counter = Counter('container_migrations_total', 
                                       'Total number of container migrations')

    def create_container(self, 
                        image: str, 
                        name: str, 
                        **kwargs) -> docker.models.containers.Container:
        """Create a new container with specified configuration."""
        try:
            container = self.client.containers.run(
                image,
                name=name,
                detach=True,
                cpu_quota=kwargs.get('cpu_quota', 100000),
                mem_limit=kwargs.get('mem_limit', '512m'),
                network_mode=kwargs.get('network_mode', 'bridge'),
                environment=kwargs.get('environment', {}),
                volumes=kwargs.get('volumes', {})
            )
            self.logger.info(f"Container {name} created successfully")
            return container
        except docker.errors.APIError as e:
            self.logger.error(f"Failed to create container: {e}")
            raise

    def get_container_stats(self, container_id: str) -> Dict:
        """Get container resource usage statistics."""
        try:
            container = self.client.containers.get(container_id)
            stats = container.stats(stream=False)
            
            # Calculate CPU percentage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0
            
            # Calculate memory usage
            memory_usage = stats['memory_stats']['usage']
            memory_limit = stats['memory_stats']['limit']
            memory_percent = (memory_usage / memory_limit) * 100.0
            
            # Update Prometheus metrics
            self.container_cpu_usage.set(cpu_percent)
            self.container_memory_usage.set(memory_usage)
            
            return {
                'cpu_percent': cpu_percent,
                'memory_usage': memory_usage,
                'memory_percent': memory_percent,
                'network_rx_bytes': stats['networks']['eth0']['rx_bytes'],
                'network_tx_bytes': stats['networks']['eth0']['tx_bytes']
            }
        except Exception as e:
            self.logger.error(f"Failed to get container stats: {e}")
            return {}

    def checkpoint_container(self, 
                           container_id: str, 
                           checkpoint_dir: str) -> bool:
        """Create a checkpoint of the running container."""
        try:
            container = self.client.containers.get(container_id)
            
            # Ensure checkpoint directory exists
            checkpoint_cmd = (
                f"docker checkpoint create --checkpoint-dir={checkpoint_dir} "
                f"{container_id} checkpoint_{int(time.time())}"
            )
            result = subprocess.run(
                checkpoint_cmd.split(), 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info(f"Container {container_id} checkpointed successfully")
                return True
            else:
                self.logger.error(f"Checkpoint failed: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Checkpoint error: {e}")
            return False

    def restore_container(self, 
                         container_id: str, 
                         checkpoint_dir: str) -> bool:
        """Restore a container from checkpoint."""
        try:
            restore_cmd = (
                f"docker start --checkpoint-dir={checkpoint_dir} "
                f"--checkpoint=checkpoint_{container_id} {container_id}"
            )
            result = subprocess.run(
                restore_cmd.split(), 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info(f"Container {container_id} restored successfully")
                return True
            else:
                self.logger.error(f"Restore failed: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Restore error: {e}")
            return False