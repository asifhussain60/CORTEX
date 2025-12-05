"""
Full CORTEX repository analysis with Python support.
"""

from pathlib import Path
from src.dashboard.collectors.architecture_collector_v2 import ArchitectureCollectorV2

def main():
    print("=" * 80)
    print("CORTEX Full Repository Analysis")
    print("=" * 80)
    
    cortex_root = Path(__file__).parent.parent.parent.parent.resolve()
    
    collector = ArchitectureCollectorV2(
        root_path=cortex_root,
        project_name='CORTEX'
    )
    
    print(f"\nAnalyzing: {cortex_root}")
    print("This may take a few minutes for 1700+ files...\n")
    
    result = collector.collect()
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    
    print(f"\nProject: {result.project_name}")
    print(f"Path: {result.project_path}")
    print(f"Timestamp: {result.scan_timestamp}")
    
    print(f"\n{'-' * 80}")
    print("SUMMARY")
    print(f"{'-' * 80}")
    print(f"Total Files: {result.total_files:,}")
    print(f"Total Lines: {result.total_lines:,}")
    print(f"Architecture: {result.architecture_type}")
    print(f"Layers: {', '.join(result.layers) if result.layers else 'None'}")
    
    print(f"\n{'-' * 80}")
    print("LANGUAGE BREAKDOWN")
    print(f"{'-' * 80}")
    for lang, count in sorted(result.languages.items(), key=lambda x: x[1], reverse=True):
        print(f"{lang:15} {count:5,} files")
    
    print(f"\n{'-' * 80}")
    print("COMPONENTS")
    print(f"{'-' * 80}")
    if result.components:
        total_components = sum(result.components.values())
        print(f"Total: {total_components:,}\n")
        for comp_type, count in sorted(result.components.items(), key=lambda x: x[1], reverse=True):
            print(f"{comp_type:15} {count:5,}")
    else:
        print("No components detected")
    
    print(f"\n{'-' * 80}")
    print("COMPLEXITY")
    print(f"{'-' * 80}")
    if result.complexity:
        for key, value in sorted(result.complexity.items()):
            if isinstance(value, float):
                print(f"{key:20} {value:,.2f}")
            else:
                print(f"{key:20} {value:,}")
    
    print(f"\n{'-' * 80}")
    print("TECHNOLOGY STACK")
    print(f"{'-' * 80}")
    if result.backend:
        print("Backend:", result.backend)
    if result.frontend:
        print("Frontend:", result.frontend)
    if result.database:
        print("Database:", result.database)
    
    print(f"\n{'-' * 80}")
    print("PATTERNS")
    print(f"{'-' * 80}")
    if result.patterns:
        for pattern in result.patterns:
            print(f"  - {pattern}")
    else:
        print("No patterns detected")
    
    print(f"\n{'-' * 80}")
    print("ERRORS & WARNINGS")
    print(f"{'-' * 80}")
    print(f"Errors: {len(result.errors)}")
    print(f"Warnings: {len(result.warnings)}")
    
    if result.errors:
        print("\nFirst 10 errors:")
        for i, error in enumerate(result.errors[:10], 1):
            print(f"  {i}. {error}")
        if len(result.errors) > 10:
            print(f"  ... and {len(result.errors) - 10} more errors")
    
    # Save report
    report_path = cortex_root / 'cortex-brain' / 'documents' / 'reports' / 'cortex-full-analysis.md'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# CORTEX Full Repository Analysis\n\n")
        f.write(f"**Generated:** {result.scan_timestamp}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- **Total Files:** {result.total_files:,}\n")
        f.write(f"- **Total Lines:** {result.total_lines:,}\n")
        f.write(f"- **Architecture:** {result.architecture_type}\n")
        f.write(f"- **Layers:** {', '.join(result.layers)}\n\n")
        
        f.write(f"## Languages\n\n")
        for lang, count in sorted(result.languages.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- **{lang}:** {count:,} files\n")
        
        f.write(f"\n## Components\n\n")
        f.write(f"**Total:** {sum(result.components.values()):,}\n\n")
        for comp_type, count in sorted(result.components.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- **{comp_type}:** {count:,}\n")
        
        f.write(f"\n## Complexity\n\n")
        for key, value in sorted(result.complexity.items()):
            if isinstance(value, float):
                f.write(f"- **{key}:** {value:,.2f}\n")
            else:
                f.write(f"- **{key}:** {value:,}\n")
        
        f.write(f"\n## Status\n\n")
        f.write(f"- **Errors:** {len(result.errors)}\n")
        f.write(f"- **Warnings:** {len(result.warnings)}\n")
    
    print(f"\n\nReport saved to: {report_path}")
    
    success = len(result.errors) == 0
    print("\n" + "=" * 80)
    print(f"[{'SUCCESS' if success else 'COMPLETED WITH ERRORS'}]")
    print("=" * 80)
    
    return 0 if success else 1

if __name__ == '__main__':
    exit(main())
