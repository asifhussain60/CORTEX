"""
Cleanup Entry Point Module Orchestrator

Comprehensive file organization and cleanup orchestrator that:
1. Reorganizes misplaced files (tests, scripts, documentation)
2. Updates all code references to moved files
3. Cleans obsolete and duplicate files
4. Validates directory structure compliance

This orchestrator is designed to run as part of system maintenance to keep
the codebase organized and references up-to-date.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 3.8.1
"""

from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime
import logging
import json
import shutil
import re

from src.operations.base_operation_module import (
    BaseOperationModule, OperationResult, OperationStatus,
    OperationPhase, OperationModuleMetadata
)
from src.utils.progress_decorator import with_progress, yield_progress

logger = logging.getLogger(__name__)


class CleanupOrchestrator(BaseOperationModule):
    """
    Comprehensive cleanup and file organization orchestrator.
    
    Phases:
    1. File Organization - Move misplaced files to correct locations
    2. Reference Updates - Update all import/path references
    3. Obsolete Cleanup - Remove obsolete and duplicate files
    4. Validation - Verify organization and references
    """
    
    def __init__(self, project_root: Path = None):
        """Initialize cleanup orchestrator."""
        super().__init__()
        self.project_root = project_root or Path.cwd()
        self.metrics: Dict[str, Any] = {
            'files_moved': 0,
            'files_removed': 0,
            'references_updated': 0,
            'issues_fixed': 0,
            'space_freed_mb': 0.0,
            'moved_files': [],
            'updated_references': [],
            'removed_files': [],
            'errors': []
        }
        
        # Backup directory for safety
        self.backup_dir = self.project_root / 'cortex-brain' / 'backups' / 'cleanup'
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="cleanup",
            name="Cleanup Orchestrator",
            description="Comprehensive file organization, reference updates, and cleanup",
            phase=OperationPhase.PROCESSING,
            priority=80,
            version="3.8.1",
            author="Asif Hussain",
            tags=["orchestration", "cleanup", "organization", "maintenance"]
        )
    
    @with_progress(operation_name="Cleanup & Organization", threshold_seconds=3.0)
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute comprehensive cleanup and organization.
        
        Args:
            context: Operation context with optional 'dry_run' flag
            
        Returns:
            OperationResult with cleanup metrics and report
        """
        start_time = datetime.now()
        dry_run = context.get('dry_run', False)
        
        logger.info(f"🧹 Starting comprehensive cleanup and organization (dry_run={dry_run})")
        
        try:
            # Phase 1: File Organization
            yield_progress(1, 4, "Phase 1: Organizing files")
            self._organize_files(dry_run)
            
            # Phase 2: Reference Updates
            if not dry_run and self.metrics['files_moved'] > 0:
                yield_progress(2, 4, "Phase 2: Updating references")
                self._update_references()
            else:
                logger.info("Phase 2: Skipped (no files moved or dry run)")
            
            # Phase 3: Obsolete Cleanup
            yield_progress(3, 4, "Phase 3: Cleaning obsolete files")
            self._cleanup_obsolete(dry_run)
            
            # Phase 4: Validation
            yield_progress(4, 4, "Phase 4: Validating organization")
            validation = self._validate_organization()
            
            # Generate report
            report = self._generate_report(start_time, dry_run, validation)
            report_path = self._save_report(report, dry_run)
            
            success = len(self.metrics['errors']) == 0
            
            return OperationResult(
                success=success,
                status=OperationStatus.SUCCESS if success else OperationStatus.WARNING,
                message=self._format_summary(dry_run),
                data={
                    'metrics': self.metrics,
                    'report_path': str(report_path),
                    'validation': validation,
                    'dry_run': dry_run
                },
                errors=self.metrics['errors'],
                warnings=[],
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now(),
                formatted_header="🧹 Cleanup & Organization",
                formatted_footer=f"Report: {report_path.name}"
            )
        
        except Exception as e:
            logger.error(f"Cleanup failed: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Cleanup failed: {str(e)}",
                data={'metrics': self.metrics},
                errors=[str(e)],
                warnings=[],
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now(),
                formatted_header="🧹 Cleanup & Organization",
                formatted_footer="❌ Cleanup failed"
            )
    
    def _organize_files(self, dry_run: bool) -> None:
        """
        Phase 1: Organize misplaced files.
        
        Rules:
        - Test files (test_*.py) → tests/ directory
        - Script files in root → scripts/ directory  
        - Temp/scratch files → cleanup/remove
        """
        logger.info("📁 Phase 1: Organizing misplaced files")
        
        # Rule 1: Move root-level test files to tests/
        root_test_files = list(self.project_root.glob("test_*.py"))
        for test_file in root_test_files:
            # Skip if already processed or is a known utility
            if test_file.name in ['test_output.txt']:
                continue
            
            target_dir = self.project_root / 'tests' / 'integration'
            target_path = target_dir / test_file.name
            
            if dry_run:
                logger.info(f"[DRY RUN] Would move: {test_file.name} → tests/integration/")
            else:
                target_dir.mkdir(parents=True, exist_ok=True)
                self._move_file_with_backup(test_file, target_path)
            
            self.metrics['files_moved'] += 1
            self.metrics['moved_files'].append({
                'from': str(test_file.relative_to(self.project_root)),
                'to': str(target_path.relative_to(self.project_root))
            })
        
        # Rule 2: Move misplaced scripts to scripts/
        root_scripts = [
            f for f in self.project_root.glob("*.py")
            if f.stem not in ['setup', 'conftest', '__init__']
            and not f.stem.startswith('test_')
            and f.stem not in ['generate_tests', 'launch-dashboard']  # Known utilities
        ]
        
        for script_file in root_scripts:
            # Skip if it's a main entry point or configuration
            if script_file.name in ['setup.py', 'manage.py', 'wsgi.py', 'asgi.py']:
                continue
            
            target_dir = self.project_root / 'scripts' / 'utilities'
            target_path = target_dir / script_file.name
            
            if dry_run:
                logger.info(f"[DRY RUN] Would move: {script_file.name} → scripts/utilities/")
            else:
                target_dir.mkdir(parents=True, exist_ok=True)
                self._move_file_with_backup(script_file, target_path)
            
            self.metrics['files_moved'] += 1
            self.metrics['moved_files'].append({
                'from': str(script_file.relative_to(self.project_root)),
                'to': str(target_path.relative_to(self.project_root))
            })
        
        # Rule 3: Organize scattered documentation
        docs_to_move = []
        for doc_file in self.project_root.glob("*.md"):
            # Keep essential root docs
            if doc_file.name in ['README.md', 'LICENSE', 'CHANGELOG.md', 
                                 'CONTRIBUTING.md', 'MULTI-MACHINE-SETUP.md']:
                continue
            
            # Move to appropriate category in cortex-brain/documents/
            target_category = self._categorize_document(doc_file)
            target_dir = self.project_root / 'cortex-brain' / 'documents' / target_category
            target_path = target_dir / doc_file.name
            
            docs_to_move.append((doc_file, target_path))
        
        for doc_file, target_path in docs_to_move:
            if dry_run:
                logger.info(f"[DRY RUN] Would move: {doc_file.name} → {target_path.parent.name}/")
            else:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                self._move_file_with_backup(doc_file, target_path)
            
            self.metrics['files_moved'] += 1
            self.metrics['moved_files'].append({
                'from': str(doc_file.relative_to(self.project_root)),
                'to': str(target_path.relative_to(self.project_root))
            })
        
        logger.info(f"✓ Phase 1 complete: {self.metrics['files_moved']} files organized")
    
    def _categorize_document(self, doc_file: Path) -> str:
        """Categorize document into appropriate cortex-brain/documents/ folder."""
        name_lower = doc_file.stem.lower()
        
        if 'report' in name_lower or 'summary' in name_lower:
            return 'reports'
        elif 'analysis' in name_lower or 'review' in name_lower:
            return 'analysis'
        elif 'plan' in name_lower or 'proposal' in name_lower:
            return 'planning'
        elif 'investigation' in name_lower or 'debug' in name_lower:
            return 'investigations'
        elif 'guide' in name_lower or 'howto' in name_lower or 'tutorial' in name_lower:
            return 'implementation-guides'
        else:
            return 'summaries'
    
    def _update_references(self) -> None:
        """
        Phase 2: Update all import statements and path references.
        
        Updates:
        - Python imports (from/import statements)
        - File path references in strings
        - Test discovery patterns
        """
        logger.info("🔄 Phase 2: Updating code references")
        
        if not self.metrics['moved_files']:
            logger.info("No files moved - skipping reference updates")
            return
        
        # Build mapping of old → new paths
        path_mapping = {
            item['from']: item['to']
            for item in self.metrics['moved_files']
        }
        
        # Update references in all Python files
        python_files = list(self.project_root.glob("**/*.py"))
        
        for py_file in python_files:
            if '__pycache__' in str(py_file) or '.venv' in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                updated_content = content
                changes_made = False
                
                # Update import statements
                for old_path, new_path in path_mapping.items():
                    # Convert file paths to Python module paths
                    old_module = old_path.replace('/', '.').replace('\\', '.').replace('.py', '')
                    new_module = new_path.replace('/', '.').replace('\\', '.').replace('.py', '')
                    
                    # Pattern 1: from X import Y
                    old_import = f"from {old_module} import"
                    new_import = f"from {new_module} import"
                    if old_import in updated_content:
                        updated_content = updated_content.replace(old_import, new_import)
                        changes_made = True
                    
                    # Pattern 2: import X
                    old_import = f"import {old_module}"
                    new_import = f"import {new_module}"
                    if old_import in updated_content:
                        updated_content = updated_content.replace(old_import, new_import)
                        changes_made = True
                    
                    # Pattern 3: String path references
                    if old_path in updated_content:
                        updated_content = updated_content.replace(old_path, new_path)
                        changes_made = True
                
                if changes_made:
                    py_file.write_text(updated_content, encoding='utf-8')
                    self.metrics['references_updated'] += 1
                    self.metrics['updated_references'].append(str(py_file.relative_to(self.project_root)))
                    logger.info(f"Updated references in: {py_file.relative_to(self.project_root)}")
            
            except Exception as e:
                logger.warning(f"Could not update references in {py_file}: {e}")
                self.metrics['errors'].append(f"Reference update failed: {py_file.name} - {str(e)}")
        
        logger.info(f"✓ Phase 2 complete: {self.metrics['references_updated']} files updated")
    
    def _cleanup_obsolete(self, dry_run: bool) -> None:
        """
        Phase 3: Remove obsolete and duplicate files.
        
        Removes:
        - Duplicate test files
        - Obsolete backup files (*.backup, *.old, *.bak)
        - Empty directories
        - Temporary files
        """
        logger.info("🗑️  Phase 3: Cleaning obsolete files")
        
        # Find obsolete patterns
        obsolete_patterns = [
            '**/*.backup',
            '**/*.old',
            '**/*.bak',
            '**/*.tmp',
            '**/*~',
            '**/.DS_Store',
            '**/Thumbs.db'
        ]
        
        for pattern in obsolete_patterns:
            obsolete_files = list(self.project_root.glob(pattern))
            
            for obsolete_file in obsolete_files:
                # Skip if in protected directories
                if any(protected in str(obsolete_file) for protected in ['.git', '.venv', 'node_modules']):
                    continue
                
                size_mb = obsolete_file.stat().st_size / (1024 * 1024)
                
                if dry_run:
                    logger.info(f"[DRY RUN] Would remove: {obsolete_file.relative_to(self.project_root)}")
                else:
                    obsolete_file.unlink()
                    logger.info(f"Removed: {obsolete_file.relative_to(self.project_root)}")
                
                self.metrics['files_removed'] += 1
                self.metrics['space_freed_mb'] += size_mb
                self.metrics['removed_files'].append(str(obsolete_file.relative_to(self.project_root)))
        
        # Clean empty directories
        self._remove_empty_directories(dry_run)
        
        logger.info(f"✓ Phase 3 complete: {self.metrics['files_removed']} obsolete files removed")
    
    def _remove_empty_directories(self, dry_run: bool) -> None:
        """Remove empty directories (except protected ones)."""
        protected_dirs = {'.git', '.venv', 'node_modules', '__pycache__', 'cortex-brain'}
        
        for dirpath in list(self.project_root.rglob('*')):
            if not dirpath.is_dir():
                continue
            
            # Skip protected directories
            if any(protected in str(dirpath) for protected in protected_dirs):
                continue
            
            # Check if empty
            try:
                if not any(dirpath.iterdir()):
                    if dry_run:
                        logger.info(f"[DRY RUN] Would remove empty directory: {dirpath.relative_to(self.project_root)}")
                    else:
                        dirpath.rmdir()
                        logger.info(f"Removed empty directory: {dirpath.relative_to(self.project_root)}")
            except (OSError, PermissionError):
                pass
    
    def _validate_organization(self) -> Dict[str, Any]:
        """
        Phase 4: Validate file organization.
        
        Checks:
        - No test files in root
        - No misplaced scripts
        - Directory structure compliance
        """
        logger.info("✅ Phase 4: Validating organization")
        
        validation = {
            'passed': True,
            'issues': []
        }
        
        # Check 1: No test files in root
        root_tests = list(self.project_root.glob("test_*.py"))
        if root_tests:
            validation['passed'] = False
            validation['issues'].append(f"{len(root_tests)} test files still in root directory")
        
        # Check 2: No misplaced documentation
        root_docs = [
            f for f in self.project_root.glob("*.md")
            if f.name not in ['README.md', 'LICENSE', 'CHANGELOG.md', 
                             'CONTRIBUTING.md', 'MULTI-MACHINE-SETUP.md']
        ]
        if root_docs:
            validation['passed'] = False
            validation['issues'].append(f"{len(root_docs)} documentation files in root (should be in cortex-brain/documents/)")
        
        # Check 3: Directory structure
        required_dirs = ['src', 'tests', 'cortex-brain', 'docs']
        for req_dir in required_dirs:
            if not (self.project_root / req_dir).exists():
                validation['passed'] = False
                validation['issues'].append(f"Missing required directory: {req_dir}")
        
        if validation['passed']:
            logger.info("✓ Validation passed: File organization compliant")
        else:
            logger.warning(f"⚠️  Validation found {len(validation['issues'])} issues")
            for issue in validation['issues']:
                logger.warning(f"  - {issue}")
        
        return validation
    
    def _move_file_with_backup(self, source: Path, target: Path) -> None:
        """Move file with backup for safety."""
        try:
            # Create backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = self.backup_dir / timestamp / source.name
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, backup_path)
            
            # Move to target
            shutil.move(str(source), str(target))
            logger.info(f"Moved: {source.name} → {target.relative_to(self.project_root)}")
            
            self.metrics['issues_fixed'] += 1
        
        except Exception as e:
            logger.error(f"Failed to move {source}: {e}")
            self.metrics['errors'].append(f"Move failed: {source.name} - {str(e)}")
    
    def _format_summary(self, dry_run: bool) -> str:
        """Format operation summary message."""
        prefix = "[DRY RUN] " if dry_run else ""
        return (
            f"{prefix}Cleanup complete: "
            f"{self.metrics['files_moved']} moved, "
            f"{self.metrics['files_removed']} removed, "
            f"{self.metrics['references_updated']} references updated"
        )
    
    def _generate_report(self, start_time: datetime, dry_run: bool, 
                        validation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cleanup report."""
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'dry_run': dry_run,
            'summary': {
                'files_moved': self.metrics['files_moved'],
                'files_removed': self.metrics['files_removed'],
                'references_updated': self.metrics['references_updated'],
                'issues_fixed': self.metrics['issues_fixed'],
                'space_freed_mb': round(self.metrics['space_freed_mb'], 2),
                'errors': len(self.metrics['errors'])
            },
            'moved_files': self.metrics['moved_files'],
            'removed_files': self.metrics['removed_files'],
            'updated_references': self.metrics['updated_references'],
            'validation': validation,
            'errors': self.metrics['errors']
        }
    
    def _save_report(self, report: Dict[str, Any], dry_run: bool) -> Path:
        """Save cleanup report."""
        reports_dir = self.project_root / 'cortex-brain' / 'documents' / 'reports'
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        prefix = 'cleanup-dryrun' if dry_run else 'cleanup'
        report_path = reports_dir / f'{prefix}-{timestamp}.json'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Report saved: {report_path}")
        return report_path
