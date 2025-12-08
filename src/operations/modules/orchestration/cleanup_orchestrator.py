"""
Cleanup Entry Point Module Orchestrator

Comprehensive file organization and cleanup orchestrator that:
0. Analyzes duplicate functionality (with safety detection)
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
import sys

# Add scripts/utilities to path for duplicate analyzer
scripts_path = Path(__file__).resolve().parents[4] / 'scripts' / 'utilities'
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

from src.operations.base_operation_module import (
    BaseOperationModule, OperationResult, OperationStatus,
    OperationPhase, OperationModuleMetadata
)
from src.utils.progress_decorator import with_progress, yield_progress

# Import duplicate analyzer (conditional - may not exist in all environments)
try:
    from analyze_duplicates_v2 import DuplicateFunctionalityAnalyzer
    DUPLICATE_ANALYZER_AVAILABLE = True
except ImportError:
    DUPLICATE_ANALYZER_AVAILABLE = False
    logging.warning("Duplicate analyzer not available - skipping duplicate detection phase")

logger = logging.getLogger(__name__)


class CleanupOrchestrator(BaseOperationModule):
    """
    Comprehensive cleanup and file organization orchestrator.
    
    Phases:
    0. Duplicate Analysis - Detect and analyze duplicate functionality (safety-enhanced)
    1. File Organization - Move misplaced files to correct locations
    2. Reference Updates - Update all import/path references
    3. Obsolete Cleanup - Remove obsolete and duplicate files (uses Phase 0 analysis)
    4. Validation - Verify organization and references
    """
    
    def __init__(self, project_root: Path = None):
        """Initialize cleanup orchestrator."""
        super().__init__()
        self.project_root = project_root or Path.cwd()
        self.duplicate_report: Dict[str, Any] = None  # Stores Phase 0 analysis
        self.metrics: Dict[str, Any] = {
            'files_moved': 0,
            'files_removed': 0,
            'references_updated': 0,
            'issues_fixed': 0,
            'space_freed_mb': 0.0,
            'duplicates_found': 0,
            'safe_to_delete': 0,
            'needs_review': 0,
            'duplicates_deleted': 0,
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
            description="Duplicate analysis, file organization, reference updates, and cleanup",
            phase=OperationPhase.PROCESSING,
            priority=80,
            version="3.8.1",
            author="Asif Hussain",
            tags=["orchestration", "cleanup", "organization", "maintenance", "duplicate-detection"]
        )
    
    @with_progress(operation_name="Cleanup & Organization", threshold_seconds=3.0)
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute comprehensive cleanup and organization.
        
        Args:
            context: Operation context with optional flags:
                - 'dry_run': bool - Preview changes without executing
                - 'skip_duplicate_analysis': bool - Skip Phase 0 (faster)
                - 'auto_delete_archived': bool - Auto-delete archived duplicates (Phase 3)
            
        Returns:
            OperationResult with cleanup metrics and report
        """
        start_time = datetime.now()
        dry_run = context.get('dry_run', False)
        skip_duplicate_analysis = context.get('skip_duplicate_analysis', False)
        auto_delete_archived = context.get('auto_delete_archived', False)
        
        total_phases = 5 if not skip_duplicate_analysis and DUPLICATE_ANALYZER_AVAILABLE else 4
        current_phase = 0
        
        logger.info(f"🧹 Starting comprehensive cleanup (dry_run={dry_run}, phases={total_phases})")
        
        try:
            # Phase 0: Duplicate Analysis (optional, can be skipped for speed)
            if not skip_duplicate_analysis and DUPLICATE_ANALYZER_AVAILABLE:
                current_phase += 1
                yield_progress(current_phase, total_phases, "Phase 0: Analyzing duplicates")
                self._analyze_duplicates()
            else:
                if skip_duplicate_analysis:
                    logger.info("Phase 0: Skipped (skip_duplicate_analysis=True)")
                else:
                    logger.info("Phase 0: Skipped (analyzer not available)")
            
            # Phase 1: File Organization
            current_phase += 1
            yield_progress(current_phase, total_phases, "Phase 1: Organizing files")
            self._organize_files(dry_run)
            
            # Phase 2: Reference Updates
            if not dry_run and self.metrics['files_moved'] > 0:
                current_phase += 1
                yield_progress(current_phase, total_phases, "Phase 2: Updating references")
                self._update_references()
            else:
                logger.info("Phase 2: Skipped (no files moved or dry run)")
                current_phase += 1
            
            # Phase 3: Obsolete Cleanup (enhanced with duplicate analysis)
            current_phase += 1
            yield_progress(current_phase, total_phases, "Phase 3: Cleaning obsolete files")
            self._cleanup_obsolete(dry_run, auto_delete_archived)
            
            # Phase 4: Validation
            current_phase += 1
            yield_progress(current_phase, total_phases, "Phase 4: Validating organization")
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
                    'duplicate_report': self.duplicate_report,
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
    
    def _analyze_duplicates(self) -> None:
        """
        Phase 0: Analyze duplicate functionality with safety detection.
        
        Uses the enhanced duplicate analyzer to:
        - Detect duplicate files, classes, and functions
        - Identify active vs archived versions
        - Generate safety scores for each duplicate
        - Provide automated cleanup recommendations
        """
        logger.info("[*] Phase 0: Analyzing duplicate functionality")
        
        try:
            analyzer = DuplicateFunctionalityAnalyzer(str(self.project_root))
            self.duplicate_report = analyzer.analyze()
            
            # Extract metrics
            summary = self.duplicate_report.get('summary', {})
            recommendations = self.duplicate_report.get('recommendations', [])
            
            self.metrics['duplicates_found'] = summary.get('duplicate_files', 0)
            
            # Count safe-to-delete vs needs-review
            self.metrics['safe_to_delete'] = len([r for r in recommendations 
                                                  if r.get('action', '').startswith('SAFE')])
            self.metrics['needs_review'] = len([r for r in recommendations 
                                                if 'MANUAL' in r.get('action', '') or 'MIXED' in r.get('action', '')])
            
            logger.info(f"    [+] Found {self.metrics['duplicates_found']} duplicate files")
            logger.info(f"    [+] {self.metrics['safe_to_delete']} safe to delete (archived)")
            logger.info(f"    [?] {self.metrics['needs_review']} need manual review (active)")
            
            # Save detailed duplicate report
            analysis_dir = self.project_root / 'cortex-brain' / 'documents' / 'analysis'
            analysis_dir.mkdir(parents=True, exist_ok=True)
            report_path = analysis_dir / f'duplicate-analysis-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.duplicate_report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"    [*] Detailed report: {report_path.name}")
            
        except Exception as e:
            logger.warning(f"Duplicate analysis failed: {e}")
            self.metrics['errors'].append(f"Duplicate analysis: {str(e)}")
            self.duplicate_report = None
    
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
    
    def _cleanup_obsolete(self, dry_run: bool, auto_delete_archived: bool = False) -> None:
        """
        Phase 3: Remove obsolete and duplicate files.
        
        Removes:
        - Archived duplicates (if auto_delete_archived=True and Phase 0 detected them)
        - Duplicate test files
        - Obsolete backup files (*.backup, *.old, *.bak)
        - Empty directories
        - Temporary files
        
        Args:
            dry_run: If True, only preview changes without executing
            auto_delete_archived: If True, automatically delete archived duplicates identified in Phase 0
        """
        logger.info("🗑️  Phase 3: Cleaning obsolete files")
        
        # Step 1: Process archived duplicates from Phase 0 analysis
        if auto_delete_archived and self.duplicate_report:
            logger.info("Processing archived duplicates from Phase 0 analysis...")
            recommendations = self.duplicate_report.get('recommendations', [])
            
            for rec in recommendations:
                if rec['action'].startswith('SAFE') and 'archived' in rec['action'].lower():
                    file_path = Path(rec['file'])
                    
                    # Verify file exists and is in archives
                    if file_path.exists() and 'archives' in str(file_path).lower():
                        size_mb = file_path.stat().st_size / (1024 * 1024)
                        
                        if dry_run:
                            logger.info(f"[DRY RUN] Would remove archived duplicate: {file_path.relative_to(self.project_root)}")
                        else:
                            try:
                                file_path.unlink()
                                logger.info(f"Removed archived duplicate: {file_path.relative_to(self.project_root)}")
                                self.metrics['duplicates_deleted'] += 1
                            except Exception as e:
                                logger.warning(f"Failed to remove {file_path}: {e}")
                                continue
                        
                        self.metrics['files_removed'] += 1
                        self.metrics['space_freed_mb'] += size_mb
                        self.metrics['removed_files'].append(str(file_path.relative_to(self.project_root)))
            
            if self.metrics['duplicates_deleted'] > 0:
                logger.info(f"Removed {self.metrics['duplicates_deleted']} archived duplicates from Phase 0 analysis")
        
        # Step 2: Find and remove standard obsolete patterns
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
        
        # Step 3: Clean empty directories
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
        
        summary_parts = [
            f"{prefix}Cleanup complete:",
            f"{self.metrics['files_moved']} moved",
            f"{self.metrics['files_removed']} removed",
            f"{self.metrics['references_updated']} references updated"
        ]
        
        # Add duplicate analysis summary if Phase 0 was executed
        if self.duplicate_report:
            summary_parts.append(
                f"({self.metrics['duplicates_found']} duplicates: "
                f"{self.metrics['duplicates_deleted']} deleted, "
                f"{self.metrics['needs_review']} need review)"
            )
        
        return " ".join(summary_parts)
    
    def _generate_report(self, start_time: datetime, dry_run: bool, 
                        validation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cleanup report."""
        duration = (datetime.now() - start_time).total_seconds()
        
        report = {
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
        
        # Add duplicate analysis metrics if Phase 0 was executed
        if self.duplicate_report:
            report['duplicate_analysis'] = {
                'duplicates_found': self.metrics['duplicates_found'],
                'safe_to_delete': self.metrics['safe_to_delete'],
                'needs_review': self.metrics['needs_review'],
                'duplicates_deleted': self.metrics['duplicates_deleted'],
                'summary': self.duplicate_report.get('summary', {}),
                'analysis_timestamp': self.duplicate_report.get('analysis_timestamp', '')
            }
        
        return report
    
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
