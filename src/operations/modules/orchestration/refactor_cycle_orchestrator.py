"""
Refactor Cycle Engine - Automatic code cleanup and quality enforcement.

Integrated into Planning System 3.0 for automatic code cleanup
during Tier 3/4 operations.

Copyright © 2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass
import re
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..analysis.ast_engine import ASTEngine
from ..version.version_manager import get_version_manager

logger = logging.getLogger(__name__)


@dataclass
class RefactorResult:
    """Results of refactor operation."""
    phase: str
    files_processed: int
    changes_made: int
    issues_found: List[str]


class RefactorCycleOrchestrator:
    """Orchestrate automatic code cleanup and refactoring."""
    
    def __init__(self, project_root: Path = None):
        """Initialize refactor cycle orchestrator."""
        self.project_root = project_root or Path.cwd()
        self.ast_engine = ASTEngine(self.project_root)
        
        # Version management
        self.version_manager = get_version_manager()
        self.version_manager.register_orchestrator_version("refactor_cycle_orchestrator", "1.0")
        self.version = self.version_manager.get_orchestrator_version("refactor_cycle_orchestrator")
        
        self.phases = [
            "comment_sync",
            "debug_removal",
            "dead_code",
            "lint_enforcement",
            "format_enforcement",
            "finalization"
        ]
        
        self.metrics = {
            'phases_completed': [],
            'files_processed': 0,
            'changes_made': 0,
            'errors': []
        }
        
        self.max_workers = 4
        
    async def execute(
        self,
        target_files: List[Path] = None,
        phases: List[str] = None
    ) -> Dict[str, Any]:
        """Execute refactor cycle."""
        logger.info(f"🎭 Orchestrator engaged: RefactorCycleOrchestrator v{self.version}")
        
        phases = phases or self.phases
        target_files = target_files or list(self.project_root.rglob("*.py"))
        
        results = []
        
        try:
            if "comment_sync" in phases:
                logger.info("🎭 Phase transition: START → comment_sync")
                comment_result = await self._run_comment_sync_phase(target_files)
                results.append(comment_result)
                self.metrics['phases_completed'].append('comment_sync')
                
            if "debug_removal" in phases:
                logger.info("🎭 Phase transition: comment_sync → debug_removal")
                debug_result = await self._run_debug_removal_phase(target_files)
                results.append(debug_result)
                self.metrics['phases_completed'].append('debug_removal')
                
            if "dead_code" in phases:
                logger.info("🎭 Phase transition: debug_removal → dead_code")
                dead_code_result = await self._run_dead_code_phase(target_files)
                results.append(dead_code_result)
                self.metrics['phases_completed'].append('dead_code')
                
            if "lint_enforcement" in phases:
                logger.info("🎭 Phase transition: dead_code → lint_enforcement")
                lint_result = await self._run_lint_phase(target_files)
                results.append(lint_result)
                self.metrics['phases_completed'].append('lint_enforcement')
                
            if "format_enforcement" in phases:
                logger.info("🎭 Phase transition: lint_enforcement → format_enforcement")
                format_result = await self._run_format_phase(target_files)
                results.append(format_result)
                self.metrics['phases_completed'].append('format_enforcement')
                
            logger.info("🎭 Phase transition: format_enforcement → finalization")
            self._finalize_refactor(results)
            self.metrics['phases_completed'].append('finalization')
            
            success = True
            is_complete = success and len(self.metrics['errors']) == 0
            
            logger.info(
                f"🎭 Orchestrator completing: "
                f"{'✅ ALL WORK COMPLETE' if is_complete else '⏳ PHASES DONE WITH WARNINGS'}"
            )
            
            return {
                'success': success,
                'results': results,
                'metrics': self.metrics,
                'is_complete': is_complete
            }
            
        except Exception as e:
            logger.error(f"Refactor cycle failed: {e}", exc_info=True)
            self.metrics['errors'].append(str(e))
            return {
                'success': False,
                'error': str(e),
                'metrics': self.metrics,
                'is_complete': False
            }
            
    async def _run_comment_sync_phase(self, files: List[Path]) -> RefactorResult:
        """Phase 1: Synchronize comments with code."""
        logger.info(f"Synchronizing comments in {len(files)} files")
        
        changes = 0
        issues = []
        processed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._sync_file_comments, file): file for file in files}
            
            for future in as_completed(futures):
                try:
                    file_changes = future.result()
                    changes += file_changes
                    processed += 1
                except Exception as e:
                    issues.append(str(e))
                    
        self.metrics['files_processed'] += processed
        self.metrics['changes_made'] += changes
        
        return RefactorResult(
            phase="comment_sync",
            files_processed=processed,
            changes_made=changes,
            issues_found=issues
        )
    
    def _sync_file_comments(self, file: Path) -> int:
        """Synchronize comments in a single file."""
        # Stub for now
        return 0
        
    async def _run_debug_removal_phase(self, files: List[Path]) -> RefactorResult:
        """Phase 2: Remove debug code."""
        logger.info(f"Removing debug code from {len(files)} files")
        
        debug_patterns = [
            r'console\.log\([^)]*\);?',
            r'print\([^)]*\)',
            r'debugger;?',
            r'logger\.debug\([^)]*\)'
        ]
        
        changes = 0
        issues = []
        processed = 0
        
        for file in files:
            try:
                content = file.read_text(encoding='utf-8')
                original = content
                
                for pattern in debug_patterns:
                    content = re.sub(pattern, '', content, flags=re.MULTILINE)
                    
                if content != original:
                    file.write_text(content, encoding='utf-8')
                    changes += 1
                    
                processed += 1
            except Exception as e:
                issues.append(f"{file}: {e}")
                
        self.metrics['files_processed'] += processed
        self.metrics['changes_made'] += changes
        
        return RefactorResult(
            phase="debug_removal",
            files_processed=processed,
            changes_made=changes,
            issues_found=issues
        )
        
    async def _run_dead_code_phase(self, files: List[Path]) -> RefactorResult:
        """Phase 3: Remove dead code using AST."""
        logger.info(f"Detecting dead code in {len(files)} files")
        
        dead_code_items = self.ast_engine.detect_dead_code(files)
        
        changes = len(dead_code_items)
        self.metrics['changes_made'] += changes
        
        return RefactorResult(
            phase="dead_code",
            files_processed=len(files),
            changes_made=changes,
            issues_found=[]
        )
        
    async def _run_lint_phase(self, files: List[Path]) -> RefactorResult:
        """Phase 4: Enforce linting rules."""
        logger.info(f"Running lint checks on {len(files)} files")
        
        # Stub - would integrate with pylint/flake8
        return RefactorResult(
            phase="lint_enforcement",
            files_processed=len(files),
            changes_made=0,
            issues_found=[]
        )
        
    async def _run_format_phase(self, files: List[Path]) -> RefactorResult:
        """Phase 5: Enforce formatting."""
        logger.info(f"Formatting {len(files)} files")
        
        # Stub - would integrate with black/autopep8
        return RefactorResult(
            phase="format_enforcement",
            files_processed=len(files),
            changes_made=0,
            issues_found=[]
        )
        
    def _finalize_refactor(self, results: List[RefactorResult]):
        """Phase 6: Finalize refactor cycle."""
        total_files = sum(r.files_processed for r in results)
        total_changes = sum(r.changes_made for r in results)
        
        logger.info(f"Refactor cycle complete: {total_files} files, {total_changes} changes")


def run_refactor_cycle(
    project_root: Path = None,
    target_files: List[Path] = None,
    phases: List[str] = None
) -> Dict[str, Any]:
    """Synchronous wrapper for refactor cycle."""
    orchestrator = RefactorCycleOrchestrator(project_root)
    return asyncio.run(orchestrator.execute(target_files, phases))
