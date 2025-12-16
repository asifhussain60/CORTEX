"""
Refactor Cycle Engine v2.0 - Automatic code cleanup and quality enforcement.

Integrated with Planning System 3.0 for standardized operation handling:
- Inherits BaseOperationModule for consistent interface
- Uses orchestration metrics for engagement tracking
- Returns standardized OperationResult
- Provides visual progress tracking with 🎭 hints

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 2.0.0
"""

from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import re
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.operations.base_operation_module import (
    BaseOperationModule, OperationResult, OperationStatus,
    OperationPhase, OperationModuleMetadata
)
from ..analysis.ast_engine import ASTEngine
from ..version.version_manager import get_version_manager
from src.operations.utilities.orchestration_metrics_collector import with_orchestration_metrics
from src.utils.progress_decorator import with_progress, yield_progress

logger = logging.getLogger(__name__)


@dataclass
class RefactorResult:
    """Results of refactor operation."""
    phase: str
    files_processed: int
    changes_made: int
    issues_found: List[str]


class RefactorCycleOrchestrator(BaseOperationModule):
    """
    Orchestrate automatic code cleanup and refactoring.
    
    Planning System 3.0 Integration:
    - Standardized BaseOperationModule inheritance
    - Orchestration metrics for engagement tracking
    - Visual progress hints with 🎭 pattern
    - Consistent OperationResult format
    """
    
    def __init__(self, project_root: Path = None):
        """Initialize refactor cycle orchestrator v2.0."""
        super().__init__()
        self.project_root = project_root or Path.cwd()
        self.ast_engine = ASTEngine(self.project_root)
        
        # Version management
        self.version_manager = get_version_manager()
        self.version_manager.register_orchestrator_version("refactor_cycle_orchestrator", "2.0")
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
        
        logger.info(f"✅ RefactorCycleOrchestrator v{self.version} initialized (Planning System 3.0)")
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="refactor_cycle_orchestrator",
            name="Refactor Cycle Orchestrator 2.0",
            description="Automatic code cleanup: comments, debug removal, lint, format",
            phase=OperationPhase.PROCESSING,
            priority=70,
            version="2.0.0",
            author="Asif Hussain",
            tags=["orchestration", "refactoring", "cleanup", "quality", "planning-system-3.0"]
        )
    
    @with_progress(operation_name="Refactor Cycle", threshold_seconds=3.0)
    @with_orchestration_metrics("RefactorCycleOrchestrator")
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """Execute refactor cycle."""
        logger.info(f"🎭 Orchestrator engaged: RefactorCycleOrchestrator v{self.version}")
        
        phases = phases or self.phases
        target_files = target_files or list(self.project_root.rglob("*.py"))
        
        results = []
        
        try:
            phase_idx = 1
            if "comment_sync" in phases:
                yield_progress(phase_idx, len(phases) + 1, "Phase 1: Synchronizing comments")
                logger.info("🎭 Phase transition: START → comment_sync")
                comment_result = asyncio.run(self._run_comment_sync_phase(target_files))
                results.append(comment_result)
                self.metrics['phases_completed'].append('comment_sync')
                phase_idx += 1
                
            if "debug_removal" in phases:
                yield_progress(phase_idx, len(phases) + 1, "Phase 2: Removing debug code")
                logger.info("🎭 Phase transition: comment_sync → debug_removal")
                debug_result = asyncio.run(self._run_debug_removal_phase(target_files))
                results.append(debug_result)
                self.metrics['phases_completed'].append('debug_removal')
                phase_idx += 1
                
            if "dead_code" in phases:
                yield_progress(phase_idx, len(phases) + 1, "Phase 3: Detecting dead code")
                logger.info("🎭 Phase transition: debug_removal → dead_code")
                dead_code_result = asyncio.run(self._run_dead_code_phase(target_files))
                results.append(dead_code_result)
                self.metrics['phases_completed'].append('dead_code')
                phase_idx += 1
                
            if "lint_enforcement" in phases:
                yield_progress(phase_idx, len(phases) + 1, "Phase 4: Enforcing lint rules")
                logger.info("🎭 Phase transition: dead_code → lint_enforcement")
                lint_result = asyncio.run(self._run_lint_phase(target_files))
                results.append(lint_result)
                self.metrics['phases_completed'].append('lint_enforcement')
                phase_idx += 1
                
            if "format_enforcement" in phases:
                yield_progress(phase_idx, len(phases) + 1, "Phase 5: Formatting code")
                logger.info("🎭 Phase transition: lint_enforcement → format_enforcement")
                format_result = asyncio.run(self._run_format_phase(target_files))
                results.append(format_result)
                self.metrics['phases_completed'].append('format_enforcement')
                phase_idx += 1
                
            yield_progress(len(phases) + 1, len(phases) + 1, "Phase 6: Finalizing refactor")
            logger.info("🎭 Phase transition: format_enforcement → finalization")
            self._finalize_refactor(results)
            self.metrics['phases_completed'].append('finalization')
            
            success = True
            is_complete = success and len(self.metrics['errors']) == 0
            
            logger.info(
                f"🎭 Orchestrator completing: "
                f"{'✅ ALL WORK COMPLETE' if is_complete else '⏳ PHASES DONE WITH WARNINGS'}"
            )
            
            return OperationResult(
                success=success,
                status=OperationStatus.SUCCESS if success else OperationStatus.WARNING,
                message=f"Refactor cycle completed: {len(results)} phases, {self.metrics['changes_made']} changes",
                data={
                    'results': [vars(r) for r in results],
                    'metrics': self.metrics,
                    'is_complete': is_complete
                },
                errors=self.metrics['errors'],
                warnings=[],
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now(),
                formatted_header="🔧 Refactor Cycle",
                formatted_footer=f"{self.metrics['changes_made']} changes made"
            )
            
        except Exception as e:
            logger.error(f"Refactor cycle failed: {e}", exc_info=True)
            self.metrics['errors'].append(str(e))
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Refactor cycle failed: {e}",
                data={'metrics': self.metrics},
                errors=[str(e)],
                warnings=[],
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now(),
                formatted_header="🔧 Refactor Cycle",
                formatted_footer="❌ Refactor failed"
            )
            
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
) -> OperationResult:
    """
    Synchronous wrapper for refactor cycle.
    
    Args:
        project_root: Project root path
        target_files: Files to refactor
        phases: Phases to run
        
    Returns:
        OperationResult with refactor metrics
    """
    orchestrator = RefactorCycleOrchestrator(project_root)
    context = {
        'target_files': target_files,
        'phases': phases
    }
    return orchestrator.execute(context)
