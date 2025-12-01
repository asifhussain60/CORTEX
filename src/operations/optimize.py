"""
CORTEX Optimize Entry Point

Simple CLI wrapper for OptimizeOperation.
Follows the same pattern as align.py for consistency.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from operations.optimize_operation import OptimizeOperation


def run_optimize():
    """
    Run CORTEX optimize operation.
    
    Returns:
        Dict with success, message, and optimization results
    """
    optimizer = OptimizeOperation()
    result = optimizer.execute()
    
    return {
        "success": result.success,
        "message": result.message,
        "data": result.data,
    }


def main():
    """CLI entry point."""
    result = run_optimize()
    
    print(f"\n{'='*60}")
    print(f"CORTEX Optimize Operation")
    print(f"{'='*60}\n")
    print(result["message"])
    
    if result.get("data"):
        print(f"\nOptimization Details:")
        for key, value in result["data"].items():
            print(f"  {key}: {value}")
    
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
