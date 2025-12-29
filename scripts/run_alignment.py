"""Direct execution of System Alignment Orchestrator."""

from pathlib import Path
from src.operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator

# Initialize orchestrator
orchestrator = SystemAlignmentOrchestrator()

# Set up context
context = {
    'project_root': Path('d:/PROJECTS/CORTEX'),
    'verbose': True
}

print("=" * 80)
print("RUNNING SYSTEM ALIGNMENT CHECK")
print("=" * 80)
print()

# Execute alignment
result = orchestrator.execute(context)

print()
print("=" * 80)
print("ALIGNMENT RESULT")
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
    print("\nAlignment Data:")
    for key, value in result.data.items():
        if isinstance(value, list):
            print(f"  {key}: [{len(value)} items]")
            if value and len(value) <= 5:
                for item in value:
                    print(f"    - {item}")
        elif isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")
