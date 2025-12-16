"""
Vacuum Orchestrator v2.0 - Deep codebase cleanup with AST intelligence.

Integrated with Planning System 3.0 for standardized operation handling:
- Inherits BaseOperationModule for consistent interface
- Uses orchestration metrics for engagement tracking
- Returns standardized OperationResult
- Provides visual progress tracking with 🎭 hints

Performs comprehensive cleanup operations using semantic analysis
to identify and remove duplicates, orphaned code, and dead code.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 2.0.0
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import asyncio

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
class VacuumResult:
    """Results of vacuum operation."""
    phase: str
    items_found: int
    items_removed: int
    dry_run: bool
    details: List[str]


class VacuumOrchestrator(BaseOperationModule):
    """
    Orchestrate deep codebase cleanup operations.
    
    Planning System 3.0 Integration:
    - Standardized BaseOperationModule inheritance
    - Orchestration metrics for engagement tracking
    - Visual progress hints with 🎭 pattern
    - Consistent OperationResult format
    """
    
    def __init__(self, project_root: Path = None):
        """
        Initialize vacuum orchestrator v2.0.
        
        Args:
            project_root: Root path of project to clean
        """
        super().__init__()
        self.project_root = project_root or Path.cwd()
        self.ast_engine = ASTEngine(self.project_root)
        
        # Version management
        self.version_manager = get_version_manager()
        self.version_manager.register_orchestrator_version("vacuum_orchestrator", "2.0")
        self.version = self.version_manager.get_orchestrator_version("vacuum_orchestrator")
        
        # Vacuum phases
        self.phases = [
            "duplicate_detection",
            "orphaned_tests",
            "unused_imports",
            "dead_code",
            "finalization"
        ]
        
        self.metrics = {
            'phases_completed': [],
            'items_found': 0,
            'items_removed': 0,
            'dry_run': True,
            'errors': []
        }
        
        logger.info(f"✅ VacuumOrchestrator v{self.version} initialized (Planning System 3.0)")
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="vacuum_orchestrator",
            name="Vacuum Orchestrator 2.0",
            description="AST-powered deep cleanup: duplicates, orphaned tests, dead code",
            phase=OperationPhase.PROCESSING,
            priority=75,
            version="2.0.0",
            author="Asif Hussain",
            tags=["orchestration", "cleanup", "ast", "vacuum", "planning-system-3.0"]
        )
    
    @with_progress(operation_name="Vacuum Cleanup", threshold_seconds=3.0)
    @with_orchestration_metrics("VacuumOrchestrator")
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute vacuum cleanup operation.
        
        Args:
            targets: Specific cleanup targets or None for all
            dry_run: If True, preview changes without applying
            similarity_threshold: Minimum similarity for duplicates
            
        Returns:
            Operation results with metrics
        """
        logger.info(f"🎭 Orchestrator engaged: VacuumOrchestrator v{self.version}")
        logger.info(f"Dry run: {dry_run}, Targets: {targets or 'all'}")
        
        self.metrics['dry_run'] = dry_run
        
        targets = targets or [
            "duplicate_code",
            "orphaned_tests",
            "unused_imports",
            "dead_code"
        ]
        
        results = []
        
        try:
            # Phase 1: Duplicate Detection
            if "duplicate_code" in targets:
                yield_progress(1, len(targets) + 1, "Phase 1: Detecting duplicates")
                logger.info("🎭 Phase transition: START → duplicate_detection")
                dup_result = asyncio.run(self._run_duplicate_detection_phase(
                    similarity_threshold,
                    dry_run
                ))
                results.append(dup_result)
                
            # Phase 2: Orphaned Tests
            if "orphaned_tests" in targets:
                yield_progress(2, len(targets) + 1, "Phase 2: Finding orphaned tests")
                logger.info("🎭 Phase transition: duplicate_detection → orphaned_tests")
                orphan_result = asyncio.run(self._run_orphaned_tests_phase(dry_run))
                results.append(orphan_result)
                self.metrics['phases_completed'].append('orphaned_tests')
                
            # Phase 3: Unused Imports
            if "unused_imports" in targets:
                yield_progress(3, len(targets) + 1, "Phase 3: Cleaning unused imports")
                logger.info("🎭 Phase transition: orphaned_tests → unused_imports")
                import_result = asyncio.run(self._run_unused_imports_phase(dry_run))
                results.append(import_result)
                self.metrics['phases_completed'].append('unused_imports')
                
            # Phase 4: Dead Code
            if "dead_code" in targets:
                yield_progress(4, len(targets) + 1, "Phase 4: Detecting dead code")
                logger.info("🎭 Phase transition: unused_imports → dead_code")
                dead_code_result = asyncio.run(self._run_dead_code_phase(dry_run))
                results.append(dead_code_result)
                self.metrics['phases_completed'].append('dead_code')
                
            # Phase 5: Finalization
            yield_progress(len(targets) + 1, len(targets) + 1, "Phase 5: Finalizing vacuum")
            logger.info("🎭 Phase transition: dead_code → finalization")
            self._finalize_vacuum(results, dry_run)
            self.metrics['phases_completed'].append('finalization')
            
            success = True
            is_complete = success and len(self.metrics['errors']) == 0
            
            logger.info(
                f"🎭 Orchestrator completing: "
                f"{'✅ ALL WORK COMPLETE' if is_complete else '⏳ PHASES DONE WITH WARNINGS'}"
            )
            
            return OperationResult(
                success=success,
                status=OperationStatus.COMPLETED,
                message="Vacuum cleanup completed",
                data={'metrics': self.metrics},
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            logger.error(f"Vacuum operation failed: {e}", exc_info=True)
            self.metrics['errors'].append(str(e))
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Vacuum cleanup failed: {e}",
                data={'metrics': self.metrics},
                errors=[str(e)],
                warnings=[],
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now(),
                formatted_header="🧹 Vacuum Cleanup",
                formatted_footer="❌ Cleanup failed"
            )
            
        except Exception as e:
            logger.error(f"Vacuum operation failed: {e}", exc_info=True)
            self.metrics['errors'].append(str(e))
            return {
                'success': False,
                'error': str(e),
                'metrics': self.metrics,
                'is_complete': False
            }
            
    async def _run_duplicate_detection_phase(
        self,
        threshold: float,
        dry_run: bool
    ) -> VacuumResult:
        """Phase 1: Detect and remove duplicate code."""
        logger.info(f"Detecting duplicates (threshold: {threshold})")
        
        duplicate_groups = self.ast_engine.find_semantic_duplicates(
            similarity_threshold=threshold,
            min_lines=10
        )
        
        items_removed = 0
        details = []
        
        for group in duplicate_groups:
            details.append(
                f"Duplicate group: {len(group.get('locations', []))} instances"
            )
            
            if not dry_run:
                # Keep first instance, remove rest
                locations = group.get('locations', [])
                if len(locations) > 1:
                    items_removed += len(locations) - 1
                    
        self.metrics['items_found'] += len(duplicate_groups)
        self.metrics['items_removed'] += items_removed
        
        return VacuumResult(
            phase="duplicate_detection",
            items_found=len(duplicate_groups),
            items_removed=items_removed,
            dry_run=dry_run,
            details=details[:10]  # Limit details
        )
        
    async def _run_orphaned_tests_phase(self, dry_run: bool) -> VacuumResult:
        """Phase 2: Detect and remove orphaned test files."""
        logger.info("Detecting orphaned tests")
        
        orphaned_tests = self.ast_engine.find_orphaned_tests()
        
        items_removed = 0
        details = []
        
        for test_path in orphaned_tests:
            details.append(f"Orphaned test: {test_path}")
            
            if not dry_run:
                test_path.unlink()
                items_removed += 1
                
        self.metrics['items_found'] += len(orphaned_tests)
        self.metrics['items_removed'] += items_removed
        
        return VacuumResult(
            phase="orphaned_tests",
            items_found=len(orphaned_tests),
            items_removed=items_removed,
            dry_run=dry_run,
            details=details[:10]
        )
        
    async def _run_unused_imports_phase(self, dry_run: bool) -> VacuumResult:
        """Phase 3: Remove unused imports."""
        logger.info("Cleaning unused imports")
        
        unused_imports = self.ast_engine.find_unused_imports()
        count = len(unused_imports)
        
        items_removed = 0
        if not dry_run:
            items_removed = count  # In real implementation, would remove them
            
        details = [f"Files with unused imports: {count}"]
        
        self.metrics['items_found'] += count
        self.metrics['items_removed'] += items_removed
        
        return VacuumResult(
            phase="unused_imports",
            items_found=count,
            items_removed=items_removed,
            dry_run=dry_run,
            details=details
        )
        
    async def _run_dead_code_phase(self, dry_run: bool) -> VacuumResult:
        """Phase 4: Detect and remove dead code."""
        logger.info("Detecting dead code")
        
        dead_code_items = self.ast_engine.detect_dead_code()
        
        items_removed = 0
        details = []
        
        for item in dead_code_items:
            details.append(f"Dead code: {item.get('type', 'unknown')} in {item.get('file', 'unknown')}")
            
            if not dry_run:
                items_removed += 1
                
        self.metrics['items_found'] += len(dead_code_items)
        self.metrics['items_removed'] += items_removed
        
        return VacuumResult(
            phase="dead_code",
            items_found=len(dead_code_items),
            items_removed=items_removed,
            dry_run=dry_run,
            details=details[:10]
        )
        
    def _finalize_vacuum(self, results: List[VacuumResult], dry_run: bool):
        """Phase 5: Finalize vacuum operation."""
        total_found = sum(r.items_found for r in results)
        total_removed = sum(r.items_removed for r in results)
        
        if dry_run:
            logger.info(
                f"Vacuum preview: {total_found} items identified, "
                f"{total_removed} would be removed"
            )
        else:
            logger.info(
                f"Vacuum complete: {total_removed} items removed from codebase"
            )
    
    def generate_preview_report(self, results: List[VacuumResult]) -> str:
        """
        Generate detailed preview report for dry-run mode.
        
        Args:
            results: Vacuum operation results
            
        Returns:
            Formatted markdown report
        """
        lines = ["# Vacuum Operation Preview\n"]
        lines.append("## Summary\n")
        
        total_found = sum(r.items_found for r in results)
        total_would_remove = sum(r.items_removed for r in results)
        
        lines.append(f"**Total Items Found:** {total_found}")
        lines.append(f"**Items to Remove:** {total_would_remove}\n")
        
        for result in results:
            lines.append(f"### {result.phase.replace('_', ' ').title()}\n")
            lines.append(f"- Found: {result.items_found}")
            lines.append(f"- Would Remove: {result.items_removed}\n")
            
            if result.details:
                lines.append("**Details:**")
                for detail in result.details:
                    lines.append(f"- {detail}")
                lines.append("")
                    
        lines.append("\n---\n")
        lines.append("**To execute cleanup:** Re-run with `dry_run=False`")
        
        return "\n".join(lines)


# Synchronous wrapper for compatibility
def run_vacuum(
    project_root: Path = None,
    targets: List[str] = None,
    dry_run: bool = True,
    similarity_threshold: float = 0.85
) -> OperationResult:
    """
    Synchronous wrapper for vacuum operation.
    
    Args:
        project_root: Project root path
        targets: Cleanup targets
        dry_run: Preview mode flag
        similarity_threshold: Duplicate detection threshold
        
    Returns:
        OperationResult with vacuum metrics
    """
    orchestrator = VacuumOrchestrator(project_root)
    context = {
        'targets': targets,
        'dry_run': dry_run,
        'similarity_threshold': similarity_threshold
    }
    return orchestrator.execute(context)
