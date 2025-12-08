"""Quick test script for CORTEX system optimization with SKULL discovery."""
from pathlib import Path
from src.operations.modules.system.optimize_system_orchestrator import OptimizeSystemOrchestrator

if __name__ == '__main__':
    print("Starting CORTEX System Optimization (Comprehensive Profile)")
    print("=" * 80)
    
    orchestrator = OptimizeSystemOrchestrator(project_root=Path('.'))
    result = orchestrator.execute({'profile': 'comprehensive'})
    
    print("\n" + "=" * 80)
    print("=== OPTIMIZATION RESULT ===")
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    
    if result.data:
        print(f"Health Score: {result.data.get('health_score', 0):.1f}/100")
        print(f"Overall Health: {result.data.get('overall_health', 'unknown')}")
        print(f"Report Path: {result.data.get('report_path', 'N/A')}")
    
    if not result.success and result.errors:
        print(f"\nErrors: {result.errors}")
