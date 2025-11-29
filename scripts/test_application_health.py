"""
Quick test script for Application Health Dashboard

Runs analysis on CORTEX repository itself and displays the report.
"""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.orchestrators.application_health_orchestrator import ApplicationHealthOrchestrator


def main():
    """Run application health analysis on CORTEX"""
    print("=" * 80)
    print("APPLICATION HEALTH DASHBOARD - Testing on CORTEX Repository")
    print("=" * 80)
    print()
    
    # Get CORTEX root directory
    cortex_root = str(project_root)
    print(f"Analyzing: {cortex_root}")
    print()
    
    # Create orchestrator and run analysis
    print("⏳ Running analysis (this may take a minute)...")
    orchestrator = ApplicationHealthOrchestrator()
    
    try:
        # Run with 'overview' for faster test
        result = orchestrator.analyze(cortex_root, scan_level='overview')
        
        print("✅ Analysis complete!")
        print()
        
        # Generate and display report
        report = orchestrator.generate_report(result)
        print(report)
        
        # Save report
        report_dir = project_root / "cortex-brain" / "documents" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = report_dir / "application-health-test-report.md"
        report_path.write_text(report, encoding='utf-8')
        
        print()
        print("=" * 80)
        print(f"📄 Report saved to: {report_path}")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
