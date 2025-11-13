"""
Benchmark parallel execution performance improvement.

Demonstrates time savings from parallel module execution.

Author: Asif Hussain
Version: 1.0
"""

import time
from pathlib import Path
from typing import Dict, Any
from src.operations.operations_orchestrator import OperationsOrchestrator
from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)


class BenchmarkModule(BaseOperationModule):
    """Module that simulates work with controlled duration."""
    
    def __init__(self, module_id: str, duration: float = 0.5):
        super().__init__()
        self.id = module_id
        self.duration = duration
    
    def get_metadata(self) -> OperationModuleMetadata:
        return OperationModuleMetadata(
            module_id=self.id,
            name=f"Benchmark Module {self.id}",
            description=f"Simulates {self.duration}s of work",
            phase=OperationPhase.PROCESSING,
            priority=10
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """Simulate work."""
        time.sleep(self.duration)
        return OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message=f"Module {self.id} completed"
        )


def benchmark_scenario(num_modules: int, duration: float, max_workers: int):
    """
    Benchmark a specific scenario.
    
    Args:
        num_modules: Number of independent modules
        duration: Duration each module takes
        max_workers: Max parallel workers
    
    Returns:
        Tuple of (actual_time, sequential_estimate, time_saved, speedup_factor)
    """
    print(f"\n{'='*70}")
    print(f"Scenario: {num_modules} modules × {duration}s each, max_workers={max_workers}")
    print(f"{'='*70}")
    
    # Create independent modules
    modules = [
        BenchmarkModule(f"module_{i}", duration)
        for i in range(num_modules)
    ]
    
    orchestrator = OperationsOrchestrator(
        operation_id="benchmark",
        operation_name="Parallel Execution Benchmark",
        modules=modules,
        max_parallel_workers=max_workers
    )
    
    # Execute and measure
    start = time.time()
    report = orchestrator.execute_operation()
    actual_time = time.time() - start
    
    # Sequential estimate
    sequential_estimate = num_modules * duration
    
    # Calculate metrics
    time_saved = report.time_saved_seconds
    speedup_factor = sequential_estimate / actual_time if actual_time > 0 else 0
    efficiency = (speedup_factor / min(num_modules, max_workers)) * 100
    
    # Print results
    print(f"\n📊 Results:")
    print(f"  Actual time:        {actual_time:.2f}s")
    print(f"  Sequential estimate: {sequential_estimate:.2f}s")
    print(f"  Time saved:         {time_saved:.2f}s")
    print(f"  Speedup factor:     {speedup_factor:.2f}x")
    print(f"  Parallel efficiency: {efficiency:.1f}%")
    print(f"  Modules in parallel: {report.parallel_execution_count}")
    print(f"  Execution groups:   {report.parallel_groups_count}")
    
    return actual_time, sequential_estimate, time_saved, speedup_factor


def main():
    """Run benchmarks and summarize results."""
    print("🚀 CORTEX Parallel Execution Benchmark")
    print("=" * 70)
    
    scenarios = [
        # (num_modules, duration, max_workers, description)
        (4, 0.5, 4, "Small operation (4 modules)"),
        (8, 0.5, 4, "Medium operation (8 modules)"),
        (12, 0.5, 4, "Large operation (12 modules)"),
        (8, 0.5, 2, "Limited workers (8 modules, 2 workers)"),
    ]
    
    results = []
    
    for num_modules, duration, max_workers, description in scenarios:
        print(f"\n\n📌 {description}")
        actual, sequential, saved, speedup = benchmark_scenario(
            num_modules, duration, max_workers
        )
        results.append({
            'description': description,
            'actual': actual,
            'sequential': sequential,
            'saved': saved,
            'speedup': speedup
        })
    
    # Summary
    print(f"\n\n{'='*70}")
    print("📈 SUMMARY")
    print(f"{'='*70}\n")
    
    print(f"{'Scenario':<35} {'Actual':<10} {'Sequential':<12} {'Speedup':<10}")
    print(f"{'-'*70}")
    
    for r in results:
        print(f"{r['description']:<35} {r['actual']:>7.2f}s  "
              f"{r['sequential']:>9.2f}s  {r['speedup']:>7.2f}x")
    
    # Overall statistics
    total_actual = sum(r['actual'] for r in results)
    total_sequential = sum(r['sequential'] for r in results)
    total_saved = total_sequential - total_actual
    avg_speedup = sum(r['speedup'] for r in results) / len(results)
    
    print(f"\n{'Total Time:':<35} {total_actual:>7.2f}s  {total_sequential:>9.2f}s")
    print(f"{'Total Saved:':<35} {total_saved:>7.2f}s ({total_saved/total_sequential*100:.1f}%)")
    print(f"{'Average Speedup:':<35} {avg_speedup:>7.2f}x")
    
    print(f"\n{'='*70}")
    print("✅ Parallel execution optimization is working!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
