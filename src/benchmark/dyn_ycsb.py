# src/benchmark/dyn_ycsb.py
import asyncio
import logging
from datetime import datetime
from typing import List, Tuple, Dict, Optional
import subprocess
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .metrics import BenchmarkMetrics, MetricsCollector

class DynYCSB:
    def __init__(self, ycsb_home: Optional[str] = None):
        """
        Initialize DynYCSB benchmark manager.
        
        Args:
            ycsb_home: Path to YCSB installation directory. If None, will try to use YCSB_HOME env variable.
        """
        self.ycsb_home = ycsb_home or os.environ.get('YCSB_HOME')
        if not self.ycsb_home:
            raise ValueError("YCSB_HOME not set and not provided")
        
        self.logger = logging.getLogger("limoce.benchmark")
        self.metrics_collector = MetricsCollector()

    def generate_workload_file(self, 
                             workload_type: str,
                             target_throughput: int,
                             operation_count: int,
                             filename: str) -> str:
        """Generate custom workload file."""
        workload_template = {
            'A': {
                'readproportion': '0.5',
                'updateproportion': '0.5',
                'requestdistribution': 'zipfian'
            },
            'B': {
                'readproportion': '0.95',
                'updateproportion': '0.05',
                'requestdistribution': 'zipfian'
            },
            'C': {
                'readproportion': '1.0',
                'requestdistribution': 'zipfian'
            },
            'D': {
                'readproportion': '0.95',
                'insertproportion': '0.05',
                'requestdistribution': 'latest'
            },
            'E': {
                'insertproportion': '0.05',
                'scanproportion': '0.95',
                'requestdistribution': 'zipfian'
            },
            'F': {
                'readproportion': '0.5',
                'readmodifywriteproportion': '0.5',
                'requestdistribution': 'zipfian'
            }
        }
        
        workload_path = os.path.join(self.ycsb_home, 'workloads', filename)
        
        with open(workload_path, 'w') as f:
            f.write(f"# Workload {workload_type} configuration\n")
            f.write("recordcount=1000000\n")
            f.write(f"operationcount={operation_count}\n")
            f.write(f"target={target_throughput}\n")
            
            # Write workload-specific properties
            for key, value in workload_template.get(workload_type, {}).items():
                f.write(f"{key}={value}\n")
                
        return workload_path

    async def execute_workload(self, 
                             database: str,
                             workload_file: str,
                             phase: str = 'run',
                             additional_props: Optional[Dict] = None) -> BenchmarkMetrics:
        """Execute YCSB workload."""
        cmd = [
            os.path.join(self.ycsb_home, 'bin', 'ycsb'),
            phase,
            database,
            '-P', workload_file,
            '-s'  # Add status flag for progress
        ]
        
        # Add additional properties
        if additional_props:
            for key, value in additional_props.items():
                cmd.extend(['-p', f"{key}={value}"])

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"Workload execution failed: {stderr.decode()}")
                raise Exception("Workload execution failed")

            # Parse results
            results = self._parse_ycsb_output(stdout.decode())
            
            return BenchmarkMetrics(
                throughput=results.get('throughput', 0),
                latency_avg=results.get('latency_avg', 0),
                latency_95th=results.get('latency_95th', 0),
                latency_99th=results.get('latency_99th', 0),
                error_count=results.get('error_count', 0)
            )
            
        except Exception as e:
            self.logger.error(f"Error executing workload: {e}")
            raise

    def _parse_ycsb_output(self, output: str) -> Dict:
        """Parse YCSB output to extract metrics."""
        results = {}
        
        for line in output.split('\n'):
            if '[OVERALL]' in line:
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    metric = parts[1].strip()
                    value = float(parts[2].strip())
                    if 'Throughput' in metric:
                        results['throughput'] = value
            elif '[READ]' in line or '[UPDATE]' in line:
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    metric = parts[1].strip()
                    value = float(parts[2].strip())
                    if 'AverageLatency' in metric:
                        results['latency_avg'] = value
                    elif '95thPercentileLatency' in metric:
                        results['latency_95th'] = value
                    elif '99thPercentileLatency' in metric:
                        results['latency_99th'] = value
            
        return results

    async def run_benchmark(self, 
                          database: str,
                          workload_sequence: List[Tuple[str, int, int]],
                          additional_props: Optional[Dict] = None) -> pd.DataFrame:
        """
        Run complete benchmark sequence.
        
        Args:
            database: Target database (e.g., 'mongodb', 'cassandra')
            workload_sequence: List of (workload_type, duration, target_throughput) tuples
            additional_props: Additional YCSB properties
        """
        for idx, (workload_type, duration, target_throughput) in enumerate(workload_sequence):
            self.logger.info(f"Running workload {workload_type} "
                           f"(throughput: {target_throughput}, duration: {duration}s)")
            
            # Generate workload file
            workload_file = self.generate_workload_file(
                workload_type,
                target_throughput,
                int(target_throughput * duration),
                f'workload_{idx}.spec'
            )
            
            # Execute workload
            metrics = await self.execute_workload(
                database,
                workload_file,
                additional_props=additional_props
            )
            
            # Record metrics
            self.metrics_collector.add_metrics(
                timestamp=datetime.now(),
                workload_type=workload_type,
                metrics=metrics
            )
            
            # Wait for next workload
            if idx < len(workload_sequence) - 1:
                await asyncio.sleep(1)
                
        return self.metrics_collector.get_dataframe()

    def plot_results(self, results: pd.DataFrame):
        """Plot benchmark results."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Throughput plot
        sns.lineplot(data=results, x='timestamp', y='throughput', 
                    hue='workload_type', ax=ax1)
        ax1.set_title('Throughput over Time')
        ax1.set_ylabel('Operations/second')
        
        # Latency plots
        metrics = ['latency_avg', 'latency_95th', 'latency_99th']
        for metric in metrics:
            sns.lineplot(data=results, x='timestamp', y=metric, 
                        label=metric, ax=ax2)
        ax2.set_title('Latency over Time')
        ax2.set_ylabel('Latency (μs)')
        
        plt.tight_layout()
        plt.show()

    def save_results(self, results: pd.DataFrame, filename: str):
        """Save benchmark results to file."""
        results.to_csv(filename, index=False)
        self.logger.info(f"Results saved to {filename}")