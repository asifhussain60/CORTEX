#!/usr/bin/env python3
"""Test comprehensive dashboard validation"""

from pathlib import Path
from src.operations.dashboard_validator_v2 import DashboardValidator

# Test dashboard
output_dir = Path(r"D:\PROJECTS\CORTEX\cortex-brain\documents\onboarded-apps\noor-canvas")
dashboard_path = output_dir / 'dashboard.html'

print(f"Testing dashboard: {dashboard_path}")
print(f"Dashboard exists: {dashboard_path.exists()}")
print(f"Dashboard size: {dashboard_path.stat().st_size:,} bytes\n")

validator = DashboardValidator(output_dir, dashboard_path)
success, report = validator.validate_all()

# Print comprehensive report
validator.print_report()

# Save report
import json
report_path = output_dir / 'validation_report.json'
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)

print(f"\nReport saved: {report_path}")
print(f"\nValidation Result: {'✅ PASSED' if success else '❌ FAILED'}")
