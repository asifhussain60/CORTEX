#!/usr/bin/env python3
"""
CORTEX Deploy Operation - CLI Entry Point

Runs CORTEX deployment with validation gates.
Wrapper for scripts/deploy_cortex.py to enable module execution pattern.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))

# Import deployment function
from deploy_cortex import publish_to_branch, PUBLISH_BRANCH


def run_deploy(
    dry_run: bool = False,
    skip_validation: bool = False,
    branch: str = PUBLISH_BRANCH
):
    """
    Run CORTEX deploy operation with validators.
    
    Args:
        dry_run: Preview only, don't make changes
        skip_validation: Skip deployment gates (use with caution)
        branch: Target branch name (default: main)
    
    Returns:
        dict: Operation result with success status
    """
    try:
        success = publish_to_branch(
            project_root=project_root,
            branch_name=branch,
            dry_run=dry_run,
            resume=False,
            skip_validation=skip_validation
        )
        
        return {
            "success": success,
            "operation": "deploy",
            "branch": branch,
            "dry_run": dry_run,
            "validation_enabled": not skip_validation
        }
    except Exception as e:
        return {
            "success": False,
            "operation": "deploy",
            "error": str(e)
        }


def main():
    """CLI entry point for module execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX deployment with validation gates"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview only, no changes'
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip deployment gates (caution)'
    )
    parser.add_argument(
        '--branch',
        type=str,
        default=PUBLISH_BRANCH,
        help=f'Target branch (default: {PUBLISH_BRANCH})'
    )
    
    args = parser.parse_args()
    
    result = run_deploy(
        dry_run=args.dry_run,
        skip_validation=args.skip_validation,
        branch=args.branch
    )
    
    if result["success"]:
        print("\n✅ Deployment complete")
        if result.get("dry_run"):
            print("   (Dry run - no changes made)")
        print(f"   Branch: {result.get('branch', 'main')}")
        print(f"   Validation: {'SKIPPED' if not result.get('validation_enabled') else 'ENABLED'}")
        sys.exit(0)
    else:
        print("\n❌ Deployment failed")
        if "error" in result:
            print(f"   Error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
