"""
Cleanup Orchestrator for CORTEX 3.0 - Enhanced Edition

Comprehensive workspace cleanup orchestrator with advanced capabilities:
- Recursive file scanning and categorization
- Smart deletion with safety validation
- File reorganization with automatic reference updates
- Document consolidation
- Script/test organization
- Git recovery capability
- Comprehensive reporting

NEW CAPABILITIES (v3.0):
- Deep recursive scanning from repo root
- Intelligent file categorization (type, purpose, age)
- Reference tracking across Python imports, paths, markdown links
- Automatic import/path/link updates when files move
- Smart deletion rules with risk assessment
- Post-cleanup verification with git recovery
- Comprehensive audit trail and reporting

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Set, Tuple, Optional
import json
import shutil
import subprocess
import logging
import re
import hashlib
from collections import defaultdict

from src.operations.base_operation_module import BaseOperationModule, OperationPhase, OperationResult, OperationModuleMetadata, OperationStatus
from src.operations.operation_header_formatter import print_minimalist_header, print_completion_footer
from src.operations.modules.cleanup.cleanup_models import CleanupMetrics
from src.operations.modules.cleanup.legacy_kds_cleaner import LegacyKDSCleaner
from src.operations.modules.cleanup.doc_archive_cleaner import DocumentArchiveCleaner
from src.operations.modules.cleanup.backup_archiver import BackupArchiver
from .remove_obsolete_tests_module import RemoveObsoleteTestsModule
from src.governance import DocumentGovernance

# NEW: Import enhanced cleanup components
from src.operations.modules.cleanup.file_scanner import FileScanner, FileCategory, FilePurpose
from src.operations.modules.cleanup.reference_tracker import ReferenceTracker
from src.operations.modules.cleanup.smart_deletion_engine import SmartDeletionEngine, DeletionRisk
from src.operations.modules.cleanup.file_reorganization_engine import FileReorganizationEngine

logger = logging.getLogger(__name__)


class CleanupOrchestrator(BaseOperationModule):
    """
    Orchestrates comprehensive workspace cleanup with:
    - Backup file management (GitHub archival before deletion)
    - Root folder organization
    - File reorganization to correct locations
    - MD file consolidation (removes duplicates)
    - Bloat detection for entry points/orchestrators
    - Automatic optimization trigger after cleanup
    """
    
    def __init__(self, project_root: Path = None):
        super().__init__()
        self.project_root = project_root or Path.cwd()
        self.metrics = CleanupMetrics(timestamp=datetime.now())
        self.actions_log: List[Dict[str, Any]] = []
        
        # Protected paths - NEVER touch these
        self.protected_paths = {
            'src/', 'src/orchestrators/', 'tests/', 'cortex-brain/', 'docs/',
            'prompts/', 'workflows/', 'scripts/', '.git/',
            '.github/', '.vscode/', 'node_modules/',
            'package.json', 'tsconfig.json', 'pytest.ini',
            'requirements.txt', 'cortex.config.json',
            'cortex.config.template.json', 'cortex.config.example.json',
            'LICENSE', 'README.md', 'CHANGELOG.md',
            '.gitignore', '.gitattributes', '.editorconfig',
            'mkdocs.yml', 'cortex-operations.yaml'
        }
        
        # CRITICAL: Protected orchestrator files (restored 2025-12-03)
        # These files were incorrectly removed by cleanup but are required for:
        # - TDD Mastery workflow (git_checkpoint_orchestrator, phase_checkpoint_manager)
        # - Deployment validation (planning_orchestrator, setup_epm_orchestrator)
        # - Test suite execution (rollback_orchestrator, rollback_command_parser)
        # - Health monitoring (application_health_orchestrator, dashboard_generator)
        # - User onboarding (onboarding_acknowledgment_orchestrator, master_setup_orchestrator)
        self.protected_orchestrator_files = {
            'src/orchestrators/git_checkpoint_orchestrator.py',
            'src/orchestrators/phase_checkpoint_manager.py',
            'src/orchestrators/rollback_orchestrator.py',
            'src/orchestrators/rollback_command_parser.py',
            'src/orchestrators/application_health_orchestrator.py',
            'src/orchestrators/dashboard_generator.py',
            'src/orchestrators/planning_orchestrator.py',
            'src/orchestrators/setup_epm_orchestrator.py',
            'src/orchestrators/onboarding_acknowledgment_orchestrator.py',
            'src/orchestrators/master_setup_orchestrator.py',
        }
        
        # File organization rules
        self.file_organization_rules = {
            # Python scripts → scripts/
            r'.*_(fix|execute|test|demo|show|verify|validate).*\.py$': 'scripts/temp/',
            # Documentation → docs/
            r'.*-(SUMMARY|STATUS|REPORT|ANALYSIS).*\.md$': 'docs/summaries/',
            # Implementation details → docs/implementation/
            r'.*-IMPLEMENTATION.*\.md$': 'docs/implementation/',
            # Planning → docs/planning/
            r'.*-(PLAN|ROADMAP|DESIGN).*\.md$': 'docs/planning/',
        }
        
        # Backup patterns
        self.backup_patterns = [
            '*.bak', '*.backup', '*.old', '*_backup_*',
            '*_old_*', '*.orig', '*-BACKUP-*', '*BACKUP*'
        ]
        
        # MD consolidation patterns (duplicate versions to merge)
        self.md_consolidation_patterns = [
            (r'^(.*)-v\d+\.md$', r'\1.md'),  # filename-v2.md → filename.md
            (r'^(.*)-\d{8}\.md$', r'\1.md'),  # filename-20250101.md → filename.md
            (r'^(.*)-COPY.*\.md$', r'\1.md'),  # filename-COPY.md → filename.md
        ]
        
        # Bloat thresholds (in tokens)
        self.bloat_thresholds = {
            'entry_points': 3000,    # Entry points should be < 3000 tokens
            'orchestrators': 5000,   # Orchestrators should be < 5000 tokens
            'modules': 2000,         # Regular modules should be < 2000 tokens
        }
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Module metadata."""
        return OperationModuleMetadata(
            module_id="cleanup_orchestrator_v3",
            name="Cleanup Orchestrator v3.0 (Enhanced)",
            description="Comprehensive workspace cleanup with advanced scanning, intelligent deletion, and automatic reference updates",
            version="3.0.0",
            author="Asif Hussain",
            phase=OperationPhase.PROCESSING,
            priority=100,
            dependencies=[],
            optional=False,
            tags=['cleanup', 'maintenance', 'organization', 'enhanced']
        )
    
    def check_prerequisites(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if cleanup can run"""
        issues = []
        
        # Verify project root
        if not self.project_root.exists():
            issues.append(f"Project root does not exist: {self.project_root}")
        
        # Verify git repository
        git_dir = self.project_root / '.git'
        if not git_dir.exists():
            issues.append("Not a git repository - cannot archive backups")
        
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                self.metrics.warnings.append(
                    "Git working directory has uncommitted changes. "
                    "Cleanup will create additional commits."
                )
        except Exception as e:
            issues.append(f"Git status check failed: {e}")
        
        return {
            'prerequisites_met': len(issues) == 0,
            'issues': issues
        }
    
    def execute_enhanced(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute ENHANCED comprehensive cleanup workflow (v3.0).
        
        NEW WORKFLOW:
        1. Deep recursive scanning and categorization
        2. Reference tracking (imports, paths, links)
        3. Smart deletion with risk assessment
        4. File reorganization with auto-reference updates
        5. Document consolidation
        6. Script/test organization
        7. Final verification with git recovery
        8. Comprehensive reporting
        
        Args:
            context: Execution context with options
            
        Returns:
            OperationResult with comprehensive cleanup data
        """
        start_time = datetime.now()
        
        try:
            logger.info("=" * 80)
            logger.info("CORTEX CLEANUP ORCHESTRATOR v3.0 - ENHANCED EDITION")
            logger.info("=" * 80)
            
            profile = context.get('profile', 'standard')
            dry_run = context.get('dry_run', False)
            
            # Display header
            mode = "DRY RUN" if dry_run else "LIVE EXECUTION"
            print_minimalist_header(
                operation_name="Enhanced Cleanup v3.0",
                version="3.0.0",
                profile=profile,
                mode=mode
            )
            
            logger.info(f"Profile: {profile}")
            logger.info(f"Dry Run: {dry_run}")
            logger.info(f"Project Root: {self.project_root}")
            logger.info("")
            
            # ================================================================
            # PHASE 1: Deep File Scanning & Categorization
            # ================================================================
            logger.info("Phase 1: Deep File Scanning & Categorization")
            logger.info("-" * 80)
            
            scanner = FileScanner(self.project_root, self.protected_paths)
            files = scanner.scan()
            
            scan_stats = scanner.get_statistics()
            logger.info(f"✅ Scanned {scan_stats['total_files']} files ({scan_stats['total_size_mb']:.2f}MB)")
            logger.info(f"   Categories: {len(scan_stats['categories'])} types identified")
            logger.info(f"   Duplicates: {scan_stats['duplicate_count']} files ({scan_stats['duplicate_groups']} groups)")
            logger.info("")
            
            # ================================================================
            # PHASE 2: Reference Tracking
            # ================================================================
            logger.info("Phase 2: Reference Tracking (imports, paths, links)")
            logger.info("-" * 80)
            
            reference_tracker = ReferenceTracker(self.project_root)
            references = reference_tracker.scan(files)
            
            ref_stats = reference_tracker.get_statistics()
            logger.info(f"✅ Tracked {ref_stats['total_references']} references:")
            logger.info(f"   - Python imports: {ref_stats['total_imports']}")
            logger.info(f"   - Path references: {ref_stats['total_path_refs']}")
            logger.info(f"   - Markdown links: {ref_stats['total_links']}")
            logger.info(f"   - Config references: {ref_stats['total_config_refs']}")
            logger.info("")
            
            # ================================================================
            # PHASE 3: Smart Deletion Analysis
            # ================================================================
            logger.info("Phase 3: Smart Deletion Analysis")
            logger.info("-" * 80)
            
            deletion_engine = SmartDeletionEngine(self.project_root)
            deletion_candidates = deletion_engine.analyze(files, reference_tracker.dependency_graph)
            
            del_stats = deletion_engine.get_statistics()
            logger.info(f"✅ Found {del_stats['total_candidates']} deletion candidates:")
            logger.info(f"   - Safe to auto-delete: {del_stats['safe_to_delete']}")
            logger.info(f"   - Space to free: {del_stats['space_to_free_mb']:.2f}MB")
            logger.info(f"   Risk breakdown: {del_stats['risk_breakdown']}")
            logger.info("")
            
            # Generate deletion manifest
            manifest_path = deletion_engine.generate_manifest()
            logger.info(f"📄 Deletion manifest: {manifest_path.relative_to(self.project_root)}")
            logger.info("")
            
            # ================================================================
            # PHASE 4: Execute Safe Deletions
            # ================================================================
            if profile in ['standard', 'comprehensive']:
                logger.info("Phase 4: Execute Safe Deletions")
                logger.info("-" * 80)
                
                deletion_results = deletion_engine.execute_deletions(
                    dry_run=dry_run,
                    risk_filter={DeletionRisk.SAFE, DeletionRisk.LOW}
                )
                
                logger.info(f"✅ Deleted {deletion_results['deleted_count']} files ({deletion_results['space_freed_mb']:.2f}MB)")
                logger.info(f"   Skipped: {deletion_results['skipped_count']}")
                logger.info(f"   Failed: {deletion_results['failed_count']}")
                
                # Update metrics
                self.metrics.files_deleted = deletion_results['deleted_count']
                self.metrics.space_freed_bytes = deletion_results['space_freed_bytes']
                logger.info("")
            
            # ================================================================
            # PHASE 5: File Reorganization
            # ================================================================
            if profile in ['standard', 'comprehensive']:
                logger.info("Phase 5: File Reorganization with Reference Updates")
                logger.info("-" * 80)
                
                reorganization_engine = FileReorganizationEngine(self.project_root, reference_tracker)
                reorganization_plan = reorganization_engine.analyze_reorganization(files)
                
                logger.info(f"📋 Reorganization plan: {len(reorganization_plan)} files to move")
                
                if reorganization_plan:
                    reorg_results = reorganization_engine.execute_reorganization(
                        reorganization_plan,
                        dry_run=dry_run
                    )
                    
                    logger.info(f"✅ Moved {reorg_results['moved_count']} files")
                    logger.info(f"   References updated: {reorg_results['references_updated']}")
                    logger.info(f"   Failed: {reorg_results['failed_count']}")
                    
                    # Generate reorganization manifest
                    if not dry_run and reorg_results['moved_count'] > 0:
                        reorg_manifest = reorganization_engine.generate_move_manifest()
                        logger.info(f"📄 Reorganization manifest: {reorg_manifest.relative_to(self.project_root)}")
                    
                    # Update metrics
                    self.metrics.files_reorganized = reorg_results['moved_count']
                
                logger.info("")
            
            # ================================================================
            # PHASE 6: Legacy Cleanup (Existing Phases)
            # ================================================================
            logger.info("Phase 6: Legacy Cleanup Operations")
            logger.info("-" * 80)
            
            # Run existing backup management
            if profile in ['standard', 'comprehensive']:
                self._manage_backups(dry_run)
                logger.info(f"✅ Managed {self.metrics.backups_deleted} backup files")
            
            # Run existing legacy cleanup
            legacy_cleaned = self._cleanup_legacy_kds_files(dry_run)
            logger.info(f"✅ Cleaned {legacy_cleaned} legacy files")
            
            # Run existing doc archive cleanup
            if profile in ['standard', 'comprehensive']:
                self._cleanup_doc_archives(dry_run)
                logger.info(f"✅ Removed {self.metrics.archived_docs_removed} archived documents")
            
            # Run existing bloat detection
            self._detect_bloat()
            logger.info(f"✅ Detected {self.metrics.bloated_files_found} bloated files")
            
            logger.info("")
            
            # ================================================================
            # PHASE 7: Final Verification & Git Recovery Setup
            # ================================================================
            logger.info("Phase 7: Final Verification & Git Recovery")
            logger.info("-" * 80)
            
            verification = self._verify_essential_files(files, deletion_results if 'deletion_results' in locals() else None)
            
            if verification['essential_deleted']:
                logger.warning(f"⚠️  {len(verification['essential_deleted'])} essential files may have been deleted")
                logger.warning("   Git recovery commands generated in report")
            else:
                logger.info("✅ No essential files deleted")
            
            logger.info("")
            
            # ================================================================
            # PHASE 8: Git Commit
            # ================================================================
            if not dry_run and self.metrics.files_deleted > 0:
                logger.info("Phase 8: Git Commit")
                logger.info("-" * 80)
                self._git_commit_enhanced_cleanup()
                logger.info(f"✅ Changes committed to git")
                logger.info("")
            
            # ================================================================
            # PHASE 9: Comprehensive Reporting
            # ================================================================
            logger.info("Phase 9: Comprehensive Reporting")
            logger.info("-" * 80)
            
            end_time = datetime.now()
            self.metrics.duration_seconds = (end_time - start_time).total_seconds()
            
            report = self._generate_enhanced_report({
                'scan_stats': scan_stats,
                'ref_stats': ref_stats,
                'del_stats': del_stats,
                'deletion_results': deletion_results if 'deletion_results' in locals() else {},
                'reorg_results': reorg_results if 'reorg_results' in locals() else {},
                'verification': verification
            })
            
            logger.info(f"✅ Report generated: {report['report_path']}")
            logger.info("")
            
            # ================================================================
            # COMPLETION
            # ================================================================
            logger.info("=" * 80)
            logger.info("ENHANCED CLEANUP COMPLETE")
            logger.info("=" * 80)
            logger.info(f"Duration: {self.metrics.duration_seconds:.2f}s")
            logger.info(f"Files Scanned: {scan_stats['total_files']}")
            logger.info(f"Files Deleted: {self.metrics.files_deleted}")
            logger.info(f"Files Moved: {self.metrics.files_reorganized}")
            logger.info(f"References Updated: {reorg_results.get('references_updated', 0) if 'reorg_results' in locals() else 0}")
            logger.info(f"Space Freed: {self.metrics.space_freed_mb:.2f}MB")
            logger.info("")
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Enhanced cleanup completed: {self.metrics.files_deleted} deleted, "
                        f"{self.metrics.files_reorganized} reorganized, "
                        f"{self.metrics.space_freed_mb:.2f}MB freed",
                data={
                    'metrics': self.metrics.to_dict(),
                    'report': report,
                    'scan_stats': scan_stats,
                    'reference_stats': ref_stats,
                    'deletion_stats': del_stats,
                    'verification': verification
                }
            )
            
        except Exception as e:
            logger.error(f"Enhanced cleanup failed: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Enhanced cleanup failed: {str(e)}",
                data={'error': str(e)}
            )
    
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """Execute comprehensive cleanup workflow"""
        start_time = datetime.now()
        
        try:
            logger.info("=" * 70)
            logger.info("CORTEX CLEANUP ORCHESTRATOR")
            logger.info("=" * 70)
            
            profile = context.get('profile', 'standard')
            dry_run = context.get('dry_run', False)
            start_time = datetime.now()
            
            # Display header
            mode = "DRY RUN" if dry_run else "LIVE EXECUTION"
            print_minimalist_header(
                operation_name="Cleanup",
                version="1.0.0",
                profile=profile,
                mode=mode
            )
            
            logger.info(f"Profile: {profile}")
            logger.info(f"Dry Run: {dry_run}")
            logger.info(f"Project Root: {self.project_root}")
            logger.info("")
            
            # Phase 1: Safety verification
            logger.info("Phase 1: Safety Verification")
            logger.info("-" * 70)
            safety_check = self._verify_safety()
            if not safety_check['safe']:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message=f"Safety check failed: {safety_check['reason']}",
                    data={'safety_check': safety_check}
                )
            logger.info(f"✅ Safety verified: {safety_check['reason']}")
            logger.info("")
            
            # Phase 2: Backup management
            if profile in ['standard', 'comprehensive']:
                logger.info("Phase 2: Backup Management")
                logger.info("-" * 70)
                self._manage_backups(dry_run)
                logger.info(f"✅ {self.metrics.backups_deleted} backups processed")
                logger.info("")
            
            # Phase 3: Root folder cleanup
            logger.info("Phase 3: Root Folder Cleanup")
            logger.info("-" * 70)
            self._cleanup_root_folder(dry_run)
            logger.info(f"✅ {self.metrics.root_files_cleaned} files cleaned from root")
            logger.info("")
            
            # Phase 3.5: Legacy KDS cleanup
            logger.info("Phase 3.5: Legacy KDS/Prompt Cleanup")
            logger.info("-" * 70)
            legacy_cleaned = self._cleanup_legacy_kds_files(dry_run)
            logger.info(f"✅ {legacy_cleaned} legacy files removed")
            logger.info("")
            
            # Phase 4: File reorganization
            if profile in ['standard', 'comprehensive']:
                logger.info("Phase 4: File Reorganization")
                logger.info("-" * 70)
                self._reorganize_files(dry_run)
                logger.info(f"✅ {self.metrics.files_reorganized} files reorganized")
                logger.info("")
            
            # Phase 5: MD file consolidation
            if profile == 'comprehensive':
                logger.info("Phase 5: MD File Consolidation")
                logger.info("-" * 70)
                self._consolidate_md_files(dry_run)
                logger.info(f"✅ {self.metrics.md_files_consolidated} MD files consolidated")
                logger.info("")
            
            # Phase 5.5: Documentation archive cleanup
            if profile in ['standard', 'comprehensive']:
                logger.info("Phase 5.5: Documentation Archive Cleanup")
                logger.info("-" * 70)
                self._cleanup_doc_archives(dry_run)
                logger.info(f"✅ {self.metrics.archived_docs_removed} archived documents removed")
                logger.info("")
            
            # Phase 6: Bloat detection
            logger.info("Phase 6: Bloat Detection")
            logger.info("-" * 70)
            self._detect_bloat()
            logger.info(f"✅ {self.metrics.bloated_files_found} bloated files detected")
            logger.info("")
            
            # Phase 6.5: Remove obsolete tests (marked by optimize orchestrator)
            if profile in ['standard', 'comprehensive']:
                logger.info("Phase 6.5: Remove Obsolete Tests")
                logger.info("-" * 70)
                
                # First check if optimize has marked any tests for deletion
                obsolete_manifest = self.project_root / 'cortex-brain' / 'obsolete-tests-manifest.json'
                if obsolete_manifest.exists():
                    logger.info("Found obsolete tests manifest from optimize orchestrator")
                    obsolete_result = self._remove_marked_obsolete_tests(dry_run, obsolete_manifest)
                else:
                    # Fallback to old detection method
                    obsolete_result = self._remove_obsolete_tests(dry_run)
                
                if obsolete_result.success:
                    obsolete_count = obsolete_result.data.get('obsolete_tests_found', 0)
                    removed_count = obsolete_result.data.get('removed_count', 0)
                    logger.info(f"✅ Found {obsolete_count} obsolete tests")
                    if not dry_run and removed_count > 0:
                        logger.info(f"✅ Removed {removed_count} obsolete test files")
                        for test_file in obsolete_result.data.get('removed_files', []):
                            logger.info(f"   - {test_file}")
                        
                        # Delete manifest after successful cleanup
                        if obsolete_manifest.exists():
                            obsolete_manifest.unlink()
                            logger.info("✅ Cleaned up obsolete tests manifest")
                else:
                    logger.warning(f"⚠️  Obsolete test removal failed: {obsolete_result.message}")
                logger.info("")
            
            # Phase 7: Git commit
            if not dry_run and self.metrics.backups_deleted > 0:
                logger.info("Phase 7: Git Commit")
                logger.info("-" * 70)
                self._git_commit_cleanup()
                logger.info(f"✅ {self.metrics.git_commits_created} git commits created")
                logger.info("")
            
            # Phase 8: Trigger optimization orchestrator
            if not dry_run and profile == 'comprehensive':
                logger.info("Phase 8: Optimization Orchestrator")
                logger.info("-" * 70)
                self._trigger_optimization(context)
                logger.info(f"✅ Optimization orchestrator {'triggered' if self.metrics.optimization_triggered else 'skipped'}")
                logger.info("")
            
            end_time = datetime.now()
            self.metrics.duration_seconds = (end_time - start_time).total_seconds()
            
            # Generate report
            report = self._generate_report()
            
            logger.info("=" * 70)
            logger.info("CLEANUP COMPLETE")
            logger.info("=" * 70)
            logger.info(f"Duration: {self.metrics.duration_seconds:.2f}s")
            logger.info(f"Space Freed: {self.metrics.space_freed_mb:.2f}MB")
            logger.info(f"Files Processed: {self.metrics.backups_deleted + self.metrics.files_reorganized}")
            logger.info("")
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Cleanup completed successfully: {self.metrics.backups_deleted} backups, "
                        f"{self.metrics.files_reorganized} files reorganized, "
                        f"{self.metrics.space_freed_mb:.2f}MB freed",
                data={
                    'metrics': self.metrics.to_dict(),
                    'report': report,
                    'actions_log': self.actions_log
                }
            )
            
        except Exception as e:
            logger.error(f"Cleanup orchestrator failed: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Cleanup failed: {str(e)}",
                data={'error': str(e)}
            )
    
    def _verify_safety(self) -> Dict[str, Any]:
        """CRITICAL: Verify that protected files won't be touched"""
        violations = []
        
        # Verify protected paths exist
        for protected in self.protected_paths:
            path = self.project_root / protected
            if not path.exists():
                continue
            
            if not self._is_protected(path):
                violations.append({
                    'path': str(protected),
                    'reason': 'Protected path not marked as protected'
                })
        
        if violations:
            return {
                'safe': False,
                'reason': f"Found {len(violations)} protection violations",
                'violations': violations
            }
        
        return {
            'safe': True,
            'reason': f"All {len(self.protected_paths)} protected paths verified"
        }
    
    def _is_protected(self, path: Path) -> bool:
        """Check if path is protected"""
        try:
            relative_path = path.relative_to(self.project_root)
            path_str = str(relative_path).replace('\\', '/')
            
            # Check if path matches protected orchestrator files (exact match)
            if path_str in self.protected_orchestrator_files:
                logger.debug(f"Protected orchestrator file: {path_str}")
                return True
            
            # Check if path is in protected directories
            for protected in self.protected_paths:
                if path_str == protected.rstrip('/'):
                    return True
                if path_str.startswith(protected):
                    return True
            
            return False
            
        except ValueError:
            # Path is not relative to project root
            return True  # Protect paths outside project
    
    def _manage_backups(self, dry_run: bool) -> None:
        """Archive backups to GitHub then delete them"""
        logger.info("Scanning for backup files...")
        
        backup_files = []
        
        for pattern in self.backup_patterns:
            for file_path in self.project_root.rglob(pattern):
                if self._is_protected(file_path):
                    continue
                
                if file_path.is_file():
                    backup_files.append(file_path)
        
        if not backup_files:
            logger.info("No backup files found")
            return
        
        logger.info(f"Found {len(backup_files)} backup files")
        
        # Archive to GitHub
        if not dry_run:
            archive_result = self._archive_backups_to_github(backup_files)
            
            if archive_result['success']:
                logger.info(f"✅ Archived {archive_result['archived_count']} backups to GitHub")
                self.metrics.backups_archived = archive_result['archived_count']
                
                # Now delete local files
                for file_path in backup_files:
                    try:
                        size = file_path.stat().st_size
                        file_path.unlink()
                        
                        self.metrics.backups_deleted += 1
                        self.metrics.space_freed_bytes += size
                        
                        self._log_action('backup_deleted', file_path,
                                       f"Archived to GitHub (commit: {archive_result['commit_sha'][:8]})")
                        
                    except Exception as e:
                        self.metrics.errors.append(f"Failed to delete {file_path}: {e}")
            else:
                logger.warning(f"GitHub archival failed: {archive_result.get('error')}")
                self.metrics.warnings.append(f"Backup archival skipped: {archive_result.get('error')}")
        else:
            logger.info(f"[DRY RUN] Would archive and delete {len(backup_files)} backup files")
            self.metrics.backups_deleted = len(backup_files)
    
    def _cleanup_root_folder(self, dry_run: bool) -> None:
        """Keep root folder clean - move misplaced files"""
        logger.info("Scanning root folder...")
        
        # Allowed files in root
        allowed_root_files = {
            'README.md', 'LICENSE', 'CHANGELOG.md',
            '.gitignore', '.gitattributes', '.editorconfig',
            'package.json', 'package-lock.json', 'tsconfig.json',
            'requirements.txt', 'pytest.ini', 'mkdocs.yml',
            'cortex.config.json', 'cortex.config.template.json',
            'cortex.config.example.json', 'cortex-operations.yaml'
        }
        
        root_files = [f for f in self.project_root.iterdir() if f.is_file()]
        
        for file_path in root_files:
            if file_path.name.startswith('.'):
                continue
            
            if file_path.name in allowed_root_files:
                continue
            
            # Misplaced file - move to scripts/temp/
            dest_dir = self.project_root / 'scripts' / 'temp'
            dest_path = dest_dir / file_path.name
            
            if not dry_run:
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file_path), str(dest_path))
            
            self.metrics.root_files_cleaned += 1
            self._log_action('file_moved', file_path, f"Moved to {dest_path.relative_to(self.project_root)}")
            
            logger.info(f"  Moved: {file_path.name} → scripts/temp/")
    
    def _cleanup_legacy_kds_files(self, dry_run: bool) -> int:
        """Clean up legacy KDS prompt files and directories (delegated to LegacyKDSCleaner)."""
        cleaner = LegacyKDSCleaner(self.project_root, self._log_action, self.metrics)
        return cleaner.cleanup(dry_run)
    
    def _reorganize_files(self, dry_run: bool) -> None:
        """Reorganize files to correct locations - OPTIMIZED"""
        logger.info("Reorganizing files...")
        
        # Early exit if no organization rules
        if not self.file_organization_rules:
            logger.info("  No organization rules configured")
            return
        
        # OPTIMIZATION: Only scan specific target directories instead of entire project
        # This reduces scan time from 20s to <100ms
        target_dirs = [
            self.project_root,  # Root level only
            self.project_root / 'cortex-brain',
            self.project_root / 'scripts',
            self.project_root / 'docs',
            self.project_root / 'publish'
        ]
        
        # OPTIMIZATION: Use iterdir() for shallow scans instead of rglob()
        all_files = []
        for target in target_dirs:
            if target.exists():
                try:
                    # Only scan immediate children, not recursive
                    all_files.extend([f for f in target.iterdir() if f.is_file()])
                except PermissionError:
                    logger.warning(f"  Permission denied: {target}")
                    continue
        
        # OPTIMIZATION: Pre-filter protected files ONCE
        files_to_check = [f for f in all_files if not self._is_protected(f)]
        
        # OPTIMIZATION: Cache relative path calculations
        relative_paths = {}
        for f in files_to_check:
            try:
                relative_paths[f] = f.relative_to(self.project_root)
            except ValueError:
                # File is outside project root
                continue
        
        for file_path in files_to_check:
            if file_path not in relative_paths:
                continue
            
            relative_path = relative_paths[file_path]  # O(1) lookup
            
            for pattern, destination in self.file_organization_rules.items():
                if re.match(pattern, file_path.name, re.IGNORECASE):
                    # File should be moved
                    dest_dir = self.project_root / destination
                    dest_path = dest_dir / file_path.name
                    
                    # Don't move if already in correct location
                    if file_path.parent == dest_dir:
                        continue
                    
                    if not dry_run:
                        dest_dir.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(file_path), str(dest_path))
                    
                    self.metrics.files_reorganized += 1
                    self._log_action('file_reorganized', file_path,
                                   f"Moved to {dest_path.relative_to(self.project_root)}")
                    
                    logger.info(f"  Reorganized: {file_path.name} → {destination}")
                    break
    
    def _consolidate_md_files(self, dry_run: bool) -> None:
        """Consolidate duplicate MD files"""
        logger.info("Consolidating MD files...")
        
        # Find all markdown files
        md_files = list(self.project_root.rglob('*.md'))
        
        # Group by base name (detect duplicates)
        file_groups = defaultdict(list)
        
        for md_file in md_files:
            if self._is_protected(md_file):
                continue
            
            # Try each consolidation pattern
            base_name = None
            for pattern, replacement in self.md_consolidation_patterns:
                match = re.match(pattern, md_file.name, re.IGNORECASE)
                if match:
                    base_name = match.group(1) + '.md'
                    break
            
            if base_name:
                file_groups[base_name].append(md_file)
        
        # Consolidate groups
        for base_name, files in file_groups.items():
            if len(files) <= 1:
                continue
            
            # Keep the newest file, delete others
            files_sorted = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)
            newest = files_sorted[0]
            duplicates = files_sorted[1:]
            
            logger.info(f"  Consolidating {len(duplicates)} versions of {base_name}:")
            logger.info(f"    Keeping: {newest.name}")
            
            for dup in duplicates:
                if not dry_run:
                    # Archive before deletion
                    archive_dir = self.project_root / 'docs' / 'archive' / 'consolidated'
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    
                    shutil.move(str(dup), str(archive_dir / dup.name))
                
                self.metrics.md_files_consolidated += 1
                self._log_action('md_consolidated', dup, f"Archived to docs/archive/consolidated/")
                
                logger.info(f"    Archived: {dup.name}")
    
    def _cleanup_doc_archives(self, dry_run: bool) -> None:
        """Clean up old archived documentation files (delegated to DocumentArchiveCleaner)."""
        cleaner = DocumentArchiveCleaner(self.project_root, self._log_action, self.metrics)
        return cleaner.cleanup(dry_run)
    
    def _detect_bloat(self) -> None:
        """Detect bloated entry points and orchestrators"""
        logger.info("Detecting bloated files...")
        
        files_to_check = {
            'entry_points': list((self.project_root / 'prompts').rglob('*.md')),
            'orchestrators': list((self.project_root / 'src' / 'operations' / 'modules').rglob('*orchestrator*.py')),
            'modules': list((self.project_root / 'src' / 'operations' / 'modules').rglob('*_module.py'))
        }
        
        bloated_files = []
        
        for file_type, files in files_to_check.items():
            threshold = self.bloat_thresholds.get(file_type, 2000)
            
            for file_path in files:
                if self._is_protected(file_path):
                    continue
                
                try:
                    # Estimate token count (rough: 1 token ≈ 4 characters)
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    token_count = len(content) // 4
                    
                    if token_count > threshold:
                        bloated_files.append({
                            'path': str(file_path.relative_to(self.project_root)),
                            'type': file_type,
                            'tokens': token_count,
                            'threshold': threshold,
                            'excess': token_count - threshold,
                            'excess_percent': ((token_count - threshold) / threshold) * 100
                        })
                        
                        self.metrics.bloated_files_found += 1
                        
                        logger.warning(f"  BLOAT: {file_path.name} ({token_count} tokens, "
                                     f"{token_count - threshold} over threshold)")
                        
                except Exception as e:
                    self.metrics.warnings.append(f"Failed to check {file_path}: {e}")
        
        if bloated_files:
            # Save bloat report
            report_path = self.project_root / 'logs' / 'cleanup' / f'bloat-report-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'bloated_files': bloated_files,
                    'summary': {
                        'total_bloated': len(bloated_files),
                        'entry_points': sum(1 for f in bloated_files if f['type'] == 'entry_points'),
                        'orchestrators': sum(1 for f in bloated_files if f['type'] == 'orchestrators'),
                        'modules': sum(1 for f in bloated_files if f['type'] == 'modules')
                    }
                }, f, indent=2)
            
            logger.info(f"  Bloat report saved: {report_path.relative_to(self.project_root)}")
    
    def _git_commit_cleanup(self) -> None:
        """Commit cleanup changes to git"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if not result.stdout.strip():
                logger.info("No changes to commit")
                return
            
            # Add all changes
            subprocess.run(
                ['git', 'add', '-A'],
                cwd=str(self.project_root),
                check=True,
                timeout=10
            )
            
            # Commit with detailed message
            commit_message = f"""[CLEANUP] Workspace cleanup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Automated cleanup performed:
