"""
CORTEX Health Check Entry Point

Simple CLI wrapper for fast HealthCheckUtility.
Follows the same pattern as align.py for consistency.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from operations.modules.admin.healthcheck_utility import run_healthcheck_utility


def run_healthcheck():
    """
    Run CORTEX health check operation using fast utility.
    
    Returns:
        Dict with success, message, and health check results
    """
    result = run_healthcheck_utility()
    
    return {
        "success": result["success"],
        "message": result["message"],
        "data": result.get("report_data"),
    }


def main():
    """CLI entry point."""
    result = run_healthcheck()
    
    print(f"\n{'='*60}")
    print(f"CORTEX Health Check Operation")
    print(f"{'='*60}\n")
    print(result["message"])
    
    if result.get("data"):
        print(f"\nHealth Check Details:")
        for key, value in result["data"].items():
            print(f"  {key}: {value}")
    
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
