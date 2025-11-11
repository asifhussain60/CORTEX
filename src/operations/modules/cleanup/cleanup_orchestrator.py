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

from src.operations.base_operation_module import BaseOperationModule, OperationPhase, OperationResult

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
    
    @property
    def metadata(self) -> Dict[str, Any]:
        return {
            'name': 'Cleanup Orchestrator',
            'description': 'Comprehensive workspace cleanup with organization and optimization',
            'version': '1.0.0',
            'author': 'Asif Hussain',
            'phase': OperationPhase.PROCESSING.value,
            'prerequisites': []
        }
    
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
            
            # Phase 6: Bloat detection
            logger.info("Phase 6: Bloat Detection")
            logger.info("-" * 70)
            self._detect_bloat()
            logger.info(f"✅ {self.metrics.bloated_files_found} bloated files detected")
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
            'cortex.config.example.json', 'cortex-operations.yaml',
            'cortex-brain.db', 'run-cortex.sh'
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
    
    def _reorganize_files(self, dry_run: bool) -> None:
        """Reorganize files to correct locations"""
        logger.info("Reorganizing files...")
        
        # Scan all files
        all_files = [f for f in self.project_root.rglob('*') if f.is_file()]
        
        for file_path in all_files:
            if self._is_protected(file_path):
                continue
            
            # Check against organization rules
            relative_path = file_path.relative_to(self.project_root)
            path_str = str(relative_path).replace('\\', '/')
            
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
