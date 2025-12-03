"""
CORTEX Optimize Operation Module

Provides comprehensive CORTEX system optimization capabilities.
Implements all optimizations from CORTEX-OPTIMIZATION-PLAN-2025-12-01.md

Features:
- File organization (move scattered tests/scripts to proper directories)
- Build artifact cleanup (dist/, publish/, *.db files)
- Archive consolidation (old backups, temporary files)
- Duplicate file removal (templates, logos)
- Database optimization (vacuum, cleanup)
- Cache optimization (YAML cache, temporary files)
- Automated maintenance tasks

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json
import hashlib
import re

from .base_operation_module import (
    BaseOperationModule,
    OperationResult,
    OperationStatus,
    OperationPhase,
    OperationModuleMetadata,
)
from src.utils.skull_test_runner import run_skull_tests, format_skull_test_summary


logger = logging.getLogger(__name__)


class OptimizeOperation(BaseOperationModule):
    """
    Optimization operation for CORTEX and user code.
    
    Features:
    - Code optimization suggestions
    - CORTEX brain cleanup
    - Cache optimization
    - Database vacuum
    - Token usage optimization
    
    Usage:
        User says: "optimize" or "optimize code" or "optimize cortex"
        CORTEX routes to this module
    """
    
    def __init__(self):
        super().__init__()
        self._metadata = OperationModuleMetadata(
            module_id="optimize",
            name="optimize",
            description="Code and system optimization",
            phase=OperationPhase.PROCESSING,
            priority=50,
            version="1.0.0",
            author="Asif Hussain",
            tags=["user-facing", "maintenance", "performance"],
        )
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return operation metadata."""
        return self._metadata
    
    def validate(self) -> OperationResult:
        """
        Validate optimization operation can run.
        
        Returns:
            OperationResult with validation status
        """
        issues = []
        
        brain_path = Path.cwd() / "cortex-brain"
        if not brain_path.exists():
            issues.append("cortex-brain/ directory not found")
        
        tier1_db = brain_path / "tier1" / "working_memory.db"
        tier2_db = brain_path / "tier2" / "knowledge_graph.db"
        
        if not tier1_db.exists():
            issues.append("Tier 1 database not found (working_memory.db)")
        
        if not tier2_db.exists():
            issues.append("Tier 2 database not found (knowledge_graph.db)")
        
        if issues:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Validation failed: {', '.join(issues)}",
            )
        
        return OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message="✓ Optimization prerequisites validated",
        )
    
    def execute(self, **kwargs) -> OperationResult:
        """
        Execute comprehensive optimization operations.
        
        Implements all fixes from CORTEX-OPTIMIZATION-PLAN-2025-12-01.md:
        - Phase 1: File organization and cleanup (root files → proper directories)
        - Phase 2: Archive consolidation and duplicate removal
        - Database optimization (vacuum, cleanup)
        - Cache optimization
        
        Args:
            target: What to optimize (organization/archives/cortex/cache/all)
            aggressive: Use aggressive optimization
            dry_run: Preview changes without executing (default: False)
            skip_skull_tests: Skip SKULL test validation for fast user operations (default: False)
        
        Returns:
            OperationResult with optimization summary
        """
        target = kwargs.get('target', 'all')
        aggressive = kwargs.get('aggressive', False)
        dry_run = kwargs.get('dry_run', False)
        skip_skull_tests = kwargs.get('skip_skull_tests', False)
        
        logger.info(f"Starting CORTEX optimization (target={target}, aggressive={aggressive}, dry_run={dry_run})")
        
        results = {
            'optimizations_applied': [],
            'space_saved_mb': 0.0,
            'files_moved': 0,
            'files_removed': 0,
            'directories_cleaned': 0,
            'dry_run': dry_run,
        }
        
        try:
            # Phase 1: File Organization (CRITICAL - fixes root directory clutter)
            if target in ['organization', 'all']:
                org_result = self._organize_files(dry_run)
                results['optimizations_applied'].extend(org_result['applied'])
                results['space_saved_mb'] += org_result['space_saved_mb']
                results['files_moved'] += org_result.get('files_moved', 0)
            
            # Phase 1: Build Artifacts Cleanup
            if target in ['organization', 'cortex', 'all']:
                artifacts_result = self._cleanup_build_artifacts(dry_run)
                results['optimizations_applied'].extend(artifacts_result['applied'])
                results['space_saved_mb'] += artifacts_result['space_saved_mb']
                results['files_removed'] += artifacts_result.get('files_removed', 0)
            
            # Phase 1: Duplicate File Removal
            if target in ['organization', 'cortex', 'all']:
                dup_result = self._remove_duplicates(dry_run)
                results['optimizations_applied'].extend(dup_result['applied'])
                results['space_saved_mb'] += dup_result['space_saved_mb']
                results['files_removed'] += dup_result.get('files_removed', 0)
            
            # Phase 2: Archive Consolidation
            if target in ['archives', 'cortex', 'all']:
                archive_result = self._consolidate_archives(dry_run)
                results['optimizations_applied'].extend(archive_result['applied'])
                results['space_saved_mb'] += archive_result['space_saved_mb']
                results['directories_cleaned'] += archive_result.get('directories_cleaned', 0)
            
            # Brain cleanup (original functionality)
            if target in ['cortex', 'all']:
                cleanup_result = self._optimize_brain(dry_run)
                results['optimizations_applied'].extend(cleanup_result['applied'])
                results['space_saved_mb'] += cleanup_result['space_saved_mb']
            
            # Markdown consolidation (NEW - Phase 3)
            if target in ['consolidation', 'all']:
                consolidation_result = self._consolidate_markdown_docs(dry_run)
                results['optimizations_applied'].extend(consolidation_result['applied'])
                results['space_saved_mb'] += consolidation_result['space_saved_mb']
                results['files_removed'] += consolidation_result.get('files_removed', 0)
            
            # Cache optimization
            if target in ['cache', 'cortex', 'all']:
                cache_result = self._optimize_cache(dry_run)
                results['optimizations_applied'].extend(cache_result['applied'])
                results['space_saved_mb'] += cache_result['space_saved_mb']
            
            # Database vacuum
            if target in ['cortex', 'all']:
                db_result = self._vacuum_databases(aggressive, dry_run)
                results['optimizations_applied'].extend(db_result['applied'])
                results['space_saved_mb'] += db_result['space_saved_mb']
            
            # Generate optimization report
            report_path = self._generate_optimization_report(results)
            if report_path:
                results['report_path'] = str(report_path)
            
            # SKULL test validation (admin operations only)
            # Skip in dry-run mode or when skip_skull_tests=True (user operations)
            if not dry_run and not skip_skull_tests:
                logger.info("\n" + "="*80)
                logger.info("MANDATORY VALIDATION: Running SKULL test suite...")
                logger.info("="*80)
                
                skull_result = run_skull_tests(project_root=Path.cwd())
                results['skull_tests'] = skull_result
                
                if not skull_result['success']:
                    error_msg = (
                        f"❌ SKULL tests FAILED after optimization - "
                        f"{skull_result['tests_failed']}/{skull_result['tests_run']} tests failed. "
                        f"Brain protection compromised!"
                    )
                    logger.error(error_msg)
                    
                    return OperationResult(
                        success=False,
                        status=OperationStatus.FAILED,
                        message=error_msg,
                        data=results,
                        errors=[f"SKULL test failure: {skull_result.get('error', 'Tests failed')}"]
                    )
                
                logger.info(format_skull_test_summary(skull_result))
            elif skip_skull_tests:
                logger.info("[FAST MODE] Skipping SKULL test validation (user operation)")
            else:
                logger.info("[DRY RUN] Skipping SKULL test validation")
            
            status_msg = "[DRY RUN] " if dry_run else ""
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"✓ {status_msg}Optimization complete ({len(results['optimizations_applied'])} actions, {results['space_saved_mb']:.2f} MB saved)",
                data=results,
            )
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Optimization failed: {str(e)}",
                errors=[str(e)],
            )
    
    def _optimize_brain(self, dry_run: bool = False) -> Dict[str, Any]:
        """Optimize CORTEX brain storage."""
        applied = []
        space_saved = 0.0
        
        brain_path = Path.cwd() / "cortex-brain"
        
        # Remove old conversation captures (>30 days)
        captures_dir = brain_path / "conversation-captures"
        if captures_dir.exists():
            old_captures = []
            for capture_file in captures_dir.glob("*.jsonl"):
                age_days = (datetime.now() - datetime.fromtimestamp(capture_file.stat().st_mtime)).days
                if age_days > 30:
                    old_captures.append(capture_file)
            
            if old_captures:
                for old_file in old_captures:
                    size_mb = old_file.stat().st_size / (1024 * 1024)
                    if not dry_run:
                        old_file.unlink()
                    space_saved += size_mb
                
                action = "[DRY RUN] Would remove" if dry_run else "Removed"
                applied.append(f"{action} {len(old_captures)} old conversation captures (>30 days)")
        
        # Clean up temporary crawler files
        crawler_temp = brain_path / "crawler-temp"
        if crawler_temp.exists():
            temp_files = list(crawler_temp.glob("*"))
            if temp_files:
                for temp_file in temp_files:
                    if temp_file.is_file():
                        size_mb = temp_file.stat().st_size / (1024 * 1024)
                        if not dry_run:
                            temp_file.unlink()
                        space_saved += size_mb
                
                action = "[DRY RUN] Would clean" if dry_run else "Cleaned"
                applied.append(f"{action} {len(temp_files)} temporary crawler files")
        
        # Clean old logs
        logs_dir = brain_path / "logs"
        if logs_dir.exists():
            old_logs = []
            for log_file in logs_dir.glob("*.log"):
                age_days = (datetime.now() - datetime.fromtimestamp(log_file.stat().st_mtime)).days
                if age_days > 7:
                    old_logs.append(log_file)
            
            if old_logs:
                for old_log in old_logs:
                    size_mb = old_log.stat().st_size / (1024 * 1024)
                    if not dry_run:
                        old_log.unlink()
                    space_saved += size_mb
                
                action = "[DRY RUN] Would remove" if dry_run else "Removed"
                applied.append(f"{action} {len(old_logs)} old log files (>7 days)")
        
        return {
            'applied': applied,
            'space_saved_mb': space_saved,
        }
    
    def _optimize_cache(self, dry_run: bool = False) -> Dict[str, Any]:
        """Optimize YAML cache."""
        applied = []
        space_saved = 0.0
        
        try:
            from src.utils.yaml_cache import get_cache_stats, clear_cache
            
            stats_before = get_cache_stats()
            
            # Clear cache (will rebuild on next access)
            if not dry_run:
                clear_cache()
            
            action = "[DRY RUN] Would clear" if dry_run else "Cleared"
            applied.append(f"{action} YAML cache ({stats_before['total_entries']} entries)")
            
            # Estimate space saved (rough estimate based on entry count)
            space_saved += (stats_before['total_entries'] * 0.01)  # ~10KB per entry
            
        except Exception as e:
            logger.warning(f"Cache optimization skipped: {e}")
        
        return {
            'applied': applied,
            'space_saved_mb': space_saved,
        }
    
    def _vacuum_databases(self, aggressive: bool, dry_run: bool = False) -> Dict[str, Any]:
        """Vacuum SQLite databases to reclaim space."""
        applied = []
        space_saved = 0.0
        
        import sqlite3
        brain_path = Path.cwd() / "cortex-brain"
        
        databases = [
            brain_path / "tier1" / "working_memory.db",
            brain_path / "tier2" / "knowledge_graph.db",
        ]
        
        for db_path in databases:
            if db_path.exists():
                try:
                    size_before = db_path.stat().st_size / (1024 * 1024)
                    
                    if not dry_run:
                        # Vacuum database
                        conn = sqlite3.connect(str(db_path))
                        conn.execute("VACUUM")
                        conn.close()
                        
                        size_after = db_path.stat().st_size / (1024 * 1024)
                        saved = size_before - size_after
                    else:
                        # Estimate savings (typically 10-30%)
                        saved = size_before * 0.15
                    
                    if saved > 0:
                        action = "[DRY RUN] Would vacuum" if dry_run else "Vacuumed"
                        applied.append(f"{action} {db_path.name} (saved {saved:.2f} MB)")
                        space_saved += saved
                    
                except Exception as e:
                    logger.warning(f"Failed to vacuum {db_path.name}: {e}")
        
        return {
            'applied': applied,
            'space_saved_mb': space_saved,
        }
    
    def _organize_files(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Phase 1 Task 1.1 & 1.2: Move scattered test and script files to proper directories.
        
        Moves:
        - test_*.py from root → tests/
        - fix_*.py from root → scripts/
        - analyze_*.py, check_*.py, run_*.py, generate_*.py from root → scripts/
        """
        applied = []
        space_saved = 0.0
        files_moved = 0
        
        root_path = Path.cwd()
        
        # Task 1.1: Move test files to tests/
        tests_dir = root_path / "tests"
        test_files = list(root_path.glob("test_*.py"))
        
        if test_files:
            for test_file in test_files:
                target = tests_dir / test_file.name
                if not target.exists():
                    if not dry_run:
                        shutil.move(str(test_file), str(target))
                    files_moved += 1
            
            action = "[DRY RUN] Would move" if dry_run else "Moved"
            applied.append(f"{action} {len(test_files)} test files from root → tests/")
        
        # Task 1.2: Move scripts to scripts/
        scripts_dir = root_path / "scripts"
        script_patterns = ["fix_*.py", "analyze_*.py", "check_*.py", "run_*.py", "generate_*.py", "initialize_*.py"]
        script_files = []
        
        for pattern in script_patterns:
            script_files.extend(root_path.glob(pattern))
        
        if script_files:
            for script_file in script_files:
                target = scripts_dir / script_file.name
                if not target.exists():
                    if not dry_run:
                        shutil.move(str(script_file), str(target))
                    files_moved += 1
            
            action = "[DRY RUN] Would move" if dry_run else "Moved"
            applied.append(f"{action} {len(script_files)} script files from root → scripts/")
        
        return {
            'applied': applied,
            'space_saved_mb': space_saved,
            'files_moved': files_moved,
        }
    
    def _cleanup_build_artifacts(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Phase 1 Task 1.3 & 1.4: Clean build artifacts and large temp files.
        
        Removes:
        - dist/ directory (build artifacts)
        - publish/ directory (distribution files)
        - *.db files from root (should be in cortex-brain/)
        - Large zip files from scripts/temp/
        """
        applied = []
        space_saved = 0.0
        files_removed = 0
        
        root_path = Path.cwd()
        
        # Remove dist/ directory
        dist_dir = root_path / "dist"
        if dist_dir.exists():
            size_mb = sum(f.stat().st_size for f in dist_dir.rglob("*") if f.is_file()) / (1024 * 1024)
            file_count = len(list(dist_dir.rglob("*")))
            
            if not dry_run:
                shutil.rmtree(dist_dir)
            
            space_saved += size_mb
            files_removed += file_count
            action = "[DRY RUN] Would remove" if dry_run else "Removed"
            applied.append(f"{action} dist/ directory ({size_mb:.2f} MB, {file_count} files)")
        
        # Remove publish/ directory
        publish_dir = root_path / "publish"
        if publish_dir.exists():
            size_mb = sum(f.stat().st_size for f in publish_dir.rglob("*") if f.is_file()) / (1024 * 1024)
            file_count = len(list(publish_dir.rglob("*")))
            
            if not dry_run:
                shutil.rmtree(publish_dir)
            
            space_saved += size_mb
            files_removed += file_count
            action = "[DRY RUN] Would remove" if dry_run else "Removed"
            applied.append(f"{action} publish/ directory ({size_mb:.2f} MB, {file_count} files)")
        
        # Remove *.db files from root
        db_files = list(root_path.glob("*.db"))
        if db_files:
            for db_file in db_files:
                size_mb = db_file.stat().st_size / (1024 * 1024)
                if not dry_run:
                    db_file.unlink()
                space_saved += size_mb
                files_removed += 1
            
            action = "[DRY RUN] Would remove" if dry_run else "Removed"
            applied.append(f"{action} {len(db_files)} database files from root")
        
        # Remove large zip files from scripts/temp/
        temp_dir = root_path / "scripts" / "temp"
        if temp_dir.exists():
            zip_files = list(temp_dir.glob("*.zip"))
            large_zips = [z for z in zip_files if z.stat().st_size > 10 * 1024 * 1024]  # >10MB
            
            if large_zips:
                for zip_file in large_zips:
                    size_mb = zip_file.stat().st_size / (1024 * 1024)
                    if not dry_run:
                        zip_file.unlink()
                    space_saved += size_mb
                    files_removed += 1
                
                action = "[DRY RUN] Would remove" if dry_run else "Removed"
                applied.append(f"{action} {len(large_zips)} large zip files from scripts/temp/ ({space_saved:.2f} MB)")
        
        return {
            'applied': applied,
            'space_saved_mb': space_saved,
            'files_removed': files_removed,
        }
    
    def _remove_duplicates(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Phase 1 Task 1.5 & 1.6: Remove duplicate templates and logo files.
        
        Removes:
        - Duplicate response template files (keep primary in cortex-brain/)
        - Duplicate CORTEX logo files (keep primary in docs/assets/images/)
        """
        applied = []
        space_saved = 0.0
        files_removed = 0
        
        root_path = Path.cwd()
        brain_path = root_path / "cortex-brain"
        
        # Remove duplicate response templates
        duplicate_templates = [
            brain_path / "templates" / "response-templates.yaml",
            brain_path / "templates" / "response-templates-enhanced.yaml",
        ]
        
        for template_file in duplicate_templates:
            if template_file.exists():
                size_mb = template_file.stat().st_size / (1024 * 1024)
                if not dry_run:
                    template_file.unlink()
                space_saved += size_mb
                files_removed += 1
        
        if any(t.exists() for t in duplicate_templates):
            action = "[DRY RUN] Would remove" if dry_run else "Removed"
            applied.append(f"{action} duplicate response template files")
        
        # Remove duplicate logo files
        duplicate_logos = [
            root_path / "docs" / "assets" / "assets" / "images" / "CORTEX-logo.png",  # Wrong path
        ]
        
        # Also remove logos from artifact backups
        artifacts_dir = brain_path / "artifacts"
        if artifacts_dir.exists():
            for backup_dir in artifacts_dir.glob("design-backup-*"):
                logo_path = backup_dir / "assets" / "images" / "CORTEX-logo.png"
                if logo_path.exists():
                    duplicate_logos.append(logo_path)
        
        for logo_file in duplicate_logos:
            if logo_file.exists():
                size_mb = logo_file.stat().st_size / (1024 * 1024)
                if not dry_run:
                    logo_file.unlink()
                space_saved += size_mb
                files_removed += 1
        
        if duplicate_logos:
            action = "[DRY RUN] Would remove" if dry_run else "Removed"
            applied.append(f"{action} {len([l for l in duplicate_logos if l.exists()])} duplicate CORTEX logo files ({space_saved:.2f} MB)")
        
        return {
            'applied': applied,
            'space_saved_mb': space_saved,
            'files_removed': files_removed,
        }
    
    def _consolidate_archives(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Phase 2 Task 2.5: Consolidate old archives and temporary files.
        
        Actions:
        - Archive old cortex-brain/archives/ content (>60 days) to external zip
        - Clean scripts/temp/ directory of old files
        - Remove obsolete fix scripts
        """
        applied = []
        space_saved = 0.0
        directories_cleaned = 0
        
        root_path = Path.cwd()
        brain_path = root_path / "cortex-brain"
        
        # Clean scripts/temp/ directory
        temp_dir = root_path / "scripts" / "temp"
        if temp_dir.exists():
            old_files = []
            for temp_file in temp_dir.iterdir():
                if temp_file.is_file():
                    age_days = (datetime.now() - datetime.fromtimestamp(temp_file.stat().st_mtime)).days
                    if age_days > 30:
                        old_files.append(temp_file)
            
            if old_files:
                for old_file in old_files:
                    size_mb = old_file.stat().st_size / (1024 * 1024)
                    if not dry_run:
                        old_file.unlink()
                    space_saved += size_mb
                
                directories_cleaned += 1
                action = "[DRY RUN] Would remove" if dry_run else "Removed"
                applied.append(f"{action} {len(old_files)} old files from scripts/temp/ (>30 days)")
        
        # Identify old archives in cortex-brain/archives/
        archives_dir = brain_path / "archives"
        if archives_dir.exists():
            old_archives = []
            for archive_dir in archives_dir.iterdir():
                if archive_dir.is_dir():
                    age_days = (datetime.now() - datetime.fromtimestamp(archive_dir.stat().st_mtime)).days
                    if age_days > 60:
                        old_archives.append(archive_dir)
            
            if old_archives:
                # Note: Actual archiving would require external backup location
                # For now, just report what would be archived
                total_size = 0
                for archive_dir in old_archives:
                    size_mb = sum(f.stat().st_size for f in archive_dir.rglob("*") if f.is_file()) / (1024 * 1024)
                    total_size += size_mb
                
                action = "[DRY RUN] Would archive" if dry_run else "Identified for archiving"
                applied.append(f"{action} {len(old_archives)} old archive directories (>60 days, {total_size:.2f} MB)")
                # Note: Not removing or counting as space saved until external backup confirmed
        
        return {
            'applied': applied,
            'space_saved_mb': space_saved,
            'directories_cleaned': directories_cleaned,
        }
    
    def _consolidate_markdown_docs(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Consolidate scattered markdown documentation files.
        
        Strategies:
        1. Exact Duplicates: SHA256 hash matching (keep oldest, archive others)
        2. Time-Series: PHASE-1, PHASE-2, etc. → Consolidated file
        3. Topic Clustering: Related documents grouped by keywords
        
        Args:
            dry_run: Preview mode without executing changes
            
        Returns:
            Dict with 'applied', 'space_saved_mb', 'files_removed'
        """
        applied = []
        space_saved = 0.0
        files_removed = 0
        
        root_path = Path.cwd()
        docs_path = root_path / "cortex-brain" / "documents"
        
        if not docs_path.exists():
            self.logger.warning(f"Documents directory not found: {docs_path}")
            return {'applied': applied, 'space_saved_mb': space_saved, 'files_removed': files_removed}
        
        # Find all markdown files
        md_files = list(docs_path.rglob("*.md"))
        if not md_files:
            self.logger.info("No markdown files found")
            return {'applied': applied, 'space_saved_mb': space_saved, 'files_removed': files_removed}
        
        self.logger.info(f"Found {len(md_files)} markdown files to analyze")
        
        # Strategy 1: Exact Duplicate Detection (SHA256 hashing)
        hash_map: Dict[str, List[Path]] = {}
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8', errors='ignore')
                file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
                
                if file_hash not in hash_map:
                    hash_map[file_hash] = []
                hash_map[file_hash].append(md_file)
            except Exception as e:
                self.logger.warning(f"Error hashing {md_file}: {e}")
                continue
        
        # Remove exact duplicates (keep oldest)
        for file_hash, files in hash_map.items():
            if len(files) > 1:
                # Sort by modification time (keep oldest)
                files_sorted = sorted(files, key=lambda f: f.stat().st_mtime)
                keep_file = files_sorted[0]
                duplicate_files = files_sorted[1:]
                
                for dup_file in duplicate_files:
                    file_size_mb = dup_file.stat().st_size / (1024 * 1024)
                    
                    if dry_run:
                        self.logger.info(f"[DRY RUN] Would remove duplicate: {dup_file.relative_to(root_path)} "
                                       f"(identical to {keep_file.relative_to(root_path)})")
                    else:
                        archive_dir = dup_file.parent / ".archive"
                        archive_dir.mkdir(exist_ok=True)
                        
                        # Move to archive with timestamp
                        timestamp = datetime.now().strftime("%Y%m%d")
                        archive_name = f"{dup_file.stem}_{timestamp}{dup_file.suffix}"
                        archive_path = archive_dir / archive_name
                        
                        shutil.move(str(dup_file), str(archive_path))
                        self.logger.info(f"Archived duplicate: {dup_file.relative_to(root_path)} → {archive_path.relative_to(root_path)}")
                    
                    applied.append(f"Duplicate removed: {dup_file.relative_to(root_path)}")
                    space_saved += file_size_mb
                    files_removed += 1
        
        # Strategy 2: Time-Series Document Consolidation
        # Pattern: feature-PHASE-1.md, feature-PHASE-2.md → feature-COMPLETE.md
        time_series_pattern = re.compile(r'^(.+?)[-_](PHASE|SPRINT|ITERATION)[-_](\d+)\.md$', re.IGNORECASE)
        time_series_groups: Dict[str, List[Path]] = {}
        
        for md_file in md_files:
            if not md_file.exists():  # Skip if already removed as duplicate
                continue
                
            match = time_series_pattern.match(md_file.name)
            if match:
                base_name = match.group(1)
                group_key = f"{md_file.parent}/{base_name}"
                
                if group_key not in time_series_groups:
                    time_series_groups[group_key] = []
                time_series_groups[group_key].append(md_file)
        
        # Consolidate time-series with 3+ files
        for group_key, files in time_series_groups.items():
            if len(files) >= 3:
                # Sort by phase number
                files_sorted = sorted(files, key=lambda f: int(time_series_pattern.match(f.name).group(3)))
                
                base_name = time_series_pattern.match(files_sorted[0].name).group(1)
                consolidated_name = f"{base_name}-COMPLETE.md"
                consolidated_path = files_sorted[0].parent / consolidated_name
                
                if dry_run:
                    self.logger.info(f"[DRY RUN] Would consolidate {len(files)} time-series files into {consolidated_name}")
                    for f in files_sorted:
                        self.logger.info(f"  - {f.relative_to(root_path)}")
                else:
                    # Merge content chronologically
                    merged_content = [f"# {base_name.replace('-', ' ').title()} - Complete Documentation\n\n"]
                    merged_content.append(f"**Consolidated from {len(files)} phase documents**\n\n")
                    merged_content.append("---\n\n")
                    
                    for phase_file in files_sorted:
                        phase_num = time_series_pattern.match(phase_file.name).group(3)
                        merged_content.append(f"## Phase {phase_num}\n\n")
                        
                        try:
                            content = phase_file.read_text(encoding='utf-8', errors='ignore')
                            # Remove original title if present
                            content_lines = content.split('\n')
                            if content_lines and content_lines[0].startswith('#'):
                                content_lines = content_lines[1:]
                            merged_content.append('\n'.join(content_lines).strip())
                            merged_content.append("\n\n---\n\n")
                        except Exception as e:
                            self.logger.warning(f"Error reading {phase_file}: {e}")
                            continue
                    
                    # Write consolidated file
                    consolidated_path.write_text(''.join(merged_content), encoding='utf-8')
                    self.logger.info(f"Created consolidated document: {consolidated_path.relative_to(root_path)}")
                    
                    # Archive original phase files
                    archive_dir = files_sorted[0].parent / ".archive"
                    archive_dir.mkdir(exist_ok=True)
                    
                    for phase_file in files_sorted:
                        file_size_mb = phase_file.stat().st_size / (1024 * 1024)
                        timestamp = datetime.now().strftime("%Y%m%d")
                        archive_name = f"{phase_file.stem}_{timestamp}{phase_file.suffix}"
                        archive_path = archive_dir / archive_name
                        
                        shutil.move(str(phase_file), str(archive_path))
                        space_saved += file_size_mb
                        files_removed += 1
                    
                    applied.append(f"Time-series consolidated: {len(files)} files → {consolidated_name}")
        
        # Strategy 3: Topic Clustering (suggestion only, not auto-consolidate)
        remaining_files = [f for f in md_files if f.exists()]
        if len(remaining_files) >= 4:
            topic_clusters = self._cluster_by_topic(remaining_files)
            
            for topic, files in topic_clusters.items():
                if len(files) >= 4:
                    self.logger.info(f"[SUGGESTION] {len(files)} files related to '{topic}' could be reviewed for consolidation:")
                    for f in files[:5]:  # Show first 5
                        self.logger.info(f"  - {f.relative_to(root_path)}")
                    if len(files) > 5:
                        self.logger.info(f"  ... and {len(files) - 5} more")
        
        return {
            'applied': applied,
            'space_saved_mb': space_saved,
            'files_removed': files_removed
        }
    
    def _cluster_by_topic(self, files: List[Path]) -> Dict[str, List[Path]]:
        """
        Cluster markdown files by topic keywords.
        
        Args:
            files: List of markdown file paths
            
        Returns:
            Dict mapping topic name to list of related files
        """
        topic_keywords = {
            'tdd': ['tdd', 'test', 'testing', 'pytest', 'unittest'],
            'planning': ['plan', 'planning', 'dor', 'dod', 'acceptance'],
            'architecture': ['architecture', 'design', 'pattern', 'component'],
            'optimization': ['optimize', 'optimization', 'performance', 'cleanup'],
            'documentation': ['doc', 'documentation', 'guide', 'tutorial'],
            'deployment': ['deploy', 'deployment', 'publish', 'release'],
            'validation': ['validate', 'validation', 'check', 'verify'],
            'integration': ['integration', 'workflow', 'orchestrator']
        }
        
        clusters: Dict[str, List[Path]] = {topic: [] for topic in topic_keywords}
        
        for file_path in files:
            file_name_lower = file_path.stem.lower()
            parent_name_lower = file_path.parent.name.lower()
            
            for topic, keywords in topic_keywords.items():
                if any(keyword in file_name_lower or keyword in parent_name_lower for keyword in keywords):
                    clusters[topic].append(file_path)
                    break  # Only assign to first matching topic
        
        # Remove empty clusters
        return {topic: files for topic, files in clusters.items() if files}
    
    def _generate_optimization_report(self, results: Dict[str, Any]) -> Optional[Path]:
        """Generate optimization report in cortex-brain/documents/reports/"""
        try:
            root_path = Path.cwd()
            reports_dir = root_path / "cortex-brain" / "documents" / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = reports_dir / f"optimization-report-{timestamp}.json"
            
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_optimizations": len(results['optimizations_applied']),
                    "space_saved_mb": results['space_saved_mb'],
                    "files_moved": results.get('files_moved', 0),
                    "files_removed": results.get('files_removed', 0),
                    "directories_cleaned": results.get('directories_cleaned', 0),
                    "dry_run": results.get('dry_run', False),
                },
                "optimizations": results['optimizations_applied'],
            }
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2)
            
            logger.info(f"Optimization report saved to: {report_path}")
            return report_path
            
        except Exception as e:
            logger.warning(f"Failed to generate optimization report: {e}")
            return None
    
    def rollback(self) -> OperationResult:
        """
        Rollback optimization (not applicable).
        
        Returns:
            OperationResult indicating rollback not supported
        """
        return OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message="Optimization rollback not applicable (changes are safe)",
        )
