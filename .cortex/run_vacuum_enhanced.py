#!/usr/bin/env python3
"""Execute VacuumOrchestrator cleanup on CORTEX repository.

This script performs:
1. Database file migration to proper locations
2. Root artifacts cleanup (logs, reports)
3. Verification and reporting

AC-VACUUM-002: Enhanced repository cleanup
"""

import sys
from pathlib import Path

# Add cortex_brain to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "cortex_brain"))

from tier1.orchestrators.vacuum import VacuumOrchestrator
from tier1.orchestrators.cleaners import (
    DatabaseMigrationCleaner,
    RootArtifactsCleaner,
)


def main() -> int:
    """Execute vacuum orchestrator cleanup.
    
    Returns:
        Exit code (0=success, 1=failure)
    """
    print("━" * 70)
    print("🧹 CORTEX VacuumOrchestrator - Enhanced Cleanup")
    print("━" * 70)
    print()
    
    config = {
        "repo_root": str(repo_root),
        "dry_run": False,  # Set to True for dry run
    }
    
    # Create orchestrator
    orch = VacuumOrchestrator(config=config)
    
    # Register cleaners
    print("📋 Registering cleaners...")
    result = orch.register_cleaner(DatabaseMigrationCleaner, config)
    if result.is_err():
        print(f"❌ Failed to register DatabaseMigrationCleaner: {result.error}")
        return 1
    print("  ✅ DatabaseMigrationCleaner")
    
    result = orch.register_cleaner(RootArtifactsCleaner, config)
    if result.is_err():
        print(f"❌ Failed to register RootArtifactsCleaner: {result.error}")
        return 1
    print("  ✅ RootArtifactsCleaner")
    print()
    
    # Execute database migration
    print("🗄️  Phase 1: Database File Migration")
    print("─" * 70)
    
    analysis = orch.analyze("database_migration")
    print(f"  Files scanned: {analysis.files_scanned}")
    print(f"  Issues found: {analysis.issues_found}")
    
    if analysis.issues_found > 0:
        print(f"  Actions planned: {len(analysis.plan['actions'])}")
        for action in analysis.plan["actions"]:
            source = Path(action["source"]).name
            target = Path(action["target"]).parent
            print(f"    • {source} → {target}")
        
        report = orch.execute("database_migration", analysis.plan)
        print(f"\n  Status: {report.status}")
        print(f"  Actions taken: {report.actions_taken}")
        
        if report.errors:
            print("  Errors:")
            for error in report.errors:
                print(f"    ❌ {error}")
    else:
        print("  ✅ No database files to migrate")
    
    print()
    
    # Execute root artifacts cleanup
    print("📦 Phase 2: Root Artifacts Cleanup")
    print("─" * 70)
    
    analysis = orch.analyze("root_artifacts")
    print(f"  Files scanned: {analysis.files_scanned}")
    print(f"  Issues found: {analysis.issues_found}")
    
    if analysis.issues_found > 0:
        print(f"  Actions planned: {len(analysis.plan['actions'])}")
        for action in analysis.plan["actions"]:
            source = Path(action["source"]).name
            target = Path(action["target"]).parent
            print(f"    • {source} → {target}")
        
        report = orch.execute("root_artifacts", analysis.plan)
        print(f"\n  Status: {report.status}")
        print(f"  Actions taken: {report.actions_taken}")
        
        if report.errors:
            print("  Errors:")
            for error in report.errors:
                print(f"    ❌ {error}")
    else:
        print("  ✅ No root artifacts to clean")
    
    print()
    
    # Generate final report
    print("📊 Final Report")
    print("─" * 70)
    
    final_report = orch.generate_report()
    print(f"  State: {final_report.state.value}")
    print(f"  Overall status: {final_report.overall_status}")
    print(f"  Analyses completed: {final_report.analyses_completed}")
    print(f"  Executions completed: {final_report.executions_completed}")
    print(f"  Cleaners used: {final_report.stats.cleaners_used}")
    print(f"  Issues fixed: {final_report.stats.issues_fixed}")
    
    if final_report.errors:
        print(f"  Errors encountered: {len(final_report.errors)}")
        for error in final_report.errors:
            print(f"    ❌ {error}")
    
    print()
    print("━" * 70)
    print("✅ Vacuum orchestrator complete")
    print("━" * 70)
    
    return 0 if final_report.overall_status in ["SUCCESS", "PARTIAL"] else 1


if __name__ == "__main__":
    sys.exit(main())
