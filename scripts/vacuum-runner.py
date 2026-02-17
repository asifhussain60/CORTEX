#!/usr/bin/env python3
"""CORTEX Vacuum Runner - Thin wrapper delegating to VacuumOrchestrator.

Usage: python scripts/vacuum-runner.py [--dry-run] [--commit]

Authority: PHASE-VACUUM-REFACTOR S4 | CORE-008/011/012 | Phase 104 Enhancement
"""

import sys
import argparse
import subprocess
from pathlib import Path

CORTEX_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

from cortex_intelligence.memory.tier1_learned.orchestrators.vacuum.orchestrator import VacuumOrchestrator
from cortex_intelligence.memory.tier1_learned.orchestrators.cleaners import (
    RootDatabaseCleaner,
    MarkdownSprawlCleaner,
    RootArtifactsCleaner,
    TempScriptCleaner,
    OrphanedTestCleaner,
    ArchivedPhaseExecutorCleaner,
    BuildArtifactCleaner,
)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="CORTEX Vacuum")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()
    
    # Configure and register cleaners
    config = {"repo_root": CORTEX_ROOT, "dry_run": args.dry_run}
    orchestrator = VacuumOrchestrator(config)
    
    # Register all cleaners (including new TempScriptCleaner and OrphanedTestCleaner)
    cleaners = [
        RootDatabaseCleaner,
        MarkdownSprawlCleaner,
        RootArtifactsCleaner,
        TempScriptCleaner,
        OrphanedTestCleaner,
        ArchivedPhaseExecutorCleaner,
        BuildArtifactCleaner,
    ]
    
    for cleaner_cls in cleaners:
        try:
            orchestrator.register_cleaner(cleaner_cls)  # Pass class, not instance
        except Exception as e:
            print(f"⚠️ {cleaner_cls.__name__}: {e}")
    
    # Execute
    print(f"🧹 CORTEX Vacuum ({'DRY RUN' if args.dry_run else 'LIVE'})")
    print("=" * 60)
    
    try:
        report = orchestrator.run(dry_run=args.dry_run)
        
        # Display results
        print(f"\n📊 Status: {report.status} | Actions: {report.total_actions} | "
              f"Duration: {report.duration_seconds:.2f}s")
        
        if report.changes:
            for change_type, count in sorted(report.changes.items()):
                print(f"  {change_type}: {count}")
        
        if report.errors:
            print(f"⚠️ {len(report.errors)} errors")
        
        # Auto-commit
        if args.commit and not args.dry_run and report.status in ("SUCCESS", "PARTIAL"):
            subprocess.run(["git", "add", "-A"], cwd=CORTEX_ROOT)
            subprocess.run(["git", "commit", "-m", "chore: Vacuum cleanup"], cwd=CORTEX_ROOT)
        
        return 0 if report.status in ("SUCCESS", "PARTIAL") else 1
        
    except Exception as e:
        print(f"❌ {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

