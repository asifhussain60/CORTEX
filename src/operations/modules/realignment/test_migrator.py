"""
Test Migrator for CORTEX Align Orchestrator v2.0

This module automatically migrates test files from deprecated orchestrator
imports to new utility/module imports. Includes:
- Import rewriting (orchestrators -> operations.modules)
- Class name updates (XyzOrchestrator -> XyzUtility)
- Instantiation pattern fixes
- Dry-run mode with diff preview
- Automatic backup creation

Author: Asif Hussain
Date: December 3, 2025
Version: 1.0.0
"""

import re
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
import difflib

logger = logging.getLogger(__name__)


@dataclass
class MigrationChange:
    """Represents a single migration change."""
    line_number: int
    original: str
    replacement: str
    change_type: str  # 'import', 'class_name', 'instantiation'


@dataclass
class MigrationResult:
    """Result of migrating a file."""
    file: Path
    success: bool
    changes_made: int = 0
    changes: List[MigrationChange] = field(default_factory=list)
    backup_path: Optional[Path] = None
    error: Optional[str] = None
    diff: Optional[str] = None
    
    @property
    def has_changes(self) -> bool:
        """Check if any changes were made."""
        return self.changes_made > 0


@dataclass
class BatchMigrationResult:
    """Result of batch migration."""
    total_files: int
    successful: int
    failed: int
    total_changes: int
    results: List[MigrationResult] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.successful / self.total_files) * 100


