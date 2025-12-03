"""
Commit Entry Point

Simple CLI wrapper for fast CommitUtility.
Follows standard CORTEX operations pattern.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from operations.modules.git.commit_utility import run_commit_utility


def run_commit(**kwargs):
    """
    Run commit operation using fast utility.
    
    Returns:
        Dict with success, message, and commit results
    """
    result = run_commit_utility(**kwargs)
    
    return {
        "success": result["success"],
        "message": result["message"],
        "data": result.get("data"),
    }


def main():
    """CLI entry point."""
    result = run_commit()
    
    print(f"\n{'='*60}")
    print(f"Commit Operation")
    print(f"{'='*60}\n")
    print(result["message"])
    
    if result.get("data"):
        print(f"\nCommit Details:")
        for key, value in result["data"].items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
