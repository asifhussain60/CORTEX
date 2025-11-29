"""
Execute System Refactor Plugin

Runs comprehensive critical review of CORTEX architecture.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from plugins.system_refactor_plugin import SystemRefactorPlugin

def main():
    """Execute refactor plugin."""
    print("=" * 80)
    print("CORTEX System Refactor - Critical Review & Gap Analysis")
    print("=" * 80)
    print()
    
    # Create plugin
    plugin = SystemRefactorPlugin()
    
    # Initialize
    print("Initializing plugin...")
    if not plugin.initialize():
        print("ERROR: Plugin initialization failed!")
        return 1
    
    print("✓ Plugin initialized successfully")
    print()
    
    # Execute review
    print("Executing critical review...")
    print("-" * 80)
    result = plugin.execute("perform comprehensive critical review and refactor")
    
    if result["status"] == "success":
        print()
        print("=" * 80)
        print("REVIEW COMPLETE")
        print("=" * 80)
        print()
        print(f"Summary: {result['summary']}")
        print()
        print(f"Full report saved to: {result['report_path']}")
        print()
        
        # Print key findings
        report = result["report"]
        print("Key Findings:")
        print(f"  - System Health: {report['overall_health']}")
        print(f"  - Coverage Gaps: {len(report['coverage_gaps'])}")
        print(f"  - REFACTOR Tasks: {len(report['refactor_tasks'])}")
        print(f"  - Recommendations: {len(report['recommendations'])}")
        print()
        
        return 0
    else:
        print()
        print("ERROR:", result.get("error", "Unknown error"))
        return 1

if __name__ == "__main__":
    sys.exit(main())
