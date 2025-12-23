#!/usr/bin/env python3
"""
Dashboard Validation Runner for Phase 14 Task 14.4

Validates all dashboard tabs and generates comprehensive report.

Author: Asif Hussain
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from operations.dashboard_validator import DashboardValidator


def main():
    """Run dashboard validation"""
    dashboard_path = Path("cortex-brain/dashboards/ui/index.html")
    output_dir = Path("cortex-brain/dashboards")
    
    print(f"\n🔍 Validating Dashboard: {dashboard_path}")
    print(f"📁 Output Directory: {output_dir}\n")
    
    validator = DashboardValidator(output_dir, dashboard_path)
    success, report = validator.validate_all()
    
    # Print detailed report
    validator.print_report()
    
    # Save JSON report
    report_path = output_dir / "validation-report.json"
    import json
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Detailed report saved to: {report_path}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
