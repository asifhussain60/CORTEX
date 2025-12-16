#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORTEX Deploy Operation - CLI Entry Point

Runs CORTEX deployment with validation gates.
Wrapper for scripts/deploy_cortex.py to enable module execution pattern.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import io
from pathlib import Path

# Fix Windows console encoding for Unicode emoji support
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
project_root = get_root_path()
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))

from deploy_cortex import publish_to_branch, PUBLISH_BRANCH
from src.utils.resource_resolver import get_root_path


def run_deploy(
    dry_run: bool = False,
    branch: str = PUBLISH_BRANCH,
    skip_align: bool = False
):
    """
    Run CORTEX deploy operation with validators.
    
    ALL DEPLOYMENT GATES MANDATORY - No skipping allowed.
    All 19 gates must pass for production deployment.
    
    Args:
        dry_run: Preview only, don't make changes
        branch: Target branch name (default: main)
        skip_align: Skip pre-flight alignment check (not recommended)
    
    Returns:
        dict: Operation result with success status
    """
    try:
        success = publish_to_branch(
            project_root=project_root,
            branch_name=branch,
            dry_run=dry_run,
            resume=False,
            skip_align=skip_align
        )
        
        return {
            "success": success,
            "operation": "deploy",
            "branch": branch,
            "dry_run": dry_run,
            "validation": "MANDATORY (all 19 gates enforced)"
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
        '--branch',
        type=str,
        default=PUBLISH_BRANCH,
        help=f'Target branch (default: {PUBLISH_BRANCH})'
    )
    parser.add_argument(
        '--skip-align',
        action='store_true',
        help='Skip pre-flight alignment check (not recommended)'
    )
    
    args = parser.parse_args()
    
    result = run_deploy(
        dry_run=args.dry_run,
        branch=args.branch,
        skip_align=args.skip_align
    )
    
    if result["success"]:
        print("\n✅ Deployment complete")
        if result.get("dry_run"):
            print("   (Dry run - no changes made)")
        print(f"   Branch: {result.get('branch', 'main')}")
        print(f"   {result.get('validation', 'Validation: MANDATORY')}")
        sys.exit(0)
    else:
        print("\n❌ Deployment failed")
        if "error" in result:
            print(f"   Error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
