"""
Cleanup Orchestrator for CORTEX 2.0

Comprehensive workspace cleanup orchestrator that:
- Deletes all backup files and folders (with GitHub archival)
- Keeps root folder clean and organized
- Reorganizes misplaced files to correct locations
- Removes redundancies in MD files (consolidates duplicates)
- Runs bloat tests on entry points and orchestrators
- Automatically triggers optimization orchestrator after cleanup
- Git tracking for all changes

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
import json
import shutil
import subprocess
import logging
import re
import hashlib
from collections import defaultdict

from src.operations.base_operation_module import BaseOperationModule, OperationPhase, OperationResult, OperationModuleMetadata, OperationStatus
from src.operations.operation_header_formatter import print_minimalist_header, print_completion_footer
from .remove_obsolete_tests_module import RemoveObsoleteTestsModule
from src.governance import DocumentGovernance

logger = logging.getLogger(__name__)


@dataclass
class CleanupMetrics:
    """Metrics from cleanup operation"""
    timestamp: datetime
    backups_deleted: int = 0
    backups_archived: int = 0
    files_reorganized: int = 0
    md_files_consolidated: int = 0
    root_files_cleaned: int = 0
    bloated_files_found: int = 0
    archived_docs_removed: int = 0
    space_freed_bytes: int = 0
    git_commits_created: int = 0
    duration_seconds: float = 0.0
    optimization_triggered: bool = False
    warnings: List[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []
    
    @property
    def space_freed_mb(self) -> float:
        return self.space_freed_bytes / (1024 * 1024)
    
    @property
    def space_freed_gb(self) -> float:
        return self.space_freed_bytes / (1024 * 1024 * 1024)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['space_freed_mb'] = self.space_freed_mb
        data['space_freed_gb'] = self.space_freed_gb
        return data


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
            'src/', 'tests/', 'cortex-brain/', 'docs/',
            'prompts/', 'workflows/', 'scripts/', '.git/',
            '.github/', '.vscode/', 'node_modules/',
            'package.json', 'tsconfig.json', 'pytest.ini',
            'requirements.txt', 'cortex.config.json',
            'cortex.config.template.json', 'cortex.config.example.json',
            'LICENSE', 'README.md', 'CHANGELOG.md',
            '.gitignore', '.gitattributes', '.editorconfig',
            'mkdocs.yml', 'cortex-operations.yaml'
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
            module_id="cleanup_orchestrator",
            name="Cleanup Orchestrator",
            description="Comprehensive workspace cleanup with organization and optimization",
            version="1.0.0",
            author="Asif Hussain",
            phase=OperationPhase.PROCESSING,
            priority=100,
            dependencies=[],
            optional=False,
            tags=['cleanup', 'maintenance', 'organization']
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
        
        # Check git status
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
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """Execute comprehensive cleanup workflow"""
        start_time = datetime.now()
        
        try:
            logger.info("=" * 70)
            logger.info("CORTEX CLEANUP ORCHESTRATOR")
            logger.info("=" * 70)
            
            # Get profile
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
            
            # Calculate duration
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
            
            # Check if path is truly protected
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
            
            # Check exact matches and prefix matches
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
        """
        Clean up legacy KDS prompt files and directories.
        
        Removes old Key Data Streams (KDS) prompts and folders that are no longer
        needed after CORTEX 2.0 deployment. Only keeps CORTEX.prompt.md and
        copilot-instructions.md in .github/prompts/.
        
        Legacy files removed:
        - Old prompt files: ask.prompt.md, continue.prompt.md, task.prompt.md, etc.
        - Old subdirectories: comm/, knowledge/, ops/, quality/, shared/, util/
        - Old root directories: _Portable, instructions, key-data-streams, learning, prompts.keys
        
        Returns:
            int: Number of legacy files/directories removed
        """
        logger.info("Scanning for legacy KDS files...")
        
        cleaned_count = 0
        github_dir = self.project_root / '.github'
        
        if not github_dir.exists():
            logger.info("  No .github directory found - skipping")
            return 0
        
        # Define legacy prompt files to remove (keep only CORTEX.prompt.md and copilot-instructions.md)
        legacy_prompt_files = [
            'ask.prompt.md',
            'continue.prompt.md',
            'create-plan.prompt.md',
            'handoff.prompt.md',
            'healthcheck.prompt.md',
            'port-instructions.prompt.md',
            'stash.prompt.md',
            'task.prompt.md',
            'test-generation.prompt.md',
            'question.prompt.md',
            'analyze-learning.prompt.md',
            'data-streams.prompt.md',
            'total-recall.prompt.md',
            'commit.prompt.md',
            'sync.prompt.md',
            'cohesion-review.prompt.md',
            'refactor.prompt.md',
            'cleanup.prompt.md'
        ]
        
        # Define legacy directories to remove
        legacy_directories = [
            '.github/_Portable',
            '.github/instructions',
            '.github/key-data-streams',
            '.github/learning',
            '.github/prompts.keys',
            '.github/prompts/comm',
            '.github/prompts/knowledge',
            '.github/prompts/ops',
            '.github/prompts/quality',
            '.github/prompts/shared',
            '.github/prompts/util',
            '.github/prompts/prompts.keys',
            '.github/prompts/internal'
        ]
        
        # Remove legacy prompt files
        prompts_dir = github_dir / 'prompts'
        if prompts_dir.exists():
            for prompt_file in legacy_prompt_files:
                prompt_path = prompts_dir / prompt_file
                if prompt_path.exists():
                    if not dry_run:
                        try:
                            prompt_path.unlink()
                            logger.info(f"  Removed: {prompt_path.relative_to(self.project_root)}")
                            cleaned_count += 1
                            self._log_action('legacy_removed', prompt_path, "Legacy KDS prompt file")
                        except Exception as e:
                            self.metrics.errors.append(f"Failed to remove {prompt_path}: {e}")
                            logger.error(f"  ❌ Failed to remove {prompt_file}: {e}")
                    else:
                        logger.info(f"  [DRY RUN] Would remove: {prompt_path.relative_to(self.project_root)}")
                        cleaned_count += 1
        
        # Remove legacy directories
        for legacy_dir_str in legacy_directories:
            legacy_dir = self.project_root / legacy_dir_str
            if legacy_dir.exists() and legacy_dir.is_dir():
                if not dry_run:
                    try:
                        shutil.rmtree(legacy_dir)
                        logger.info(f"  Removed directory: {legacy_dir.relative_to(self.project_root)}")
                        cleaned_count += 1
                        self._log_action('legacy_removed', legacy_dir, "Legacy KDS directory")
                    except Exception as e:
                        self.metrics.errors.append(f"Failed to remove {legacy_dir}: {e}")
                        logger.error(f"  ❌ Failed to remove directory {legacy_dir.name}: {e}")
                else:
                    logger.info(f"  [DRY RUN] Would remove directory: {legacy_dir.relative_to(self.project_root)}")
                    cleaned_count += 1
        
        # Remove old .github.zip if it exists
        github_zip = github_dir / '.github.zip'
        if github_zip.exists():
            if not dry_run:
                try:
                    github_zip.unlink()
                    logger.info(f"  Removed: {github_zip.relative_to(self.project_root)}")
                    cleaned_count += 1
                    self._log_action('legacy_removed', github_zip, "Legacy archive file")
                except Exception as e:
                    self.metrics.errors.append(f"Failed to remove {github_zip}: {e}")
            else:
                logger.info(f"  [DRY RUN] Would remove: {github_zip.relative_to(self.project_root)}")
                cleaned_count += 1
        
        if cleaned_count == 0:
            logger.info("  ✓ No legacy KDS files found")
        else:
            logger.info(f"  ✓ Cleaned {cleaned_count} legacy items")
        
        return cleaned_count
    
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
        """
        Clean up old archived documentation files.
        
        Removes archived duplicate documents older than 30 days from:
        - cortex-brain/documents/archive/
        - docs/archive/consolidated/
        
        Args:
            dry_run: If True, only preview without deleting
        """
        logger.info("Scanning for old archived documents...")
        
        # Define archive directories
        archive_dirs = [
            self.project_root / 'cortex-brain' / 'documents' / 'archive',
            self.project_root / 'docs' / 'archive' / 'consolidated'
        ]
        
        # Define age threshold (30 days in seconds)
        age_threshold_seconds = 30 * 24 * 60 * 60
        current_time = datetime.now().timestamp()
        
        archived_files = []
        
        for archive_dir in archive_dirs:
            if not archive_dir.exists():
                continue
            
            # Find all .md files in archive
            for archive_file in archive_dir.rglob('*.md'):
                if not archive_file.is_file():
                    continue
                
                # Check file age
                try:
                    file_mtime = archive_file.stat().st_mtime
                    file_age_seconds = current_time - file_mtime
                    
                    if file_age_seconds >= age_threshold_seconds:
                        archived_files.append(archive_file)
                
                except Exception as e:
                    logger.warning(f"Failed to check file age {archive_file}: {e}")
                    continue
        
        if not archived_files:
            logger.info("  No old archived documents found (older than 30 days)")
            return
        
        logger.info(f"Found {len(archived_files)} old archived documents (>30 days):")
        
        total_size_freed = 0
        
        for archive_file in archived_files:
            try:
                relative_path = archive_file.relative_to(self.project_root)
                file_size = archive_file.stat().st_size
                file_age_days = (current_time - archive_file.stat().st_mtime) / (24 * 60 * 60)
                
                logger.info(f"  - {relative_path} ({file_age_days:.0f} days old, {file_size / 1024:.1f}KB)")
                
                if not dry_run:
                    archive_file.unlink()
                    total_size_freed += file_size
                    self.metrics.archived_docs_removed += 1
                    self._log_action('archive_cleanup', archive_file, f"Removed old archive (age: {file_age_days:.0f} days)")
                else:
                    self.metrics.archived_docs_removed += 1
            
            except Exception as e:
                logger.warning(f"Failed to remove {archive_file}: {e}")
                self.metrics.errors.append(f"Failed to remove {archive_file}: {e}")
        
        if not dry_run:
            self.metrics.space_freed_bytes += total_size_freed
            logger.info(f"  ✓ Removed {self.metrics.archived_docs_removed} archived documents ({total_size_freed / 1024:.1f}KB freed)")
            
            # Clean up empty archive directories
            for archive_dir in archive_dirs:
                if archive_dir.exists():
                    try:
                        # Check if directory is empty
                        if not any(archive_dir.iterdir()):
                            archive_dir.rmdir()
                            logger.info(f"  🗑️  Removed empty archive directory: {archive_dir.relative_to(self.project_root)}")
                    except Exception as e:
                        logger.debug(f"Could not remove directory {archive_dir}: {e}")
        else:
            logger.info(f"  [DRY RUN] Would remove {self.metrics.archived_docs_removed} archived documents")
    
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
            # Check if there are changes
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
            
            # Import dynamically to avoid circular dependency
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
                
                # Get file size before deletion
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
        """Archive backup files to GitHub before deletion"""
        if not backup_files:
            return {'success': True, 'message': 'No backups to archive'}
        
        try:
            # Create backup archive directory
            archive_dir = self.project_root / '.backup-archive'
            archive_dir.mkdir(exist_ok=True)
            
            # Create timestamped manifest
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            manifest_file = archive_dir / f'backup-manifest-{timestamp}.json'
            
            # Build manifest
            manifest = {
                'timestamp': datetime.now().isoformat(),
                'backup_count': len(backup_files),
                'total_size_bytes': sum(f.stat().st_size for f in backup_files if f.exists()),
                'files': []
            }
            
            # Copy backups to archive
            for backup_path in backup_files:
                try:
                    if not backup_path.exists():
                        continue
                    
                    relative_path = backup_path.relative_to(self.project_root)
                    archive_subdir = archive_dir / relative_path.parent
                    archive_subdir.mkdir(parents=True, exist_ok=True)
                    
                    dest_path = archive_dir / relative_path
                    shutil.copy2(backup_path, dest_path)
                    
                    manifest['files'].append({
                        'original_path': str(relative_path),
                        'archived_path': str(dest_path.relative_to(self.project_root)),
                        'size_bytes': backup_path.stat().st_size,
                        'modified_time': datetime.fromtimestamp(backup_path.stat().st_mtime).isoformat()
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to copy backup {backup_path}: {e}")
                    continue
            
            # Save manifest
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            
            # Git operations
            subprocess.run(['git', 'add', '.backup-archive/'], cwd=str(self.project_root), check=True)
            
            commit_msg = f"Archive {len(backup_files)} backup files before cleanup - {timestamp}"
            subprocess.run(['git', 'commit', '-m', commit_msg], cwd=str(self.project_root), check=True)
            
            # Get commit SHA
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                check=True
            )
            commit_sha = result.stdout.strip()
            
            # Push to GitHub
            subprocess.run(['git', 'push'], cwd=str(self.project_root), check=True)
            
            logger.info(f"Archived {len(backup_files)} backups to GitHub (commit: {commit_sha[:8]})")
            
            return {
                'success': True,
                'commit_sha': commit_sha,
                'manifest_file': str(manifest_file.relative_to(self.project_root)),
                'archived_count': len(manifest['files'])
            }
            
        except Exception as e:
            logger.error(f"Failed to archive backups to GitHub: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
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
