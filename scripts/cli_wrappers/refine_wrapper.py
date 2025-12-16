#!/usr/bin/env python3
"""
CLI Wrapper for Refinement Orchestrator
Invokes refinement_orchestrator_v1.py from Copilot Chat.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import json
import sys
from pathlib import Path

# Add src to path
cortex_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(cortex_root / "src"))

from operations.modules.orchestration.refinement_orchestrator_v1 import RefinementOrchestratorV1


def main():
    """Execute refinement orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX Refinement Orchestrator - Holistic system improvement"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview changes without applying (default)"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (disables dry-run)"
    )
    parser.add_argument(
        "--phase",
        choices=["all", "discovery", "skull", "docs", "quality", "architecture", "performance", "validation"],
        default="all",
        help="Run specific phase only"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for results (JSON)"
    )
    
    args = parser.parse_args()
    
    # Determine dry-run mode
    dry_run = not args.apply
    
    print("🎭 Orchestrator engaged: RefinementOrchestrator")
    print(f"Mode: {'DRY RUN' if dry_run else 'APPLY CHANGES'}")
    print()
    
    try:
        orchestrator = RefinementOrchestratorV1(
            cortex_root=cortex_root,
            dry_run=dry_run
        )
        
        results = orchestrator.execute()
        
        # Print summary
        print("\n" + "="*80)
        print("REFINEMENT SUMMARY")
        print("="*80)
        
        metrics = results.get("metrics", {})
        print(f"Lines Removed: {metrics.get('lines_removed', 0)}")
        print(f"Complexity Delta: {metrics.get('complexity_delta', 0.0):.2f}")
        print(f"Coverage Delta: {metrics.get('coverage_delta', 0.0):.2f}%")
        print(f"Token Reduction: {metrics.get('token_reduction', 0)}")
        print(f"Dead Code Removed: {metrics.get('dead_code_removed', 0)}")
        print(f"Duplicates Eliminated: {metrics.get('duplicates_eliminated', 0)}")
        print(f"Tests Improved: {metrics.get('tests_improved', 0)}")
        print(f"Docs Fixed: {metrics.get('docs_fixed', 0)}")
        
        if results.get("status") == "success":
            print("\n✅ Refinement completed successfully")
            if dry_run:
                print("   (Dry run - no changes applied)")
            else:
                print(f"   Rollback script: {results.get('rollback_script')}")
        else:
            print("\n❌ Refinement failed")
            if "error" in results:
                print(f"   Error: {results['error']}")
        
        # Write output file if requested
        if args.output:
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\nFull results written to: {args.output}")
        
        return 0 if results.get("status") == "success" else 1
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
