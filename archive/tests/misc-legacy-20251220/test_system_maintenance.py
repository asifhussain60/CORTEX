"""Test System Maintenance Orchestrator"""

import sys
import io

# Set UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from src.operations.modules.orchestration.system_maintenance_orchestrator import SystemMaintenanceOrchestrator

def main():
    """Run system maintenance test."""
    print("=" * 60)
    print("CORTEX System Maintenance Orchestrator Test")
    print("=" * 60)
    print()
    
    orchestrator = SystemMaintenanceOrchestrator()
    result = orchestrator.execute({})
    
    print("\n" + "=" * 60)
    print(f"Result: {result.status.value}")
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    print(f"Phases Completed: {result.data.get('phases_completed', 0)}/4")
    print("=" * 60)
    
    if result.data.get('improvements'):
        print("\nImprovements:")
        for imp in result.data['improvements']:
            print(f"  + {imp}")
    
    if result.warnings:
        print("\nWarnings:")
        for warn in result.warnings:
            print(f"  ! {warn}")
    
    if result.errors:
        print("\nErrors:")
        for err in result.errors:
            print(f"  x {err}")
    
    if result.data.get('report_path'):
        print(f"\nReport: {result.data['report_path']}")
    
    print("\n" + "=" * 60)
    print("System Maintenance Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
