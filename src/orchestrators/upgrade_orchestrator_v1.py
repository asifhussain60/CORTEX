"""
CORTEX 4.0 Upgrade Orchestrator

Handles migration of CORTEX 3.0 workspaces to 4.0 multi-repo architecture.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import json
from datetime import datetime

from src.orchestrators.base.base_orchestrator import (
    BaseOrchestrator,
    OrchestratorStatus,
    OrchestratorResult
)
from src.core.workspace_registry import WorkspaceRegistry
from src.tier3.brain_tier3 import BrainTier3, Tier3MigrationManager


class UpgradeOrchestrator(BaseOrchestrator):
    """
    Orchestrates CORTEX 3.0 to 4.0 upgrade process.
    
    Features:
    - Detects CORTEX 3.0 workspaces
    - Migrates Tier 3 context to workspace-specific storage
    - Registers workspaces in WorkspaceRegistry
    - Validates migration integrity
    - Generates upgrade report
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize upgrade orchestrator."""
        super().__init__(config)
        
        self.logger = logging.getLogger(__name__)
        self.workspace_registry = WorkspaceRegistry()
        self.migration_manager = Tier3MigrationManager()
        
        # Upgrade configuration
        self.legacy_context_db = Path(config.get("legacy_context_db", "cortex-brain/context.db"))
        self.cortex_root = Path(config.get("cortex_root", "."))
        self.dry_run = config.get("dry_run", False)
        
        # Migration state
        self.migrated_workspaces: List[Dict[str, Any]] = []
        self.failed_migrations: List[Dict[str, Any]] = []
        self.validation_results: Dict[str, Any] = {}
    
    def execute(self) -> OrchestratorResult:
        """Execute upgrade workflow."""
        try:
            self.logger.info("🔄 Starting CORTEX 3.0 → 4.0 upgrade process...")
            
            # Phase 1: Detection
            self.logger.info("Phase 1: Detecting CORTEX 3.0 workspaces...")
            legacy_workspaces = self._detect_legacy_workspaces()
            
            if not legacy_workspaces:
                self.logger.info("✅ No CORTEX 3.0 workspaces found - system already on 4.0")
                return self._success_result("No upgrade needed - already on CORTEX 4.0")
            
            self.logger.info(f"Found {len(legacy_workspaces)} CORTEX 3.0 workspace(s)")
            
            # Phase 2: Migration
            if not self.dry_run:
                self.logger.info("Phase 2: Migrating Tier 3 context...")
                self._migrate_tier3_context()
            else:
                self.logger.info("Phase 2: DRY RUN - Skipping migration (preview only)")
            
            # Phase 3: Registration
            self.logger.info("Phase 3: Registering workspaces...")
            self._register_workspaces(legacy_workspaces)
            
            # Phase 4: Validation
            self.logger.info("Phase 4: Validating migration...")
            self._validate_migration()
            
            # Phase 5: Report
            self.logger.info("Phase 5: Generating upgrade report...")
            report = self._generate_upgrade_report()
            
            # Save report
            report_path = self.cortex_root / "cortex-brain" / "documents" / "reports" / f"upgrade-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(report, indent=2))
            
            self.logger.info(f"✅ Upgrade complete! Report saved to: {report_path}")
            
            return OrchestratorResult(
                status=OrchestratorStatus.COMPLETED,
                success=True,
                message=f"Successfully upgraded {len(self.migrated_workspaces)} workspace(s) to CORTEX 4.0",
                data={
                    "migrated_workspaces": len(self.migrated_workspaces),
                    "failed_migrations": len(self.failed_migrations),
                    "validation_results": self.validation_results,
                    "report_path": str(report_path),
                    "dry_run": self.dry_run
                }
            )
            
        except Exception as e:
            self.logger.error(f"❌ Upgrade failed: {e}", exc_info=True)
            return self._error_result(f"Upgrade failed: {str(e)}")
    
    def _detect_legacy_workspaces(self) -> List[Path]:
        """
        Detect CORTEX 3.0 workspaces.
        
        3.0 indicators:
        - cortex-brain/context.db exists (legacy Tier 3 storage)
        - No .cortex/workspace-id.txt file
        - Has CORTEX-related files in root
        """
        legacy_workspaces = []
        
        # Check if legacy context.db exists
        if self.legacy_context_db.exists():
            self.logger.info(f"Found legacy context.db at {self.legacy_context_db}")
            
            # Get all workspaces from context.db
            # For now, we'll use the current workspace as the only legacy workspace
            # In reality, context.db might have tracked multiple workspaces
            if self.target_directory:
                # Check if this workspace is already upgraded
                workspace_id_file = self.target_directory / ".cortex" / "workspace-id.txt"
                if not workspace_id_file.exists():
                    legacy_workspaces.append(self.target_directory)
                    self.logger.info(f"Detected legacy workspace: {self.target_directory}")
        
        return legacy_workspaces
    
    def _migrate_tier3_context(self):
        """Migrate legacy Tier 3 context to workspace-specific storage."""
        try:
            # Use Tier3MigrationManager to migrate context.db
            if self.legacy_context_db.exists():
                self.logger.info(f"Migrating {self.legacy_context_db}...")
                
                # Migrate for current workspace
                result = self.migration_manager.migrate_legacy_context(
                    legacy_db_path=self.legacy_context_db,
                    workspace_path=self.target_directory
                )
                
                if result["success"]:
                    self.migrated_workspaces.append({
                        "workspace": str(self.target_directory),
                        "entries_migrated": result["entries_migrated"],
                        "timestamp": datetime.now().isoformat()
                    })
                    self.logger.info(f"✅ Migrated {result['entries_migrated']} context entries")
                else:
                    self.failed_migrations.append({
                        "workspace": str(self.target_directory),
                        "error": result.get("error", "Unknown error"),
                        "timestamp": datetime.now().isoformat()
                    })
                    self.logger.error(f"❌ Migration failed: {result.get('error')}")
            else:
                self.logger.info("No legacy context.db found - skipping migration")
                
        except Exception as e:
            self.logger.error(f"Error during Tier 3 migration: {e}", exc_info=True)
            self.failed_migrations.append({
                "workspace": str(self.target_directory),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    def _register_workspaces(self, workspaces: List[Path]):
        """Register legacy workspaces in WorkspaceRegistry."""
        for workspace_path in workspaces:
            try:
                # Auto-discover will register the workspace
                workspace_info = self.workspace_registry.auto_discover_workspace(workspace_path)
                
                if workspace_info:
                    self.logger.info(f"✅ Registered workspace: {workspace_info.name} ({workspace_info.workspace_id})")
                else:
                    self.logger.warning(f"⚠️ Could not register workspace: {workspace_path}")
                    
            except Exception as e:
                self.logger.error(f"Error registering workspace {workspace_path}: {e}")
    
    def _validate_migration(self):
        """Validate migration integrity."""
        self.validation_results = {
            "workspace_registered": False,
            "tier3_migrated": False,
            "workspace_id_created": False,
            "config_created": False,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Check workspace registration
            workspace_info = self.workspace_registry.get_by_path(self.target_directory)
            self.validation_results["workspace_registered"] = workspace_info is not None
            
            # Check workspace ID file
            workspace_id_file = self.target_directory / ".cortex" / "workspace-id.txt"
            self.validation_results["workspace_id_created"] = workspace_id_file.exists()
            
            # Check config file
            config_file = self.target_directory / ".cortex" / "config.json"
            self.validation_results["config_created"] = config_file.exists()
            
            # Check Tier 3 migration
            tier3_dir = self.target_directory / ".cortex" / "tier3"
            self.validation_results["tier3_migrated"] = tier3_dir.exists() and any(tier3_dir.iterdir()) if tier3_dir.exists() else False
            
            # Overall validation
            all_valid = all([
                self.validation_results["workspace_registered"],
                self.validation_results["workspace_id_created"],
                self.validation_results["config_created"]
            ])
            
            if all_valid:
                self.logger.info("✅ Migration validation passed")
            else:
                self.logger.warning("⚠️ Migration validation incomplete")
                
        except Exception as e:
            self.logger.error(f"Validation error: {e}", exc_info=True)
    
    def _generate_upgrade_report(self) -> Dict[str, Any]:
        """Generate comprehensive upgrade report."""
        return {
            "upgrade_timestamp": datetime.now().isoformat(),
            "cortex_version": {
                "from": "3.0",
                "to": "4.0"
            },
            "migration_summary": {
                "total_workspaces": len(self.migrated_workspaces) + len(self.failed_migrations),
                "successful": len(self.migrated_workspaces),
                "failed": len(self.failed_migrations)
            },
            "migrated_workspaces": self.migrated_workspaces,
            "failed_migrations": self.failed_migrations,
            "validation_results": self.validation_results,
            "configuration": {
                "dry_run": self.dry_run,
                "cortex_root": str(self.cortex_root),
                "legacy_context_db": str(self.legacy_context_db)
            },
            "next_steps": self._get_next_steps()
        }
    
    def _get_next_steps(self) -> List[str]:
        """Determine next steps based on migration results."""
        next_steps = []
        
        if self.failed_migrations:
            next_steps.append("Review failed migrations and retry")
        
        if not self.validation_results.get("workspace_registered"):
            next_steps.append("Manually register workspace with WorkspaceRegistry")
        
        if not self.validation_results.get("tier3_migrated"):
            next_steps.append("Verify Tier 3 context migration completed")
        
        if not next_steps:
            next_steps.append("Upgrade complete - no further action required")
        
        return next_steps
    
    def _success_result(self, message: str) -> OrchestratorResult:
        """Create success result."""
        return OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message=message,
            data={}
        )
    
    def _error_result(self, message: str) -> OrchestratorResult:
        """Create error result."""
        return OrchestratorResult(
            status=OrchestratorStatus.FAILED,
            success=False,
            message=message,
            data={}
        )
