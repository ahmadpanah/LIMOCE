# LIMOCE: Live Migration of Containers in Edge Computing

LIMOCE is a lightweight framework for performing seamless live migration of containers in resource-constrained edge computing environments. It provides robust container migration capabilities while maintaining minimal downtime and resource usage.

Based on: [Original Paper](https://link.springer.com/article/10.1007/s42979-023-01871-5)

## Features

- Lightweight container migration for edge devices
- Real-time resource monitoring and metrics collection
- Integration with YCSB for performance benchmarking
- Support for different migration strategies
- Automated failure detection and recovery
- Prometheus metrics integration

## Requirements

- Python 3.8+
- Docker 20.10+
- CRIU 3.14+
- YCSB 0.17.0+

## Installation

```bash
# Clone the repository
git clone https://github.com/ahmadpanah/limoce.git
cd limoce

# Install requirements
pip install -r requirements.txt

# Install LIMOCE
pip install .
