#!/usr/bin/env python3
"""Test comprehensive dashboard validation"""

from pathlib import Path
import pytest
from src.operations.dashboard_validator_v2 import DashboardValidator

# Test dashboard - use relative path from project root
project_root = Path(__file__).parent.parent.parent
output_dir = project_root / "cortex-brain" / "documents" / "onboarded-apps" / "noor-canvas"
dashboard_path = output_dir / 'dashboard.html'

def test_dashboard_exists():
    """Test that dashboard file exists"""
    # Skip if dashboard doesn't exist (not generated yet)
    if not dashboard_path.exists():
        pytest.skip(f"Dashboard not found: {dashboard_path}")
    
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
    
    assert success, "Dashboard validation failed"
