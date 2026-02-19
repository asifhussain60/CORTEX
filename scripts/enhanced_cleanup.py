#!/usr/bin/env python3
"""Enhanced Health & Vacuum CLI

Runs enhanced health checks and vacuum cleanup with new drift detection
and SCREAMING_CASE enforcement.

Usage:
    python scripts/enhanced_cleanup.py --mode health
    python scripts/enhanced_cleanup.py --mode vacuum --dry-run
    python scripts/enhanced_cleanup.py --mode all

Authority: Phase 103 Enhancement
Author: CORTEX Framework
Created: 2026-02-17
"""

import argparse
import sys
from pathlib import Path

# Add CORTEX to path
CORTEX_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
from cortex.orchestrators.health.agents.informational_file_agent import (
    InformationalFileAgent,
)
from cortex.orchestrators.health.agents.filename_governance_agent import (
    FilenameGovernanceAgent,
)
from cortex.orchestrators.health.agents.duplicate_detection_agent import (
    DuplicateDetectionAgent,
)
from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator as VacuumAutomation


def run_health_check(workspace_root: Path) -> dict:
    """Run enhanced health check with new agents.
    
    Args:
        workspace_root: Root path of workspace
    
    Returns:
        Health check results
    """
    print("=" * 80)
    print("🩺 ENHANCED HEALTH CHECK")
    print("=" * 80)
    print()
    
    # Initialize orchestrator
    orchestrator = HealthOrchestrator(workspace_root)
    
    # Register agents
    orchestrator.register_agent(InformationalFileAgent())
    orchestrator.register_agent(FilenameGovernanceAgent())
    orchestrator.register_agent(DuplicateDetectionAgent())
    
    print(f"✓ Registered {len(orchestrator.list_agents())} agents")
    print()
    
    # Run health check
    print("Running health check...")
    report = orchestrator.run_health_check(use_intelligence=True)
    
    # Display results
    print()
    print("=" * 80)
    print("HEALTH REPORT")
    print("=" * 80)
    print()
    
    print(f"Health Score: {report.metrics.health_score:.1f}/100")
    print(f"Total Issues: {report.metrics.total_issues}")
    print(f"  - Critical: {report.metrics.critical_issues}")
    print(f"  - High: {report.metrics.high_issues}")
    print(f"  - Medium: {report.metrics.medium_issues}")
    print(f"  - Low: {report.metrics.low_issues}")
    print()
    
    # Breakdown by agent
    print("Issues by Agent:")
    for agent_result in report.agent_results:
        issue_count = len(agent_result.issues)
        if issue_count > 0:
            print(f"  {agent_result.agent_name}: {issue_count} issues")
            
            # Show first 5 issues
            for i, issue in enumerate(agent_result.issues[:5]):
                try:
                    if issue.file_path.is_absolute():
                        rel_path = issue.file_path.relative_to(workspace_root)
                    else:
                        rel_path = issue.file_path
                    desc = issue.description[:80] if len(issue.description) > 80 else issue.description
                    print(f"    - {rel_path}: {desc}...")
                except (ValueError, AttributeError) as e:
                    print(f"    - {issue.file_path}: {issue.description[:80]}...")
            
            if issue_count > 5:
                print(f"    ... and {issue_count - 5} more")
    
    print()
    print("=" * 80)
    
    return {
        "health_score": report.metrics.health_score,
        "total_issues": report.metrics.total_issues,
        "report": report,
    }


def run_vacuum_cleanup(workspace_root: Path, dry_run: bool = True) -> dict:
    """Run enhanced vacuum cleanup.
    
    Args:
        workspace_root: Root path of workspace
        dry_run: If True, only report what would be cleaned
    
    Returns:
        Cleanup results
    """
    print("=" * 80)
    print(f"🧹 ENHANCED VACUUM CLEANUP {'(DRY RUN)' if dry_run else ''}")
    print("=" * 80)
    print()
    
    # Initialize vacuum
    vacuum = VacuumAutomation(workspace_root, dry_run=dry_run)
    
    # Run all cleanup strategies
    print("Running cleanup strategies...")
    results = vacuum.cleanup_all()
    
    # Display report
    print()
    report = vacuum.generate_report()
    print(report)
    
    return {
        "results": results,
        "dry_run": dry_run,
    }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Enhanced Health & Vacuum CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--mode",
        choices=["health", "vacuum", "all"],
        default="all",
        help="Mode to run (default: all)",
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode (vacuum only, don't actually remove files)",
    )
    
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Workspace root path (default: current directory)",
    )
    
    args = parser.parse_args()
    
    # Validate workspace
    if not args.workspace.exists():
        print(f"❌ Error: Workspace not found: {args.workspace}")
        sys.exit(1)
    
    print()
    print(f"Workspace: {args.workspace}")
    print()
    
    # Run based on mode
    if args.mode in ["health", "all"]:
        health_results = run_health_check(args.workspace)
        
        if args.mode == "all":
            print()
            input("Press Enter to continue to vacuum cleanup...")
            print()
    
    if args.mode in ["vacuum", "all"]:
        vacuum_results = run_vacuum_cleanup(args.workspace, dry_run=args.dry_run)
        
        if args.dry_run:
            print()
            print("⚠️  This was a DRY RUN. No files were actually removed.")
            print("Run without --dry-run to perform actual cleanup.")
    
    print()
    print("✅ Complete!")


if __name__ == "__main__":
    main()