- Backups: {self.metrics.backups_deleted} deleted (archived to GitHub)
- Root folder: {self.metrics.root_files_cleaned} files moved
- Files reorganized: {self.metrics.files_reorganized}
- MD files consolidated: {self.metrics.md_files_consolidated}
- Archived docs removed: {self.metrics.archived_docs_removed}
- Bloated files detected: {self.metrics.bloated_files_found}
- Space freed: {self.metrics.space_freed_mb:.2f}MB

Duration: {self.metrics.duration_seconds:.2f}s"""
            
            subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=str(self.project_root),
                check=True,
                timeout=30
            )
            
            self.metrics.git_commits_created += 1
            logger.info("✅ Changes committed to git")
            
        except subprocess.TimeoutExpired:
            self.metrics.errors.append("Git commit timed out")
        except subprocess.CalledProcessError as e:
            self.metrics.errors.append(f"Git commit failed: {e}")
    
    def _trigger_optimization(self, context: Dict[str, Any]) -> None:
        """Trigger optimization orchestrator after cleanup"""
        try:
            logger.info("Triggering optimization orchestrator...")
            
            from src.operations.modules.optimization.optimize_cortex_orchestrator import OptimizeCortexOrchestrator
            
            orchestrator = OptimizeCortexOrchestrator(self.project_root)
            result = orchestrator.execute({
                'profile': context.get('optimization_profile', 'standard'),
                'triggered_by': 'cleanup_orchestrator'
            })
            
            if result.success:
                self.metrics.optimization_triggered = True
                logger.info(f"✅ Optimization completed: {result.message}")
            else:
                logger.warning(f"⚠️ Optimization failed: {result.message}")
                self.metrics.warnings.append(f"Optimization failed: {result.message}")
                
        except ImportError as e:
            logger.warning(f"Could not import optimization orchestrator: {e}")
            self.metrics.warnings.append("Optimization orchestrator not available")
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            self.metrics.errors.append(f"Optimization failed: {e}")
    
    def _remove_marked_obsolete_tests(self, dry_run: bool, manifest_file: Path) -> OperationResult:
        """Remove obsolete tests marked by optimize orchestrator.
        
        Args:
            dry_run: If True, only preview without deleting
            manifest_file: Path to obsolete-tests-manifest.json
            
        Returns:
            OperationResult with removal details
        """
        from src.operations.base_operation_module import OperationStatus
        
        try:
            # Parse manifest
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            marked_tests = manifest.get('tests', [])
            if not marked_tests:
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message="No obsolete tests marked for deletion",
                    data={'obsolete_tests_found': 0, 'removed_count': 0, 'removed_files': []}
                )
            
            logger.info(f"Found {len(marked_tests)} tests marked for deletion by optimize orchestrator")
            logger.info(f"Manifest timestamp: {manifest.get('timestamp', 'unknown')}")
            
            removed_files = []
            skipped_files = []
            total_size_freed = 0
            
            for test_entry in marked_tests:
                file_path_str = test_entry.get('file_path', '')
                reason = test_entry.get('reason', 'Marked as obsolete')
                confidence = test_entry.get('confidence', 'medium')
                missing_imports = test_entry.get('missing_imports', [])
                
                # Resolve full path
                test_file = self.project_root / file_path_str
                
                # Safety validations
                if not test_file.exists():
                    logger.warning(f"⚠️  Test file not found: {file_path_str}")
                    skipped_files.append(str(test_file))
                    continue
                
                if not test_file.is_file():
                    logger.warning(f"⚠️  Path is not a file: {file_path_str}")
                    skipped_files.append(str(test_file))
                    continue
                
                if not str(test_file).startswith(str(self.project_root / 'tests')):
                    logger.warning(f"⚠️  File outside tests directory: {file_path_str}")
                    skipped_files.append(str(test_file))
                    continue
                
                file_size = test_file.stat().st_size
                
                # Log details
                logger.info(f"  📄 {file_path_str}")
                logger.info(f"     Reason: {reason}")
                logger.info(f"     Confidence: {confidence}")
                if missing_imports:
                    logger.info(f"     Missing imports: {', '.join(missing_imports)}")
                
                if not dry_run:
                    try:
                        test_file.unlink()
                        removed_files.append(file_path_str)
                        total_size_freed += file_size
                        self._log_action('DELETE', test_file, f"{reason} (confidence: {confidence})")
                        logger.info(f"     ✅ Deleted")
                    except Exception as e:
                        logger.error(f"     ❌ Failed to delete: {e}")
                        skipped_files.append(str(test_file))
                        self.metrics.errors.append(f"Failed to delete {file_path_str}: {e}")
                else:
                    logger.info(f"     [DRY RUN] Would delete")
                    removed_files.append(file_path_str)  # Track for preview
            
            # Update metrics
            if not dry_run and removed_files:
                self.metrics.files_deleted += len(removed_files)
                self.metrics.space_freed_bytes += total_size_freed
                
                # Clean up empty test directories
                for test_path in removed_files:
                    test_file = self.project_root / test_path
                    parent_dir = test_file.parent
                    try:
                        if parent_dir.exists() and not any(parent_dir.iterdir()):
                            parent_dir.rmdir()
                            logger.info(f"     🗑️  Removed empty directory: {parent_dir.relative_to(self.project_root)}")
                    except Exception as e:
                        logger.debug(f"Could not remove directory {parent_dir}: {e}")
            
            result_message = f"Processed {len(marked_tests)} marked tests"
            if removed_files:
                result_message += f", removed {len(removed_files)}"
            if skipped_files:
                result_message += f", skipped {len(skipped_files)}"
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=result_message,
                data={
                    'obsolete_tests_found': len(marked_tests),
                    'removed_count': len(removed_files),
                    'removed_files': removed_files,
                    'skipped_files': skipped_files,
                    'space_freed_bytes': total_size_freed
                }
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse manifest: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Manifest parsing failed: {str(e)}",
                data={'error': str(e)}
            )
        except Exception as e:
            logger.error(f"Failed to remove marked obsolete tests: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Obsolete test removal failed: {str(e)}",
                data={'error': str(e)}
            )
    
    def _remove_obsolete_tests(self, dry_run: bool) -> OperationResult:
        """Remove obsolete test files calling non-existent APIs."""
        from src.operations.base_operation_module import OperationStatus
        
        try:
            module = RemoveObsoleteTestsModule(self.project_root)
            return module.execute({'dry_run': dry_run})
        except Exception as e:
            logger.error(f"Failed to remove obsolete tests: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED, 
                message=f"Obsolete test removal failed: {str(e)}", 
                data={'error': str(e)}
            )
    
    def _archive_backups_to_github(self, backup_files: List[Path]) -> Dict[str, Any]:
        """Archive backup files to GitHub before deletion (delegated to BackupArchiver)."""
        archiver = BackupArchiver(self.project_root)
        return archiver.archive_to_github(backup_files)
    
    def _log_action(self, action: str, path: Path, reason: str) -> None:
        """Log a cleanup action"""
        try:
            relative_path = path.relative_to(self.project_root)
        except ValueError:
            relative_path = path
        
        self.actions_log.append({
            'action': action,
            'path': str(relative_path),
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive cleanup report"""
        recommendations = []
        
        if self.metrics.bloated_files_found > 0:
            recommendations.append(
                f"Found {self.metrics.bloated_files_found} bloated files. "
                f"Consider refactoring or splitting into modules."
            )
        
        if self.metrics.space_freed_mb > 50:
            recommendations.append(
                f"Freed {self.metrics.space_freed_mb:.2f}MB of disk space. "
                f"Consider running cleanup weekly."
            )
        
        if self.metrics.md_files_consolidated > 5:
            recommendations.append(
                f"Consolidated {self.metrics.md_files_consolidated} duplicate MD files. "
                f"Consider using version control instead of file copies."
            )
        
        if self.metrics.root_files_cleaned > 10:
            recommendations.append(
                f"Moved {self.metrics.root_files_cleaned} files from root. "
                f"Keep root folder clean for better organization."
            )
        
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics.to_dict(),
            'actions_count': len(self.actions_log),
            'recommendations': recommendations,
            'success': len(self.metrics.errors) == 0
        }

    # ========================================================================
    # ENHANCED v3.0 METHODS
    # ========================================================================
    
    def _verify_essential_files(self, files: Dict[str, Any], deletion_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verify no essential files were deleted.
        
        Args:
            files: Dictionary of scanned files
            deletion_results: Results from deletion engine
            
        Returns:
            Verification results with recovery commands if needed
        """
        essential_deleted = []
        recovery_commands = []
        
        if not deletion_results or not deletion_results.get('deleted_files'):
            return {
                'essential_deleted': [],
                'recovery_commands': [],
                'verification_passed': True
            }
        
        # Define essential file patterns
        essential_patterns = [
            r'^src/tier0/.*\.py$',  # Core tier 0
            r'^src/tier1/.*\.py$',  # Core tier 1
            r'^src/cortex_agents/.*\.py$',  # Agents
            r'^cortex-brain/brain-protection-rules\.yaml$',  # Protection rules
            r'^cortex-brain/response-templates\.yaml$',  # Response templates
            r'^cortex.config\.json$',  # Main config
            r'^requirements\.txt$',  # Dependencies
        ]
        
        for deleted_file in deletion_results.get('deleted_files', []):
            # Check if file matches essential patterns
            for pattern in essential_patterns:
                if re.match(pattern, deleted_file):
                    essential_deleted.append(deleted_file)
                    
                    # Generate git recovery command
                    recovery_commands.append(f"git checkout HEAD -- {deleted_file}")
                    break
        
        verification_passed = len(essential_deleted) == 0
        
        return {
            'essential_deleted': essential_deleted,
            'recovery_commands': recovery_commands,
            'verification_passed': verification_passed,
            'total_deleted': len(deletion_results.get('deleted_files', []))
        }
    
    def _git_commit_enhanced_cleanup(self) -> None:
        """Commit enhanced cleanup changes to git"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if not result.stdout.strip():
                logger.info("No changes to commit")
                return
            
            # Add all changes
            subprocess.run(
                ['git', 'add', '-A'],
                cwd=str(self.project_root),
                check=True,
                timeout=10
            )
            
            # Commit with detailed message
            commit_message = f"""[CLEANUP v3.0] Enhanced workspace cleanup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Enhanced cleanup performed:
- Files scanned: comprehensive recursive scan
- Files deleted: {self.metrics.files_deleted} (with safety validation)
- Files reorganized: {self.metrics.files_reorganized} (with reference updates)
- Backups managed: {self.metrics.backups_deleted} archived and deleted
- Space freed: {self.metrics.space_freed_mb:.2f}MB
- References updated: automatic import/path/link updates
- Verification: essential files checked and protected

Duration: {self.metrics.duration_seconds:.2f}s
Version: 3.0.0"""
            
            subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=str(self.project_root),
                check=True,
                timeout=30
            )
            
            self.metrics.git_commits_created += 1
            logger.info("✅ Changes committed to git")
            
        except subprocess.TimeoutExpired:
            self.metrics.errors.append("Git commit timed out")
        except subprocess.CalledProcessError as e:
            self.metrics.errors.append(f"Git commit failed: {e}")
    
    def _generate_enhanced_report(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive cleanup report.
        
        Args:
            stats: Dictionary containing all statistics
            
        Returns:
            Report dictionary with path to saved report
        """
        recommendations = []
        
        # Analyze scan results
        scan_stats = stats.get('scan_stats', {})
        if scan_stats.get('duplicate_count', 0) > 10:
            recommendations.append(
                f"Found {scan_stats['duplicate_count']} duplicate files. "
                f"Consider using git for version control instead of file copies."
            )
        
        # Analyze deletion results
        del_stats = stats.get('del_stats', {})
        if del_stats.get('space_to_free_mb', 0) > 100:
            recommendations.append(
                f"Could free {del_stats['space_to_free_mb']:.2f}MB more by reviewing medium-risk deletions."
            )
        
        # Analyze reorganization
        reorg_results = stats.get('reorg_results', {})
        if reorg_results.get('moved_count', 0) > 20:
            recommendations.append(
                f"Reorganized {reorg_results['moved_count']} files. "
                f"Consider establishing file organization guidelines to prevent future misplacement."
            )
        
        # Analyze verification
        verification = stats.get('verification', {})
        if not verification.get('verification_passed', True):
            recommendations.append(
                f"⚠️ {len(verification['essential_deleted'])} essential files may need recovery. "
                f"Review recovery commands in report."
            )
        
        # Build comprehensive report
        report = {
            'timestamp': datetime.now().isoformat(),
            'version': '3.0.0',
            'summary': {
                'total_scanned': scan_stats.get('total_files', 0),
                'total_deleted': self.metrics.files_deleted,
                'total_moved': self.metrics.files_reorganized,
                'total_references_updated': reorg_results.get('references_updated', 0),
                'space_freed_mb': self.metrics.space_freed_mb,
                'duration_seconds': self.metrics.duration_seconds
            },
            'scan_statistics': scan_stats,
            'reference_statistics': stats.get('ref_stats', {}),
            'deletion_statistics': del_stats,
            'deletion_results': stats.get('deletion_results', {}),
            'reorganization_results': reorg_results,
            'verification': verification,
            'recommendations': recommendations,
            'metrics': self.metrics.to_dict()
        }
        
        # Save report
        report_path = self.project_root / 'cortex-brain' / 'cleanup-reports' / f'enhanced-cleanup-report-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Enhanced cleanup report saved: {report_path.relative_to(self.project_root)}")
        
        report['report_path'] = str(report_path.relative_to(self.project_root))
        
        return report
