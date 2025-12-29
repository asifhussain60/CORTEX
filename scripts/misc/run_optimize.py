"""Quick script to run CORTEX optimization and trigger Phase 2.5 alignment check."""

from pathlib import Path
from src.operations.modules.optimization.optimize_cortex_orchestrator import OptimizeCortexOrchestrator

# Initialize orchestrator
orchestrator = OptimizeCortexOrchestrator()

# Set up context with project root
context = {
    'project_root': Path('d:/PROJECTS/CORTEX'),
    'verbose': True
}

print("=" * 80)
print("RUNNING CORTEX OPTIMIZATION")
print("This will trigger Phase 2.5 Silent System Alignment Check")
print("=" * 80)
print()

# Execute optimization
result = orchestrator.execute(context)

print()
print("=" * 80)
print("OPTIMIZATION RESULT")
print("=" * 80)
print(f"Success: {result.success}")
print(f"Status: {result.status}")
print(f"Message: {result.message}")
print(f"Duration: {result.duration_seconds:.2f}s")

if result.errors:
    print("\nErrors:")
    for error in result.errors:
        print(f"  - {error}")

if result.warnings:
    print("\nWarnings:")
    for warning in result.warnings:
        print(f"  - {warning}")

if result.data:
    print("\nData:")
    for key, value in result.data.items():
        print(f"  {key}: {value}")
