"""
Planning Migration CLI

Command-line interface for planning artifacts migration.

Part of Phase 2: Migration System
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
import logging

from src.workflows.planning_migration_engine import (
    PlanningMigrationEngine,
    MigrationResult,
    MigrationStatus,
    PlanDiscovery
)

logger = logging.getLogger(__name__)


class PlanningMigrationCLI:
    """
    Command-line interface for planning artifacts migration.
    
    Commands:
    - discover: Scan source directory and show plans
    - migrate: Migrate specific plan or all plans
    - rollback: Rollback specific or all migrations
    - status: Show migration status
    - validate: Validate migrations
    - list: List migrated plans
    """
    
    def __init__(self, source_directory: Path, target_directory: Path, cortex_root: Optional[Path] = None):
        """
        Initialize CLI.
        
        Args:
            source_directory: Source planning directory
            target_directory: Target planning directory
            cortex_root: CORTEX root directory (optional)
        """
        self.engine = PlanningMigrationEngine(
            source_directory=source_directory,
            target_directory=target_directory,
            cortex_root=cortex_root
        )
        
        logger.info("Initialized PlanningMigrationCLI")
    
    def cmd_discover(self, verbose: bool = False):
        """
        Discover plans in source directory.
        
        Args:
            verbose: Show detailed information
        """
        print("🔍 Discovering plans...")
        
        discovery = self.engine.discover_plans()
        
        print(f"\n✅ Discovered {len(discovery.master_plans)} master plan(s)")
        print(f"   - {len(discovery.sub_plans)} sub-plans")
        print(f"   - {len(discovery.trackers)} trackers")
        print(f"   - {len(discovery.reports)} reports")
        
        if verbose and discovery.master_plans:
            print("\n📋 Master Plans:")
            for plan in discovery.master_plans:
                print(f"   - {plan.plan_id}: {plan.title or 'N/A'} ({plan.status or 'unknown'})")
        
        if discovery.orphaned_artifacts:
            print(f"\n⚠️  {len(discovery.orphaned_artifacts)} orphaned artifact(s) found")
    
    def cmd_migrate(self, plan_id: str, dry_run: bool = False):
        """
        Migrate a specific plan.
        
        Args:
            plan_id: ID of plan to migrate
            dry_run: Preview migration without executing
        """
        if dry_run:
            print(f"🔍 DRY RUN: Would migrate {plan_id}")
            print("   (No files will be modified)")
            return
        
        print(f"🚀 Migrating plan: {plan_id}")
        
        result = self.engine.migrate_plan(plan_id)
        
        self._print_result(result)
    
    def cmd_migrate_all(self, dry_run: bool = False):
        """
        Migrate all plans.
        
        Args:
            dry_run: Preview migrations without executing
        """
        if dry_run:
            discovery = self.engine.discover_plans()
            print(f"🔍 DRY RUN: Would migrate {len(discovery.master_plans)} plan(s)")
            print("   (No files will be modified)")
            return
        
        print("🚀 Migrating all plans...")
        
        results = self.engine.migrate_all()
        
        # Summary
        success = sum(1 for r in results if r.status == MigrationStatus.SUCCESS)
        failed = sum(1 for r in results if r.status == MigrationStatus.FAILED)
        partial = sum(1 for r in results if r.status == MigrationStatus.PARTIAL)
        
        print(f"\n📊 Migration Summary:")
        print(f"   ✅ Success: {success}")
        if partial > 0:
            print(f"   ⚠️  Partial: {partial}")
        if failed > 0:
            print(f"   ❌ Failed: {failed}")
        
        # Show details for failures
        if failed > 0 or partial > 0:
            print("\n⚠️  Issues:")
            for result in results:
                if result.status in [MigrationStatus.FAILED, MigrationStatus.PARTIAL]:
                    print(f"   - {result.plan_id}: {result.message}")
    
    def cmd_rollback(self, plan_id: str):
        """
        Rollback migration for a specific plan.
        
        Args:
            plan_id: ID of plan to rollback
        """
        print(f"↩️  Rolling back: {plan_id}")
        
        result = self.engine.rollback_migration(plan_id)
        
        self._print_result(result)
    
    def cmd_rollback_all(self):
        """Rollback all migrations."""
        print("↩️  Rolling back all migrations...")
        
        results = self.engine.rollback_all()
        
        success = sum(1 for r in results if r.status == MigrationStatus.SUCCESS)
        print(f"\n✅ Rolled back {success}/{len(results)} plan(s)")
    
    def cmd_status(self):
        """Show migration status."""
        print("📊 Migration Status\n")
        
        migrated_plans = self.engine.list_migrated_plans()
        
        if not migrated_plans:
            print("   No migrated plans found.")
            return
        
        print(f"   Migrated Plans: {len(migrated_plans)}")
        for plan_id in migrated_plans:
            status = self.engine.get_migration_status(plan_id)
            print(f"   - {plan_id}: {status.value}")
    
    def cmd_validate(self, plan_id: str):
        """
        Validate a specific plan migration.
        
        Args:
            plan_id: ID of plan to validate
        """
        print(f"🔍 Validating: {plan_id}")
        
        is_valid = self.engine.validate_migration(plan_id)
        
        if is_valid:
            print(f"   ✅ Valid")
        else:
            print(f"   ❌ Invalid")
    
    def cmd_validate_all(self):
        """Validate all migrations."""
        print("🔍 Validating all migrations...\n")
        
        results = self.engine.validate_all_migrations()
        
        valid = sum(1 for v in results.values() if v)
        total = len(results)
        
        print(f"   ✅ Valid: {valid}/{total}")
        
        # Show invalid plans
        invalid_plans = [pid for pid, v in results.items() if not v]
        if invalid_plans:
            print(f"\n   ❌ Invalid Plans:")
            for plan_id in invalid_plans:
                print(f"      - {plan_id}")
    
    def cmd_list(self):
        """List migrated plans."""
        print("📋 Migrated Plans\n")
        
        migrated_plans = self.engine.list_migrated_plans()
        
        if not migrated_plans:
            print("   No migrated plans found.")
            return
        
        for plan_id in migrated_plans:
            print(f"   - {plan_id}")
    
    def _print_result(self, result: MigrationResult):
        """Print migration result."""
        status_emoji = {
            MigrationStatus.SUCCESS: "✅",
            MigrationStatus.FAILED: "❌",
            MigrationStatus.PARTIAL: "⚠️",
            MigrationStatus.SKIPPED: "⏭️"
        }
        
        emoji = status_emoji.get(result.status, "❓")
        print(f"\n{emoji} {result.status.value.upper()}: {result.message}")
        
        if result.files_migrated > 0:
            print(f"   Files migrated: {result.files_migrated}")
        
        if result.errors:
            print(f"   Errors:")
            for error in result.errors[:5]:  # Show first 5 errors
                print(f"      - {error}")
    
    def _format_discovery(self, discovery: PlanDiscovery) -> str:
        """Format discovery output."""
        lines = []
        lines.append(f"Discovered {len(discovery.master_plans)} master plan(s)")
        lines.append(f"  - {len(discovery.sub_plans)} sub-plans")
        lines.append(f"  - {len(discovery.trackers)} trackers")
        lines.append(f"  - {len(discovery.reports)} reports")
        return "\n".join(lines)
    
    def _format_result(self, result: MigrationResult) -> str:
        """Format migration result."""
        lines = []
        lines.append(f"Status: {result.status.value.upper()}")
        lines.append(f"Message: {result.message}")
        if result.files_migrated > 0:
            lines.append(f"Files migrated: {result.files_migrated}")
        return "\n".join(lines)
    
    def _confirm(self, message: str) -> bool:
        """
        Prompt user for confirmation.
        
        Args:
            message: Confirmation message
            
        Returns:
            True if confirmed, False otherwise
        """
        response = input(f"{message} (y/n): ").lower().strip()
        return response in ['y', 'yes']


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Planning Artifacts Migration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  discover      Scan source directory and show plans
  migrate       Migrate specific plan
  migrate-all   Migrate all plans
  rollback      Rollback specific plan
  rollback-all  Rollback all migrations
  status        Show migration status
  validate      Validate specific plan
  validate-all  Validate all migrations
  list          List migrated plans

Examples:
  %(prog)s discover --source ./planning --target ./planning-new
  %(prog)s migrate --plan-id PLAN-2025-12-14-feature
  %(prog)s migrate-all --source ./planning --target ./planning-new
  %(prog)s status --target ./planning-new
        """
    )
    
    parser.add_argument(
        "command",
        choices=["discover", "migrate", "migrate-all", "rollback", "rollback-all", 
                 "status", "validate", "validate-all", "list"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "--source",
        type=Path,
        help="Source planning directory (flat structure)"
    )
    
    parser.add_argument(
        "--target",
        type=Path,
        help="Target planning directory (hierarchical structure)"
    )
    
    parser.add_argument(
        "--plan-id",
        help="Plan ID for single-plan operations"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview operation without executing"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--cortex-root",
        type=Path,
        help="CORTEX root directory (optional)"
    )
    
    args = parser.parse_args()
    
    # Validate required arguments
    if args.command in ["discover", "migrate", "migrate-all"] and not args.source:
        parser.error("--source is required for this command")
    
    if not args.target:
        parser.error("--target is required")
    
    # Create CLI instance
    try:
        cli = PlanningMigrationCLI(
            source_directory=args.source if args.source else args.target,
            target_directory=args.target,
            cortex_root=args.cortex_root
        )
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == "discover":
            cli.cmd_discover(verbose=args.verbose)
        
        elif args.command == "migrate":
            if not args.plan_id:
                parser.error("--plan-id is required for migrate command")
            cli.cmd_migrate(plan_id=args.plan_id, dry_run=args.dry_run)
        
        elif args.command == "migrate-all":
            cli.cmd_migrate_all(dry_run=args.dry_run)
        
        elif args.command == "rollback":
            if not args.plan_id:
                parser.error("--plan-id is required for rollback command")
            cli.cmd_rollback(plan_id=args.plan_id)
        
        elif args.command == "rollback-all":
            cli.cmd_rollback_all()
        
        elif args.command == "status":
            cli.cmd_status()
        
        elif args.command == "validate":
            if not args.plan_id:
                parser.error("--plan-id is required for validate command")
            cli.cmd_validate(plan_id=args.plan_id)
        
        elif args.command == "validate-all":
            cli.cmd_validate_all()
        
        elif args.command == "list":
            cli.cmd_list()
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        logger.exception("Command execution failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