class TestMigrator:
    """Automatically migrates test files from orchestrators to utilities."""
    
    # Import mapping patterns
    IMPORT_PATTERNS = [
        # from src.orchestrators.xyz_orchestrator import XyzOrchestrator
        (
            r'from\s+src\.orchestrators\.(\w+)_orchestrator\s+import\s+(\w+)',
            r'from src.operations.modules.\1.\1_utility import \2'
        ),
        # from orchestrators.xyz_orchestrator import XyzOrchestrator
        (
            r'from\s+orchestrators\.(\w+)_orchestrator\s+import\s+(\w+)',
            r'from src.operations.modules.\1.\1_utility import \2'
        ),
        # import src.orchestrators.xyz_orchestrator
        (
            r'import\s+src\.orchestrators\.(\w+)_orchestrator',
            r'import src.operations.modules.\1.\1_utility'
        ),
        # import orchestrators.xyz_orchestrator
        (
            r'import\s+orchestrators\.(\w+)_orchestrator',
            r'import src.operations.modules.\1.\1_utility'
        ),
    ]
    
    # Class name patterns (XyzOrchestrator -> XyzUtility)
    CLASS_NAME_PATTERNS = [
        (r'\b(\w+)Orchestrator\b', r'\1Utility'),
    ]
    
    def __init__(self, project_root: Optional[Path] = None, create_backups: bool = True):
        """
        Initialize test migrator.
        
        Args:
            project_root: Path to CORTEX project root. If None, auto-detects.
            create_backups: Whether to create backups before migration
        """
        self.project_root = project_root or self._detect_project_root()
        self.create_backups = create_backups
        self.backup_dir = self.project_root / "cortex-brain" / "backups" / "migrations"
    
    def _detect_project_root(self) -> Path:
        """Auto-detect CORTEX project root."""
        current = Path.cwd()
        
        if (current / "cortex-operations.yaml").exists():
            return current
        
        for parent in current.parents:
            if (parent / "cortex-operations.yaml").exists():
                return parent
        
        raise FileNotFoundError("Cannot detect CORTEX project root")
    
    def _create_backup(self, file_path: Path) -> Path:
        """
        Create backup of file before migration.
        
        Args:
            file_path: Path to file to backup
        
        Returns:
            Path to backup file
        """
        if not self.create_backups:
            return None
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name
        
        # Copy file to backup
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        
        return backup_path
    
    def migrate_imports(self, content: str) -> Tuple[str, List[MigrationChange]]:
        """
        Migrate deprecated orchestrator imports to utility imports.
        
        Args:
            content: File content
        
        Returns:
            Tuple of (migrated content, list of changes)
        """
        changes = []
        migrated = content
        lines = content.split('\n')
        
        for pattern, replacement in self.IMPORT_PATTERNS:
            matches = list(re.finditer(pattern, migrated, re.MULTILINE))
            
            for match in reversed(matches):  # Reverse to maintain line numbers
                original = match.group(0)
                
                # Apply replacement
                new_import = re.sub(pattern, replacement, original)
                
                # Get line number
                line_number = migrated[:match.start()].count('\n') + 1
                
                # Replace in content
                migrated = migrated[:match.start()] + new_import + migrated[match.end():]
                
                changes.append(MigrationChange(
                    line_number=line_number,
                    original=original,
                    replacement=new_import,
                    change_type='import'
                ))
                
                logger.debug(f"Migrated import at line {line_number}: {original} -> {new_import}")
        
        return migrated, changes
    
    def migrate_class_names(self, content: str) -> Tuple[str, List[MigrationChange]]:
        """
        Migrate class names from XyzOrchestrator to XyzUtility.
        
        Args:
            content: File content
        
        Returns:
            Tuple of (migrated content, list of changes)
        """
        changes = []
        migrated = content
        
        for pattern, replacement in self.CLASS_NAME_PATTERNS:
            matches = list(re.finditer(pattern, migrated))
            
            for match in reversed(matches):
                original = match.group(0)
                
                # Skip if already a utility
                if 'Utility' in original:
                    continue
                
                # Apply replacement
                new_name = re.sub(pattern, replacement, original)
                
                # Get line number
                line_number = migrated[:match.start()].count('\n') + 1
                
                # Replace in content
                migrated = migrated[:match.start()] + new_name + migrated[match.end():]
                
                changes.append(MigrationChange(
                    line_number=line_number,
                    original=original,
                    replacement=new_name,
                    change_type='class_name'
                ))
                
                logger.debug(f"Migrated class name at line {line_number}: {original} -> {new_name}")
        
        return migrated, changes
    
    def migrate_instantiation(self, content: str) -> Tuple[str, List[MigrationChange]]:
        """
        Migrate instantiation patterns (constructor calls, etc.).
        
        Args:
            content: File content
        
        Returns:
            Tuple of (migrated content, list of changes)
        """
        changes = []
        migrated = content
        
        # Pattern: orchestrator = XyzOrchestrator(...)
        pattern = r'(\w+)\s*=\s*(\w+)Orchestrator\('
        matches = list(re.finditer(pattern, migrated))
        
        for match in reversed(matches):
            original = match.group(0)
            var_name = match.group(1)
            class_base = match.group(2)
            
            # Skip if already a utility
            if 'Utility' in original:
                continue
            
            # Replace Orchestrator with Utility
            new_instantiation = f"{var_name} = {class_base}Utility("
            
            # Get line number
            line_number = migrated[:match.start()].count('\n') + 1
            
            # Replace in content
            migrated = migrated[:match.start()] + new_instantiation + migrated[match.end():]
            
            changes.append(MigrationChange(
                line_number=line_number,
                original=original,
                replacement=new_instantiation,
                change_type='instantiation'
            ))
            
            logger.debug(f"Migrated instantiation at line {line_number}: {original} -> {new_instantiation}")
        
        return migrated, changes
    
    def generate_diff(self, original: str, migrated: str, filename: str) -> str:
        """
        Generate unified diff between original and migrated content.
        
        Args:
            original: Original content
            migrated: Migrated content
            filename: Name of file (for diff header)
        
        Returns:
            Unified diff string
        """
        original_lines = original.splitlines(keepends=True)
        migrated_lines = migrated.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines,
            migrated_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
            lineterm=''
        )
        
        return ''.join(diff)
    
    def migrate_file(self, file_path: Path, dry_run: bool = False) -> MigrationResult:
        """
        Migrate a single file.
        
        Args:
            file_path: Path to file to migrate
            dry_run: If True, don't write changes (preview only)
        
        Returns:
            MigrationResult with details
        """
        try:
            # Read original content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Apply migrations
            migrated_content = original_content
            all_changes = []
            
            # 1. Migrate imports
            migrated_content, import_changes = self.migrate_imports(migrated_content)
            all_changes.extend(import_changes)
            
            # 2. Migrate class names
            migrated_content, class_changes = self.migrate_class_names(migrated_content)
            all_changes.extend(class_changes)
            
            # 3. Migrate instantiation
            migrated_content, inst_changes = self.migrate_instantiation(migrated_content)
            all_changes.extend(inst_changes)
            
            # Generate diff
            diff = self.generate_diff(original_content, migrated_content, file_path.name)
            
            # Create backup and write changes (if not dry run)
            backup_path = None
            if not dry_run and all_changes:
                backup_path = self._create_backup(file_path)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(migrated_content)
                
                logger.info(f"Migrated {file_path} ({len(all_changes)} changes)")
            
            return MigrationResult(
                file=file_path,
                success=True,
                changes_made=len(all_changes),
                changes=all_changes,
                backup_path=backup_path,
                diff=diff if all_changes else None
            )
        
        except Exception as e:
            logger.error(f"Failed to migrate {file_path}: {e}", exc_info=True)
            return MigrationResult(
                file=file_path,
                success=False,
                error=str(e)
            )
    
    def migrate_batch(self, file_paths: List[Path], dry_run: bool = False) -> BatchMigrationResult:
        """
        Migrate multiple files.
        
        Args:
            file_paths: List of file paths to migrate
            dry_run: If True, preview changes without writing
        
        Returns:
            BatchMigrationResult with summary
        """
        results = []
        total_changes = 0
        successful = 0
        failed = 0
        
        logger.info(f"Starting batch migration of {len(file_paths)} files (dry_run={dry_run})")
        
        for file_path in file_paths:
            result = self.migrate_file(file_path, dry_run=dry_run)
            results.append(result)
            
            if result.success:
                successful += 1
                total_changes += result.changes_made
            else:
                failed += 1
        
        batch_result = BatchMigrationResult(
            total_files=len(file_paths),
            successful=successful,
            failed=failed,
            total_changes=total_changes,
            results=results
        )
        
        logger.info(
            f"Batch migration complete: {successful}/{len(file_paths)} successful, "
            f"{total_changes} total changes"
        )
        
        return batch_result
    
    def generate_report(self, result: BatchMigrationResult, dry_run: bool = False) -> str:
        """
        Generate formatted report from batch migration result.
        
        Args:
            result: BatchMigrationResult to format
            dry_run: Whether this was a dry run
        
        Returns:
            Formatted markdown report
        """
        mode = "DRY RUN" if dry_run else "EXECUTED"
        
        report_lines = [
            f"# Test Migration Report ({mode})",
            "",
            f"**Total Files:** {result.total_files}",
            f"**Successful:** {result.successful}",
            f"**Failed:** {result.failed}",
            f"**Total Changes:** {result.total_changes}",
            f"**Success Rate:** {result.success_rate:.1f}%",
            "",
        ]
        
        if result.successful > 0:
            report_lines.extend([
                "## ✅ Successfully Migrated Files",
                ""
            ])
            
            for res in result.results:
                if res.success and res.has_changes:
                    relative_path = res.file.relative_to(self.project_root)
                    report_lines.append(
                        f"- `{relative_path}` ({res.changes_made} changes)"
                    )
                    
                    # Group changes by type
                    import_count = sum(1 for c in res.changes if c.change_type == 'import')
                    class_count = sum(1 for c in res.changes if c.change_type == 'class_name')
                    inst_count = sum(1 for c in res.changes if c.change_type == 'instantiation')
                    
                    details = []
                    if import_count > 0:
                        details.append(f"{import_count} imports")
                    if class_count > 0:
                        details.append(f"{class_count} class names")
                    if inst_count > 0:
                        details.append(f"{inst_count} instantiations")
                    
                    if details:
                        report_lines.append(f"  - {', '.join(details)}")
            
            report_lines.append("")
        
        # Files with no changes
        no_changes = [r for r in result.results if r.success and not r.has_changes]
        if no_changes:
            report_lines.extend([
                "## ℹ️ No Changes Required",
                "",
                f"{len(no_changes)} files already up-to-date",
                ""
            ])
        
        if result.failed > 0:
            report_lines.extend([
                "## ❌ Failed Migrations",
                ""
            ])
            
            for res in result.results:
                if not res.success:
                    relative_path = res.file.relative_to(self.project_root)
                    report_lines.append(f"- `{relative_path}`")
                    if res.error:
                        report_lines.append(f"  - Error: {res.error}")
            
            report_lines.append("")
        
        if dry_run:
            report_lines.extend([
                "## 🔧 Next Steps",
                "",
                "This was a dry run. To apply changes:",
                "1. Review the changes above",
                "2. Run `align migrate-tests --execute` to apply migrations",
                "3. Run tests to verify migrations: `pytest tests/`",
                ""
            ])
        else:
            report_lines.extend([
                "## 🔧 Next Steps",
                "",
                "1. Run tests to verify migrations: `pytest tests/`",
                "2. Review git diff: `git diff`",
                "3. Commit changes if tests pass",
                f"4. Backups available in: `{self.backup_dir.relative_to(self.project_root)}`",
                ""
            ])
        
        return "\n".join(report_lines)


def main():
    """CLI entry point for test migration."""
    import sys
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description="Migrate test files from orchestrators to utilities")
    parser.add_argument(
        'files',
        nargs='*',
        help='Specific files to migrate (default: all files with deprecated imports)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip backup creation'
    )
    
    args = parser.parse_args()
    
    try:
        migrator = TestMigrator(create_backups=not args.no_backup)
        
        # Determine files to migrate
        if args.files:
            file_paths = [Path(f) for f in args.files]
        else:
            # Find all files with deprecated imports
            from src.operations.modules.realignment.obsolete_code_detector import ObsoleteCodeDetector
            detector = ObsoleteCodeDetector()
            analyses = detector.scan_all_for_deprecated_imports()
            file_paths = [a.file for a in analyses]
        
        if not file_paths:
            print("No files to migrate")
            sys.exit(0)
        
        # Migrate files
        result = migrator.migrate_batch(file_paths, dry_run=args.dry_run)
        
        # Print report
        print(migrator.generate_report(result, dry_run=args.dry_run))
        
        # Exit with appropriate code
        sys.exit(0 if result.failed == 0 else 1)
    
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
