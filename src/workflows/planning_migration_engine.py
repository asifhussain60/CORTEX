"""
Planning Migration Engine

Migrates planning artifacts from flat structure to hierarchical folder structure.

Part of Phase 2: Migration System
"""

import shutil
from pathlib import Path
from typing import List, Dict, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import logging

from src.workflows.planning_artifacts_scanner import (
    PlanningArtifactsScanner,
    PlanDiscovery,
    PlanMetadata,
    ArtifactType
)
from src.workflows.plan_folder_manager import PlanFolderManager

logger = logging.getLogger(__name__)


class MigrationStatus(Enum):
    """Status of migration operation"""
    NOT_MIGRATED = "not_migrated"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


@dataclass
class MigrationResult:
    """Result of a migration operation"""
    plan_id: str
    status: MigrationStatus
    message: str = ""
    files_migrated: int = 0
    errors: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class PlanningMigrationEngine:
    """
    Migrates planning artifacts from flat structure to hierarchical folders.
    
    Responsibilities:
    - Discover plans in flat structure
    - Create hierarchical folder structure for each plan
    - Move artifacts to appropriate subfolders
    - Validate migrations
    - Support rollback
    """
    
    def __init__(self, source_directory: Path, target_directory: Path, cortex_root: Optional[Path] = None):
        """
        Initialize migration engine.
        
        Args:
            source_directory: Current flat planning directory
            target_directory: New hierarchical planning directory
            cortex_root: Root of CORTEX project (optional, for folder manager)
        """
        self.source_directory = Path(source_directory)
        self.target_directory = Path(target_directory)
        
        # Validate directories
        if not self.source_directory.exists():
            raise ValueError(f"Source directory does not exist: {self.source_directory}")
        
        if not self.target_directory.exists():
            raise ValueError(f"Target directory does not exist: {self.target_directory}")
        
        # Initialize scanner and folder manager
        self.scanner = PlanningArtifactsScanner(planning_directory=self.source_directory)
        
        if cortex_root:
            self.folder_manager = PlanFolderManager(cortex_root=cortex_root)
        else:
            # Use target_directory as root for testing
            self.folder_manager = PlanFolderManager(cortex_root=self.target_directory.parent)
        
        # Track migrations
        self._migration_log: Dict[str, MigrationResult] = {}
        
        logger.info(
            f"Initialized PlanningMigrationEngine: "
            f"source={self.source_directory}, target={self.target_directory}"
        )
    
    def discover_plans(self) -> PlanDiscovery:
        """
        Discover all plans in source directory.
        
        Returns:
            PlanDiscovery object with all discovered artifacts
        """
        logger.info("Discovering plans in source directory...")
        
        # Reinitialize scanner in case source_directory changed
        self.scanner = PlanningArtifactsScanner(planning_directory=self.source_directory)
        
        discovery = self.scanner.scan_directory()
        
        logger.info(
            f"Discovered {len(discovery.master_plans)} master plans, "
            f"{len(discovery.sub_plans)} sub-plans, "
            f"{len(discovery.trackers)} trackers, "
            f"{len(discovery.reports)} reports"
        )
        
        return discovery
    
    def migrate_plan(self, plan_id: str) -> MigrationResult:
        """
        Migrate a single plan and all related artifacts.
        
        Args:
            plan_id: ID of plan to migrate
            
        Returns:
            MigrationResult with status and details
        """
        logger.info(f"Migrating plan: {plan_id}")
        
        # Discover plans if not already done
        discovery = self.discover_plans()
        
        # Find master plan
        master_plan = None
        for plan in discovery.master_plans:
            if plan.plan_id == plan_id:
                master_plan = plan
                break
        
        if not master_plan:
            error_msg = f"Master plan not found: {plan_id}"
            logger.error(error_msg)
            result = MigrationResult(
                plan_id=plan_id,
                status=MigrationStatus.FAILED,
                message=error_msg
            )
            self._migration_log[plan_id] = result
            return result
        
        try:
            # Get related artifacts
            related_artifacts = discovery.plan_relationships.get(plan_id, [])
            
            # Determine status from master plan metadata
            status = master_plan.status or "active"
            
            # Create folder structure in target
            plan_folder = self.target_directory / status / plan_id
            plan_folder.mkdir(parents=True, exist_ok=True)
            
            # Create subfolders
            (plan_folder / "sub-plans").mkdir(exist_ok=True)
            (plan_folder / "artifacts").mkdir(exist_ok=True)
            (plan_folder / "reports").mkdir(exist_ok=True)
            (plan_folder / "tests").mkdir(exist_ok=True)
            (plan_folder / "checkpoints").mkdir(exist_ok=True)
            
            files_migrated = 0
            errors = []
            
            # Migrate master plan
            try:
                target_file = plan_folder / f"master-plan{master_plan.file_path.suffix}"
                shutil.copy2(master_plan.file_path, target_file)
                files_migrated += 1
                logger.info(f"Migrated master plan: {master_plan.file_path.name}")
            except Exception as e:
                error_msg = f"Failed to migrate master plan: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
            
            # Migrate related artifacts
            for artifact in related_artifacts:
                try:
                    if artifact.artifact_type == ArtifactType.SUB_PLAN:
                        target_file = plan_folder / "sub-plans" / artifact.file_path.name
                    elif artifact.artifact_type == ArtifactType.TRACKER:
                        target_file = plan_folder / "artifacts" / artifact.file_path.name
                    elif artifact.artifact_type == ArtifactType.REPORT:
                        target_file = plan_folder / "reports" / artifact.file_path.name
                    else:
                        target_file = plan_folder / "artifacts" / artifact.file_path.name
                    
                    shutil.copy2(artifact.file_path, target_file)
                    files_migrated += 1
                    logger.info(f"Migrated artifact: {artifact.file_path.name}")
                    
                except Exception as e:
                    error_msg = f"Failed to migrate {artifact.file_path.name}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            # Generate README
            try:
                self._generate_readme(plan_folder, master_plan, related_artifacts)
                logger.info("Generated README.md")
            except Exception as e:
                logger.warning(f"Failed to generate README: {e}")
            
            # Determine final status
            if errors:
                final_status = MigrationStatus.PARTIAL if files_migrated > 0 else MigrationStatus.FAILED
                message = f"Migrated {files_migrated} files with {len(errors)} errors"
            else:
                final_status = MigrationStatus.SUCCESS
                message = f"Successfully migrated {files_migrated} files"
            
            result = MigrationResult(
                plan_id=plan_id,
                status=final_status,
                message=message,
                files_migrated=files_migrated,
                errors=errors
            )
            
            self._migration_log[plan_id] = result
            logger.info(f"Migration complete: {plan_id} - {final_status.value}")
            
            return result
            
        except Exception as e:
            error_msg = f"Migration failed with exception: {e}"
            logger.error(error_msg)
            result = MigrationResult(
                plan_id=plan_id,
                status=MigrationStatus.FAILED,
                message=error_msg,
                errors=[str(e)]
            )
            self._migration_log[plan_id] = result
            return result
    
    def migrate_all(self) -> List[MigrationResult]:
        """
        Migrate all plans in source directory.
        
        Returns:
            List of MigrationResult for each plan
        """
        logger.info("Migrating all plans...")
        
        discovery = self.discover_plans()
        results = []
        
        for master_plan in discovery.master_plans:
            if master_plan.plan_id:
                result = self.migrate_plan(master_plan.plan_id)
                results.append(result)
        
        success_count = sum(1 for r in results if r.status == MigrationStatus.SUCCESS)
        logger.info(f"Migration complete: {success_count}/{len(results)} plans migrated successfully")
        
        return results
    
    def rollback_migration(self, plan_id: str) -> MigrationResult:
        """
        Rollback migration for a specific plan.
        
        Args:
            plan_id: ID of plan to rollback
            
        Returns:
            MigrationResult with rollback status
        """
        logger.info(f"Rolling back migration: {plan_id}")
        
        try:
            # Find plan folder in target directory (check all status folders)
            plan_folder = None
            for status_folder in ["active", "completed", "archived", "on-hold"]:
                potential_folder = self.target_directory / status_folder / plan_id
                if potential_folder.exists():
                    plan_folder = potential_folder
                    break
            
            if not plan_folder:
                return MigrationResult(
                    plan_id=plan_id,
                    status=MigrationStatus.FAILED,
                    message="Plan folder not found in target directory"
                )
            
            # Remove folder
            shutil.rmtree(plan_folder)
            logger.info(f"Removed plan folder: {plan_folder}")
            
            # Remove from migration log
            if plan_id in self._migration_log:
                del self._migration_log[plan_id]
            
            return MigrationResult(
                plan_id=plan_id,
                status=MigrationStatus.SUCCESS,
                message="Successfully rolled back migration"
            )
            
        except Exception as e:
            error_msg = f"Rollback failed: {e}"
            logger.error(error_msg)
            return MigrationResult(
                plan_id=plan_id,
                status=MigrationStatus.FAILED,
                message=error_msg,
                errors=[str(e)]
            )
    
    def rollback_all(self) -> List[MigrationResult]:
        """
        Rollback all migrations.
        
        Returns:
            List of MigrationResult for each rollback
        """
        logger.info("Rolling back all migrations...")
        
        results = []
        migrated_plans = list(self._migration_log.keys())
        
        for plan_id in migrated_plans:
            result = self.rollback_migration(plan_id)
            results.append(result)
        
        success_count = sum(1 for r in results if r.status == MigrationStatus.SUCCESS)
        logger.info(f"Rollback complete: {success_count}/{len(results)} plans rolled back successfully")
        
        return results
    
    def get_migration_status(self, plan_id: str) -> MigrationStatus:
        """
        Get migration status for a plan.
        
        Args:
            plan_id: ID of plan
            
        Returns:
            MigrationStatus enum value
        """
        if plan_id in self._migration_log:
            return self._migration_log[plan_id].status
        
        # Check if plan exists in target directory
        for status_folder in ["active", "completed", "archived", "on-hold"]:
            if (self.target_directory / status_folder / plan_id).exists():
                return MigrationStatus.SUCCESS
        
        return MigrationStatus.NOT_MIGRATED
    
    def list_migrated_plans(self) -> List[str]:
        """
        List all migrated plans.
        
        Returns:
            List of plan IDs
        """
        migrated = []
        
        # Check all status folders
        for status_folder in ["active", "completed", "archived", "on-hold"]:
            status_path = self.target_directory / status_folder
            if status_path.exists():
                for plan_folder in status_path.iterdir():
                    if plan_folder.is_dir():
                        migrated.append(plan_folder.name)
        
        return migrated
    
    def validate_migration(self, plan_id: str) -> bool:
        """
        Validate that a migration was successful.
        
        Args:
            plan_id: ID of plan to validate
            
        Returns:
            True if migration is valid, False otherwise
        """
        logger.info(f"Validating migration: {plan_id}")
        
        # Find plan folder
        plan_folder = None
        for status_folder in ["active", "completed", "archived", "on-hold"]:
            potential_folder = self.target_directory / status_folder / plan_id
            if potential_folder.exists():
                plan_folder = potential_folder
                break
        
        if not plan_folder:
            logger.warning(f"Plan folder not found: {plan_id}")
            return False
        
        # Check required files/folders
        required = ["sub-plans", "artifacts", "reports", "tests", "checkpoints"]
        for item in required:
            if not (plan_folder / item).exists():
                logger.warning(f"Missing required folder: {item}")
                return False
        
        # Check master plan file exists
        master_yaml = plan_folder / "master-plan.yaml"
        master_md = plan_folder / "master-plan.md"
        if not master_yaml.exists() and not master_md.exists():
            logger.warning("Master plan file not found")
            return False
        
        logger.info(f"Migration validated: {plan_id}")
        return True
    
    def validate_all_migrations(self) -> Dict[str, bool]:
        """
        Validate all migrations.
        
        Returns:
            Dict mapping plan_id to validation result
        """
        logger.info("Validating all migrations...")
        
        results = {}
        migrated_plans = self.list_migrated_plans()
        
        for plan_id in migrated_plans:
            results[plan_id] = self.validate_migration(plan_id)
        
        valid_count = sum(1 for v in results.values() if v)
        logger.info(f"Validation complete: {valid_count}/{len(results)} migrations valid")
        
        return results
    
    def _generate_readme(self, plan_folder: Path, master_plan: PlanMetadata, related_artifacts: List[PlanMetadata]):
        """
        Generate README.md for plan folder.
        
        Args:
            plan_folder: Path to plan folder
            master_plan: Master plan metadata
            related_artifacts: List of related artifact metadata
        """
        readme_path = plan_folder / "README.md"
        
        content = f"""# {master_plan.title or master_plan.plan_id}

**Plan ID:** {master_plan.plan_id}
**Status:** {master_plan.status or 'active'}
**Created:** {master_plan.created_date or 'N/A'}

## File Index

### Master Plan
- `master-plan{master_plan.file_path.suffix}` - Main plan document

### Sub-Plans ({len([a for a in related_artifacts if a.artifact_type == ArtifactType.SUB_PLAN])} files)
"""
        
        # List sub-plans
        for artifact in related_artifacts:
            if artifact.artifact_type == ArtifactType.SUB_PLAN:
                content += f"- `sub-plans/{artifact.file_path.name}` - {artifact.title or 'Sub-plan'}\n"
        
        # List trackers
        trackers = [a for a in related_artifacts if a.artifact_type == ArtifactType.TRACKER]
        if trackers:
            content += f"\n### Trackers ({len(trackers)} files)\n"
            for artifact in trackers:
                content += f"- `artifacts/{artifact.file_path.name}` - {artifact.title or 'Tracker'}\n"
        
        # List reports
        reports = [a for a in related_artifacts if a.artifact_type == ArtifactType.REPORT]
        if reports:
            content += f"\n### Reports ({len(reports)} files)\n"
            for artifact in reports:
                content += f"- `reports/{artifact.file_path.name}` - {artifact.title or 'Report'}\n"
        
        content += f"""
## Folder Structure

```
{plan_folder.name}/
├── README.md (this file)
├── master-plan{master_plan.file_path.suffix}
├── sub-plans/
├── artifacts/
├── reports/
├── tests/
└── checkpoints/
```

---
*Generated by CORTEX Planning Migration Engine*
"""
        
        readme_path.write_text(content, encoding='utf-8')
