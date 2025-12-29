#!/usr/bin/env python3
"""
CORTEX Upgrade CLI Wrapper v2 - Brain-Safe Deployment

Command-line interface for CORTEX system upgrades with 9-phase workflow.

Features:
- 9-phase brain-safe upgrade workflow
- Zero data loss guarantee (brain preservation)
- Pre/post health checks
- Automatic rollback on failure (Phase 5+)
- User-facing feature validation only
- Immutable backups with verification
- Prompt & config sync
- Comprehensive upgrade reports

Usage:
    python scripts/cli_wrappers/upgrade_wrapper.py
    python scripts/cli_wrappers/upgrade_wrapper.py --check-only
    python scripts/cli_wrappers/upgrade_wrapper.py --dry-run
    python scripts/cli_wrappers/upgrade_wrapper.py --rollback <backup_id>
    python scripts/cli_wrappers/upgrade_wrapper.py --list-backups

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 2.0.0
"""

import sys
from pathlib import Path
from typing import Dict, Any
import argparse

# Add CORTEX root to path
CORTEX_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

from scripts.cli_wrappers.base_wrapper import BaseCLIWrapper, main_template
from src.orchestrators.upgrade_orchestrator_v2 import UpgradeOrchestratorV2
from src.operations.modules.upgrade.upgrade_utility import (
    check_for_updates,
    create_backup,
    list_backups,
    restore_backup,
    get_current_version,
    VersionInfo
)
from src.operations.base_operation_module import OperationResult, OperationStatus


class UpgradeWrapper(BaseCLIWrapper):
    """CLI wrapper for brain-safe CORTEX system upgrade (v2)."""
    
    def get_operation_name(self) -> str:
        """Get operation name for logging."""
        return "upgrade"
    
    def get_orchestrator(self):
        """
        Get UpgradeOrchestratorV2 instance.
        
        Returns:
            UpgradeOrchestratorV2 configured for CLI execution
        """
        return UpgradeOrchestratorV2(
            config={
                "cortex_root": str(CORTEX_ROOT),
                "dry_run": False,  # Overridden in execute()
                "skip_phases": []
            }
        )
    
    def setup_argparse(self, parser: argparse.ArgumentParser) -> None:
        """Configure command-line arguments."""
        super().setup_argparse(parser)
        
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='Check for updates without upgrading'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview upgrade without making changes'
        )
        parser.add_argument(
            '--rollback',
            type=str,
            metavar='BACKUP_ID',
            help='Rollback to specific backup (e.g., 20251227_143000)'
        )
        parser.add_argument(
            '--list-backups',
            action='store_true',
            help='List available backups'
        )
    
    def execute(self) -> OperationResult:
        """
        Execute upgrade operation with 9-phase workflow.
        
        Returns:
            OperationResult with upgrade status
        """
        try:
            # Handle special operations
            if self.args.list_backups:
                return self._list_backups()
            
            if self.args.check_only:
                return self._check_for_updates()
            
            if self.args.rollback:
                return self._rollback_upgrade(self.args.rollback)
            
            # Execute full 9-phase upgrade
            orchestrator = self.get_orchestrator()
            orchestrator.dry_run = self.args.dry_run
            
            print("🎭 Orchestrator engaged: UpgradeOrchestratorV2")
            print("🚀 Starting brain-safe CORTEX upgrade...")
            print()
            
            result = orchestrator.execute()
            
            if result.success:
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message=result.message,
                    data=result.data
                )
            else:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message=result.message,
                    data=result.data,
                    errors=[result.message]
                )
        
        except Exception as e:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Upgrade failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _list_backups(self) -> OperationResult:
        """List available backups."""
        try:
            backups = list_backups(CORTEX_ROOT)
            
            print("\n📦 Available Backups:")
            print("=" * 80)
            
            if not backups:
                print("No backups found.")
            else:
                for backup in backups:
                    print(f"\nBackup ID: {backup.backup_id}")
                    print(f"Timestamp: {backup.timestamp}")
                    print(f"Version: {backup.version}")
                    print(f"Branch: {backup.branch}")
                    print(f"Size: {backup.total_size_bytes / 1024 / 1024:.2f} MB")
                    print(f"Verified: {'✅' if backup.verified else '❌'}")
            
            print("\n" + "=" * 80)
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Found {len(backups)} backup(s)",
                data={"backups": len(backups)}
            )
        
        except Exception as e:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Failed to list backups: {str(e)}",
                errors=[str(e)]
            )
    
    def _check_for_updates(self) -> OperationResult:
        """Check for updates without upgrading."""
        try:
            print("🔍 Checking for updates...")
            
            version_info = check_for_updates(CORTEX_ROOT)
            current_version = get_current_version(CORTEX_ROOT)
            
            print(f"\nCurrent Version: {current_version}")
            print(f"Remote Version: {version_info.version}")
            print(f"Updates Available: {'✅ Yes' if version_info.has_updates else '❌ No'}")
            
            if version_info.has_updates:
                print(f"\n📢 Update available: {current_version} → {version_info.version}")
                print("Run without --check-only to upgrade.")
            else:
                print("\n✅ You're on the latest version!")
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message="Version check complete",
                data={
                    "current_version": current_version,
                    "remote_version": version_info.version,
                    "has_updates": version_info.has_updates
                }
            )
        
        except Exception as e:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Version check failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _rollback_upgrade(self, backup_id: str) -> OperationResult:
        """Rollback to previous version using backup."""
        try:
            print(f"🔄 Rolling back to backup: {backup_id}")
            
            success = restore_backup(CORTEX_ROOT, backup_id)
            
            if success:
                print(f"✅ Rollback successful!")
                print("Run healthcheck to verify system integrity.")
                
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message="Rollback successful",
                    data={"backup_id": backup_id}
                )
            else:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="Rollback failed",
                    errors=["Backup restoration failed"]
                )
        
        except Exception as e:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Rollback failed: {str(e)}",
                errors=[str(e)]
            )


def main():
    """Main entry point."""
    return main_template(UpgradeWrapper)


if __name__ == '__main__':
    sys.exit(main())
