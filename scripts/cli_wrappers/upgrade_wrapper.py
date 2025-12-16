#!/usr/bin/env python3
"""
CORTEX Upgrade CLI Wrapper

Command-line interface for CORTEX system upgrades.

Features:
- Version checking and comparison
- Brain data backup/restore with verification
- Git pull from origin/main
- Dependency updates (requirements.txt)
- Schema migrations
- Operational readiness validation
- What's New feature discovery
- Rollback support

Usage:
    python scripts/cli_wrappers/upgrade_wrapper.py
    python scripts/cli_wrappers/upgrade_wrapper.py --check-only
    python scripts/cli_wrappers/upgrade_wrapper.py --backup-only
    python scripts/cli_wrappers/upgrade_wrapper.py --force

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import sys
from pathlib import Path
from typing import Dict, Any
import argparse

# Add CORTEX root to path
CORTEX_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

from scripts.cli_wrappers.base_wrapper import BaseCLIWrapper, main_template
from src.operations.modules.upgrade.upgrade_utility import (
    execute_upgrade,
    check_for_updates,
    create_backup,
    list_backups,
    VersionInfo,
    UpgradeResult
)
from src.operations.base_operation_module import OperationResult, OperationStatus


class UpgradeWrapper(BaseCLIWrapper):
    """CLI wrapper for CORTEX system upgrade."""
    
    def get_orchestrator(self):
        """
        Get upgrade executor.
        
        Note: execute_upgrade is a function, not a class.
        We'll wrap it in a simple executor.
        """
        class UpgradeExecutor:
            def __init__(self):
                self.cortex_root = CORTEX_ROOT
            
            def run(self, check_only: bool = False, backup_only: bool = False, 
                   force: bool = False, auto_confirm: bool = True) -> UpgradeResult:
                """Execute upgrade with options."""
                if check_only:
                    version_info = check_for_updates(self.cortex_root)
                    return UpgradeResult(
                        success=True,
                        from_version=version_info.version,
                        to_version="N/A",
                        backup_id=None,
                        migrations_applied=0,
                        whats_new="Check only mode",
                        validation_results={"has_updates": version_info.has_updates},
                        message="Version check complete",
                        errors=[]
                    )
                
                if backup_only:
                    backup = create_backup(self.cortex_root)
                    return UpgradeResult(
                        success=backup is not None,
                        from_version="N/A",
                        to_version="N/A",
                        backup_id=backup.backup_id if backup else None,
                        migrations_applied=0,
                        whats_new="Backup only mode",
                        validation_results={"backup_created": backup is not None},
                        message="Backup complete" if backup else "Backup failed",
                        errors=[] if backup else ["Backup creation failed"]
                    )
                
                return execute_upgrade(
                    cortex_root=self.cortex_root,
                    force=force,
                    auto_confirm=auto_confirm
                )
        
        return UpgradeExecutor()
    
    def execute(self, args: argparse.Namespace) -> OperationResult:
        """
        Execute upgrade operation.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            OperationResult with upgrade status
        """
        try:
            orchestrator = self.get_orchestrator()
            
            # Execute upgrade
            result = orchestrator.run(
                check_only=args.check_only,
                backup_only=args.backup_only,
                force=args.force,
                auto_confirm=not args.interactive
            )
            
            if result.success:
                return self.success_result(
                    message=result.message,
                    data={
                        "from_version": result.from_version,
                        "to_version": result.to_version,
                        "backup_id": result.backup_id,
                        "migrations_applied": result.migrations_applied,
                        "whats_new": result.whats_new,
                        "validation_results": result.validation_results
                    }
                )
            else:
                return self.error_result(
                    message=result.message,
                    errors=result.errors
                )
        
        except Exception as e:
            return self.error_result(
                message=f"Upgrade failed: {str(e)}",
                errors=[str(e)]
            )
    
    def add_custom_args(self, parser: argparse.ArgumentParser):
        """Add upgrade-specific arguments."""
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='Check for updates without upgrading'
        )
        parser.add_argument(
            '--backup-only',
            action='store_true',
            help='Create backup without upgrading'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force upgrade even if on latest version'
        )
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Prompt for confirmation before upgrading'
        )
        parser.add_argument(
            '--list-backups',
            action='store_true',
            help='List available backups'
        )


def main():
    """Main entry point."""
    wrapper = UpgradeWrapper()
    
    # Handle list-backups as special case
    if '--list-backups' in sys.argv:
        backups = list_backups(CORTEX_ROOT)
        print("\n📦 Available Backups:")
        print("=" * 80)
        for backup in backups:
            print(f"\nBackup ID: {backup.backup_id}")
            print(f"Timestamp: {backup.timestamp}")
            print(f"Version: {backup.version}")
            print(f"Branch: {backup.branch}")
            print(f"Size: {backup.size_bytes / 1024 / 1024:.2f} MB")
            print(f"Verified: {'✅' if backup.verified else '❌'}")
        print("\n" + "=" * 80)
        sys.exit(0)
    
    return main_template(wrapper)


if __name__ == '__main__':
    sys.exit(main())
