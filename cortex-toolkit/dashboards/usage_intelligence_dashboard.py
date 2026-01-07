#!/usr/bin/env python3
"""
Usage Intelligence Dashboard for CORTEX Toolkit Utilities.

Displays:
- Category breakdown
- Most/least used utilities
- Slowest utilities (optimization targets)
- Unused utilities (archival candidates)
- Success rate analysis
- Cleanup recommendations

Part of Phase P05.5: Usage Intelligence Dashboard.
"""

import json
from pathlib import Path
from typing import Dict, Any
import importlib.util

# Import ScriptsUtilitiesManager
spec = importlib.util.spec_from_file_location(
    'manager',
    Path(__file__).parent.parent / 'core' / 'scripts_utilities_manager.py'
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ScriptsUtilitiesManager = module.ScriptsUtilitiesManager


def print_header(title: str):
    """Print section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_table(headers: list, rows: list):
    """Print formatted table."""
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    
    # Print header
    header_row = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(header_row)
    print("-" * len(header_row))
    
    # Print rows
    for row in rows:
        print(" | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row)))


def display_dashboard():
    """Display usage intelligence dashboard."""
    # Detect project root
    current = Path(__file__).resolve()
    for parent in [current.parent] + list(current.parents):
        if (parent / "cortex.config.json").exists():
            project_root = parent
            break
    else:
        project_root = current.parent.parent.parent
    
    # Initialize manager
    manager = ScriptsUtilitiesManager(
        scripts_dir=str(project_root / "scripts" / "utilities"),
        toolkit_dir=str(project_root / "cortex-toolkit" / "scripts-utilities")
    )
    
    # Get usage patterns
    patterns = manager.get_usage_patterns()
    
    # Header
    print_header("CORTEX Toolkit - Usage Intelligence Dashboard")
    
    # Overview
    print(f"📊 Total Utilities: {patterns['total_utilities']}")
    print(f"📁 Categories: {len(patterns['by_category'])}")
    print(f"⚠️  Unused: {patterns['unused_count']} ({patterns['unused_count']/patterns['total_utilities']*100:.1f}%)")
    
    # Category breakdown
    print_header("Category Breakdown")
    category_rows = [[cat, count] for cat, count in patterns['by_category'].items()]
    category_rows.sort(key=lambda x: x[1], reverse=True)
    print_table(["Category", "Utilities"], category_rows)
    
    # Most used utilities
    if patterns['most_used']:
        print_header("Most Used Utilities (Top 5)")
        most_used_rows = [[u['name'], u['count']] for u in patterns['most_used']]
        print_table(["Utility", "Executions"], most_used_rows)
    
    # Slowest utilities
    if patterns['slowest']:
        print_header("Slowest Utilities (Optimization Targets)")
        slowest_rows = [[u['name'], f"{u['avg_ms']/1000:.2f}s"] for u in patterns['slowest']]
        print_table(["Utility", "Avg Duration"], slowest_rows)
    
    # Unused utilities
    if patterns['unused_utilities']:
        print_header("Unused Utilities (Archival Candidates)")
        print("These utilities have never been executed and may be candidates for archival:\n")
        for util in patterns['unused_utilities']:
            print(f"  • {util}")
    
    # Cleanup recommendations
    recommendations = manager.get_cleanup_recommendations()
    if recommendations:
        print_header("Cleanup Recommendations")
        
        # Group by priority
        high_priority = [r for r in recommendations if r['priority'] == 'high']
        medium_priority = [r for r in recommendations if r['priority'] == 'medium']
        low_priority = [r for r in recommendations if r['priority'] == 'low']
        
        if high_priority:
            print("🔴 High Priority:")
            for rec in high_priority:
                print(f"  • {rec['utility']}: {rec['action']} - {rec['reason']}")
        
        if medium_priority:
            print("\n🟡 Medium Priority:")
            for rec in medium_priority:
                print(f"  • {rec['utility']}: {rec['action']} - {rec['reason']}")
        
        if low_priority:
            print("\n🟢 Low Priority:")
            for rec in low_priority:
                print(f"  • {rec['utility']}: {rec['action']} - {rec['reason']}")
    
    # Summary
    print_header("Summary & Recommendations")
    print(f"✅ Active Utilities: {patterns['total_utilities'] - patterns['unused_count']}")
    print(f"⚠️  Review Needed: {len([r for r in recommendations if r['priority'] in ['high', 'medium']])}")
    print(f"📦 Archival Candidates: {patterns['unused_count']}")
    print(f"\n💡 Next Steps:")
    print(f"  1. Review high-priority recommendations")
    print(f"  2. Optimize slow utilities (> 60s avg)")
    print(f"  3. Archive unused utilities to cortex-brain/archives/")
    print(f"  4. Monitor usage patterns via audit logs")
    
    # Export to JSON
    dashboard_data = {
        'patterns': patterns,
        'recommendations': recommendations,
    }
    
    output_path = project_root / "cortex-toolkit" / "reports" / "usage-intelligence.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(dashboard_data, f, indent=2)
    
    print(f"\n📄 Full report saved: {output_path}")
    print("="*70)


if __name__ == "__main__":
    display_dashboard()
