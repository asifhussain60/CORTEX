#!/usr/bin/env python3
"""
Validate Dashboard Data - Quick Test Script

Validates the security data for V5.WebServices.PrevalidationWS to ensure
consistency and accuracy before displaying in dashboard.

Author: Asif Hussain
"""

import sys
import json
from pathlib import Path

# Add CORTEX to path
cortex_root = Path(__file__).parent
sys.path.insert(0, str(cortex_root))
sys.path.insert(0, str(cortex_root / "src"))

from src.dashboard.data.data_validator import DashboardDataValidator


def main():
    """Validate dashboard data."""
    
    # Load security.json
    security_file = cortex_root / "cortex-brain" / "dashboards" / "v5-webservices-prevalidationws" / "security.json"
    
    if not security_file.exists():
        print(f"ERROR: Security file not found: {security_file}")
        return 1
    
    print(f"Loading security data from: {security_file}\n")
    
    with open(security_file, 'r', encoding='utf-8') as f:
        security_data = json.load(f)
    
    # Run validation
    validator = DashboardDataValidator()
    is_valid, errors, warnings = validator.validate_all(security_data)
    
    # Print report
    print(validator.get_validation_report())
    
    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
