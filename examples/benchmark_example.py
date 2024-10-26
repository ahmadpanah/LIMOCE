from limoce import ContainerManager, NetworkManager, MigrationCoordinator, DynYCSB

import asyncio
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
    benchmark = DynYCSB(mongodb_uri="mongodb://localhost:27017")
    
    # Define workload sequence
    workload_sequence = [
        ('A', 60, 1000),  # workload type, duration, target throughput
        ('B', 60, 800),
        ('C', 60, 1200)
    ]
    
    # Run benchmark
    results = await benchmark.run_benchmark(workload_sequence)
    
    # Plot results
    benchmark.plot_results(results)

if __name__ == "__main__":
    asyncio.run(main())