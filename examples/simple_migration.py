# examples/simple_migration.py
import asyncio
import logging
from limoce import ContainerManager, NetworkManager, MigrationCoordinator, DynYCSB
from limoce.utils import EnvironmentLoader

# Initialize environment
env = EnvironmentLoader()

# Use configurations
docker_config = env.docker_config
network_config = env.network_config
migration_config = env.migration_config

# Initialize components with configurations
container_manager = ContainerManager(
    docker_host=docker_config['host'],
    api_version=docker_config['api_version']
)

network_manager = NetworkManager(
    host=network_config['host'],
    port=network_config['port']
)

async def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Initialize components
    container_mgr = ContainerManager()
    network_mgr = NetworkManager("localhost", 8080)
    migration_coordinator = MigrationCoordinator(container_mgr, network_mgr)

    try:
        # Create test container
        container = container_mgr.create_container(
            image="nginx:latest",
            name="test_container",
            cpu_quota=200000,
            mem_limit="512m"
        )
        logger.info(f"Created container: {container.id}")

        # Perform migration
        migration_id = await migration_coordinator.start_migration(
            source_id="source_host",
            target_id="target_host",
            container_id=container.id
        )
        
        logger.info(f"Migration completed: {migration_id}")

    finally:
        # Cleanup
        container.remove(force=True)
        await network_mgr.close_session("source_host")

if __name__ == "__main__":
    asyncio.run(main())