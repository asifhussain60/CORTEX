"""
Planning Document Migrator - Phase 2 Implementation
Migrates planning documents to status-based subdirectories

Purpose:
- Organize 100+ planning documents by status
- Prevent data loss with backup capability
- Detect status from document frontmatter
- Support dry-run mode for validation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class PlanningDocumentMigrator:
    """
    Migrates planning documents from flat structure to status-based subdirectories.
    
    Directory Structure:
        cortex-brain/documents/planning/
        ├── active/          (in-progress, proposed plans)
        ├── approved/        (approved but not started)
        ├── completed/       (finished plans)
        └── deprecated/      (cancelled or superseded)
    
    Status Detection:
        Scans document frontmatter for "**Status:** <status>" pattern
        Defaults to "active" if no status found
    
    Safety Features:
        - Dry-run mode (preview without moving)
        - Automatic backup before migration
        - Validation checks after migration
        - Preserves existing subdirectories (ado/, features/, enhancements/)
    """
    
    # Valid status values
    VALID_STATUSES = {
        'in-progress': 'active',
        'proposed': 'active',
        'approved': 'approved',
        'completed': 'completed',
        'cancelled': 'deprecated',
        'deprecated': 'deprecated',
        'blocked': 'active',  # Blocked plans stay active
    }
    
    def __init__(self, cortex_root: str):
        """
        Initialize migrator.
        
        Args:
            cortex_root: Path to CORTEX root directory
        """
        self.cortex_root = Path(cortex_root)
        self.brain_path = self.cortex_root / "cortex-brain"
        self.planning_path = self.brain_path / "documents" / "planning"
        
        # Status directories
        self.status_dirs = {
            'active': self.planning_path / "active",
            'approved': self.planning_path / "approved",
            'completed': self.planning_path / "completed",
            'deprecated': self.planning_path / "deprecated"
        }
        
        # Ensure status directories exist
        for status_dir in self.status_dirs.values():
            status_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized PlanningDocumentMigrator at {cortex_root}")
    
    def migrate_documents(
        self, 
        dry_run: bool = True, 
        create_backup: bool = True
    ) -> Dict:
        """
        Migrate planning documents to status-based directories.
        
        Args:
            dry_run: If True, preview changes without moving files
            create_backup: If True, create backup before migration
        
        Returns:
            Dictionary with migration results:
            {
                'success': bool,
                'dry_run': bool,
                'migrated_count': int,
                'failed_count': int,
                'backup_path': Optional[str],
                'migrations': List[Dict],
                'errors': List[str]
            }
        """
        logger.info(f"Starting migration (dry_run={dry_run}, backup={create_backup})")
        
        result = {
            'success': False,
            'dry_run': dry_run,
            'migrated_count': 0,
            'failed_count': 0,
            'backup_path': None,
            'migrations': [],
            'errors': []
        }
        
        try:
            # Step 1: Find all planning documents in root
            plans = self._find_plans_in_root()
            logger.info(f"Found {len(plans)} planning documents in root")
            
            if len(plans) == 0:
                logger.info("No plans to migrate")
                result['success'] = True
                return result
            
            # Step 2: Create backup if requested
            if create_backup and not dry_run:
                backup_path = self._create_backup(plans)
                result['backup_path'] = str(backup_path)
                logger.info(f"Created backup at {backup_path}")
            
            # Step 3: Process each plan
            for plan_path in plans:
                try:
                    # Detect status
                    status = self._detect_plan_status(plan_path)
                    target_dir = self.status_dirs.get(status, self.status_dirs['active'])
                    target_path = target_dir / plan_path.name
                    
                    migration_record = {
                        'source': str(plan_path),
                        'target': str(target_path),
                        'status': status,
                        'dry_run': dry_run
                    }
                    
                    # Move file (unless dry run)
                    if not dry_run:
                        shutil.move(str(plan_path), str(target_path))
                        logger.debug(f"Moved {plan_path.name} to {status}/")
                    else:
                        logger.debug(f"[DRY RUN] Would move {plan_path.name} to {status}/")
                    
                    result['migrations'].append(migration_record)
                    result['migrated_count'] += 1
                    
                except Exception as e:
                    error_msg = f"Failed to migrate {plan_path.name}: {str(e)}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
                    result['failed_count'] += 1
            
            # Step 4: Validation (only if not dry run)
            if not dry_run:
                validation_ok = self._validate_migration(plans, result['migrations'])
                result['success'] = validation_ok and result['failed_count'] == 0
            else:
                result['success'] = True
            
            logger.info(f"Migration complete: {result['migrated_count']} migrated, {result['failed_count']} failed")
            
        except Exception as e:
            error_msg = f"Migration failed: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
            result['success'] = False
        
        return result
    
    def _find_plans_in_root(self) -> List[Path]:
        """
        Find all planning documents in planning root directory.
        
        Excludes:
        - Files in subdirectories (ado/, features/, enhancements/, active/, approved/, etc.)
        - Non-markdown files
        - Index files
        
        Returns:
            List of Path objects for planning documents
        """
        plans = []
        
        for item in self.planning_path.iterdir():
            # Skip directories
            if item.is_dir():
                continue
            
            # Only process markdown files
            if item.suffix != '.md':
                continue
            
            # Skip index/readme files
            if item.name.lower() in ['index.md', 'readme.md']:
                continue
            
            # Include if it looks like a planning document
            if item.name.startswith('PLAN-') or item.name.startswith('ADO-') or item.name.startswith('CORTEX-'):
                plans.append(item)
        
        return sorted(plans)
    
    def _detect_plan_status(self, plan_path: Path) -> str:
        """
        Detect plan status from document frontmatter.
        
        Args:
            plan_path: Path to planning document
        
        Returns:
            Status directory name ('active', 'approved', 'completed', 'deprecated')
        """
        try:
            content = plan_path.read_text(encoding='utf-8')
            return self._detect_plan_status_from_content(content)
        except Exception as e:
            logger.warning(f"Could not read {plan_path.name}, defaulting to 'active': {e}")
            return 'active'
    
    def _detect_plan_status_from_content(self, content: str) -> str:
        """
        Detect status from document content.
        
        Args:
            content: Document content
        
        Returns:
            Status directory name
        """
        # Try multiple patterns for flexibility
        patterns = [
            r'\*\*Status:\*\*\s*([a-zA-Z-]+)',  # **Status:** value (Markdown bold)
            r'\*\*Status\*\*:\s*([a-zA-Z-]+)',  # **Status**: value
            r'Status:\s*([a-zA-Z-]+)',          # Status: value (plain)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                status_value = match.group(1).strip().lower()
                
                # Map to directory name
                directory = self.VALID_STATUSES.get(status_value, 'active')
                logger.debug(f"Detected status '{status_value}' -> directory '{directory}'")
                return directory
        
        # Default to active if no status found
        logger.debug("No status found, defaulting to 'active'")
        return 'active'
    
    def _create_backup(self, plans: List[Path]) -> Path:
        """
        Create backup of planning documents before migration.
        
        Args:
            plans: List of plan paths to backup
        
        Returns:
            Path to backup directory
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_dir = self.planning_path / f"backup-{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        for plan_path in plans:
            backup_path = backup_dir / plan_path.name
            shutil.copy2(str(plan_path), str(backup_path))
        
        logger.info(f"Backed up {len(plans)} documents to {backup_dir}")
        return backup_dir
    
    def _validate_migration(self, original_plans: List[Path], migrations: List[Dict]) -> bool:
        """
        Validate migration completed successfully.
        
        Args:
            original_plans: List of original plan paths
            migrations: List of migration records
        
        Returns:
            True if validation passed
        """
        # Check that all original files were moved
        if len(original_plans) != len(migrations):
            logger.error(f"Migration count mismatch: {len(original_plans)} original, {len(migrations)} migrated")
            return False
        
        # Check that no files remain in root
        remaining = self._find_plans_in_root()
        if len(remaining) > 0:
            logger.error(f"Found {len(remaining)} documents still in root after migration")
            return False
        
        # Check that all target files exist
        for migration in migrations:
            target_path = Path(migration['target'])
            if not target_path.exists():
                logger.error(f"Migration target does not exist: {target_path}")
                return False
        
        logger.info("Migration validation passed")
        return True
    
    def generate_migration_report(self, result: Dict) -> str:
        """
        Generate human-readable migration report.
        
        Args:
            result: Migration result dictionary
        
        Returns:
            Markdown-formatted report
        """
        report = []
        report.append("# 🧠 CORTEX Planning Document Migration Report")
        report.append(f"**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX\n")
        report.append("---\n")
        
        report.append("## Summary\n")
        report.append(f"- **Mode:** {'DRY RUN' if result['dry_run'] else 'LIVE MIGRATION'}")
        report.append(f"- **Success:** {'✅ YES' if result['success'] else '❌ NO'}")
        report.append(f"- **Migrated:** {result['migrated_count']} documents")
        report.append(f"- **Failed:** {result['failed_count']} documents")
        
        if result['backup_path']:
            report.append(f"- **Backup:** {result['backup_path']}")
        
        report.append("")
        
        # Migration details
        if result['migrations']:
            report.append("## Migrations\n")
            
            # Group by status
            by_status = {}
            for migration in result['migrations']:
                status = migration['status']
                if status not in by_status:
                    by_status[status] = []
                by_status[status].append(migration)
            
            for status, migrations in sorted(by_status.items()):
                report.append(f"### {status.title()} ({len(migrations)} documents)\n")
                for migration in migrations:
                    source_name = Path(migration['source']).name
                    report.append(f"- {source_name}")
                report.append("")
        
        # Errors
        if result['errors']:
            report.append("## Errors\n")
            for error in result['errors']:
                report.append(f"- ❌ {error}")
            report.append("")
        
        return "\n".join(report)
