"""
Quick test to validate ArchitectureCollectorV2 with Python analyzer.
"""

from pathlib import Path
from src.dashboard.collectors.architecture_collector_v2 import ArchitectureCollectorV2

def main():
    print("Testing ArchitectureCollectorV2 with Python Analyzer...")
    print("=" * 80)
    
    # Path: src/dashboard/collectors/test_collector_quick.py
    from src.utils.resource_resolver import get_root_path
    cortex_root = get_root_path().resolve()
    test_path = cortex_root / 'src' / 'dashboard' / 'analyzers'
    
    if not test_path.exists():
        print(f"ERROR: Test path does not exist: {test_path}")
        return 1
    
    collector = ArchitectureCollectorV2(
        root_path=test_path,
        project_name='Dashboard Analyzers'
    )
    
    result = collector.collect()
    
    print(f"\nProject: {result.project_name}")
    print(f"Path: {result.project_path}")
    print(f"Timestamp: {result.scan_timestamp}")
    print(f"\nSummary:")
    print(f"  - Total Files: {result.total_files}")
    print(f"  - Total Lines: {result.total_lines}")
    print(f"  - Architecture: {result.architecture_type}")
    print(f"  - Layers: {', '.join(result.layers) if result.layers else 'None'}")
    
    print(f"\nLanguage Breakdown:")
    for lang, count in sorted(result.languages.items()):
        print(f"  - {lang}: {count} files")
    
    print(f"\nComponents:")
    if result.components:
        for comp_type, count in sorted(result.components.items()):
            print(f"  - {comp_type}: {count}")
    else:
        print("  No components detected")
    
    print(f"\nComplexity:")
    if result.complexity:
        for key, value in sorted(result.complexity.items()):
            print(f"  - {key}: {value}")
    else:
        print("  No complexity metrics")
    
    print(f"\nErrors: {len(result.errors)}")
    if result.errors:
        print("\nError Details:")
        for i, error in enumerate(result.errors[:5], 1):
            print(f"  {i}. {error}")
        if len(result.errors) > 5:
            print(f"  ... and {len(result.errors) - 5} more errors")
    
    success = len(result.errors) == 0
    print("\n" + "=" * 80)
    print(f"[{'SUCCESS' if success else 'PARTIAL'}] Multi-language analysis {'completed without errors!' if success else 'completed with errors'}")
    
    return 0 if success else 1

if __name__ == '__main__':
    exit(main())
