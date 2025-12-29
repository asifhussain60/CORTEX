"""
Vacuum Orchestrator - Deep codebase cleanup with AST intelligence and SQLite optimization.

Performs comprehensive cleanup operations using semantic analysis to identify and remove
duplicates, orphaned code, unused imports, and optimize database storage.

Integration:
- BaseOrchestrator: Phase management, error handling, lifecycle
- ASTEngine: Semantic code analysis for duplicate detection
- SQLite: Database vacuum operations on Tier 1/2/3 databases

Copyright © 2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
import sqlite3

from src.orchestration_4_0.base.base_orchestrator import BaseOrchestrator
from src.operations.modules.analysis.ast_engine import ASTEngine
from src.operations.modules.analysis.deduplication_analyzer import DeduplicationAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class VacuumResult:
    """Results of vacuum operation."""
    success: bool
    data: Dict[str, Any]
    message: str = ""
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class VacuumOrchestrator(BaseOrchestrator):
    """
    Orchestrate deep codebase cleanup operations.
    
    Phases:
    1. sqlite_vacuum - Compact Tier 1/2/3 databases
    2. duplicate_detection - Find semantic duplicates (AST-powered)
    3. orphaned_tests - Identify tests without source files
    4. unused_imports - Detect unused import statements
    5. finalization - Generate summary report
    """
    
    def __init__(self, project_root: Path = None):
        """
        Initialize vacuum orchestrator.
        
        Args:
            project_root: Root path of CORTEX project
        """
        super().__init__(name="vacuum", logger=logger)
        
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.cortex_brain = self.project_root / "cortex-brain"
        
        # Initialize AST engine
        self.ast_engine = ASTEngine(self.project_root)
        self.dedup_analyzer = DeduplicationAnalyzer(self.ast_engine)
        
        # Metrics tracking
        self.metrics = {
            'space_saved_bytes': 0,
            'databases_vacuumed': 0,
            'duplicates_found': 0,
            'orphaned_tests': 0,
            'unused_imports': 0,
            'dry_run': True,
            'errors': []
        }
        
        # Database paths
        self.databases = [
            self.cortex_brain / "conversation-history.db",
            self.cortex_brain / "cortex-brain.db",
            self.project_root / "cortex_alerts.db",
            self.project_root / "cortex_metrics.db",
            self.project_root / "cortex_status.db"
        ]
        
    def _setup(self, context: Dict[str, Any]) -> None:
        """Initialize orchestrator resources."""
        self.logger.info("🎭 Orchestrator engaged: VacuumOrchestrator")
        self.logger.info(f"Project root: {self.project_root}")
        
    def _register_phases(self) -> None:
        """Register vacuum phases."""
        self.phase_manager.register_phase("sqlite_vacuum", "SQLite database optimization", required=True)
        self.phase_manager.register_phase("duplicate_detection", "AST-powered duplicate detection", required=False)
        self.phase_manager.register_phase("orphaned_tests", "Orphaned test file identification", required=False)
        self.phase_manager.register_phase("unused_imports", "Unused import detection", required=False)
        self.phase_manager.register_phase("finalization", "Summary report generation", required=True)
        
    def _execute_phase(self, phase_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single vacuum phase.
        
        Args:
            phase_name: Name of phase to execute
            context: Phase execution context
            
        Returns:
            Phase result dictionary
        """
        if phase_name == "sqlite_vacuum":
            return self._run_sqlite_vacuum_phase(context)
        elif phase_name == "duplicate_detection":
            return self._run_duplicate_detection_phase(context)
        elif phase_name == "orphaned_tests":
            return self._run_orphaned_tests_phase(context)
        elif phase_name == "unused_imports":
            return self._run_unused_imports_phase(context)
        elif phase_name == "finalization":
            return self._run_finalization_phase(context)
        else:
            return {'success': False, 'error': f"Unknown phase: {phase_name}"}
            
    def _teardown(self, context: Dict[str, Any]) -> None:
        """Cleanup orchestrator resources."""
        self.logger.info("🎭 Orchestrator completing: VacuumOrchestrator")
        self.logger.info(f"Space saved: {self.metrics['space_saved_bytes']} bytes")
        
    # ========================================================================
    # Phase Implementations
    # ========================================================================
    
    def _run_sqlite_vacuum_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute SQLite VACUUM on all CORTEX databases.
        
        VACUUM rebuilds database files to:
        - Reclaim unused space
        - Reduce fragmentation
        - Improve query performance
        
        Args:
            context: Phase context
            
        Returns:
            Phase result with space saved
        """
        self.logger.info("🎭 Phase transition: START → sqlite_vacuum")
        
        space_saved_total = 0
        databases_vacuumed = 0
        errors = []
        
        for db_path in self.databases:
            if not db_path.exists():
                self.logger.debug(f"Database not found: {db_path}")
                continue
                
            try:
                # Get size before vacuum
                size_before = db_path.stat().st_size
                
                # Execute VACUUM
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("VACUUM")
                conn.commit()
                conn.close()
                
                # Get size after vacuum
                size_after = db_path.stat().st_size
                space_saved = size_before - size_after
                
                if space_saved > 0:
                    self.logger.info(f"✅ Vacuumed {db_path.name}: {space_saved:,} bytes saved")
                    space_saved_total += space_saved
                else:
                    self.logger.debug(f"No space saved for {db_path.name}")
                    
                databases_vacuumed += 1
                
            except Exception as e:
                error_msg = f"Failed to vacuum {db_path.name}: {e}"
                self.logger.warning(error_msg)
                errors.append(error_msg)
                
        self.metrics['space_saved_bytes'] = space_saved_total
        self.metrics['databases_vacuumed'] = databases_vacuumed
        self.metrics['errors'].extend(errors)
        
        return {
            'success': databases_vacuumed > 0,
            'space_saved_bytes': space_saved_total,
            'databases_vacuumed': databases_vacuumed,
            'errors': errors,
            'skipped': False
        }
        
    def _run_duplicate_detection_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect semantic code duplicates using AST analysis.
        
        Uses DeduplicationAnalyzer with 85% similarity threshold and 10-line minimum.
        
        Args:
            context: Phase context with optional similarity_threshold
            
        Returns:
            Phase result with duplicate count
        """
        self.logger.info("🎭 Phase transition: sqlite_vacuum → duplicate_detection")
        
        try:
            # Use DeduplicationAnalyzer
            analysis = self.dedup_analyzer.analyze(target_path=None)
            
            duplicates_found = analysis.get('total_duplicates', 0)
            self.metrics['duplicates_found'] = duplicates_found
            
            if duplicates_found > 0:
                self.logger.info(f"✅ Found {duplicates_found} duplicate code groups")
                for group in analysis.get('duplicate_groups', [])[:5]:  # Show top 5
                    self.logger.info(f"  - {group.similarity_score:.1%} similar, {group.lines_count} lines: {group.recommendation}")
            else:
                self.logger.info("✅ No duplicates found")
                
            return {
                'success': True,
                'duplicates_found': duplicates_found,
                'duplicate_lines': analysis.get('total_duplicate_lines', 0),
                'cleanup_hours': analysis.get('estimated_cleanup_hours', 0.0),
                'skipped': False
            }
            
        except Exception as e:
            error_msg = f"Duplicate detection failed: {e}"
            self.logger.warning(error_msg)
            self.metrics['errors'].append(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'skipped': False
            }
            
    def _run_orphaned_tests_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify test files without corresponding source files.
        
        Args:
            context: Phase context
            
        Returns:
            Phase result with orphaned test count
        """
        self.logger.info("🎭 Phase transition: duplicate_detection → orphaned_tests")
        
        try:
            orphaned_tests = self.ast_engine.find_orphaned_tests()
            
            self.metrics['orphaned_tests'] = len(orphaned_tests)
            
            if orphaned_tests:
                self.logger.info(f"✅ Found {len(orphaned_tests)} orphaned test files")
                for test_file in orphaned_tests[:5]:  # Show top 5
                    self.logger.info(f"  - {test_file}")
            else:
                self.logger.info("✅ No orphaned tests found")
                
            return {
                'success': True,
                'orphaned_tests': len(orphaned_tests),
                'test_files': [str(p) for p in orphaned_tests],
                'skipped': False
            }
            
        except Exception as e:
            error_msg = f"Orphaned test detection failed: {e}"
            self.logger.warning(error_msg)
            self.metrics['errors'].append(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'skipped': False
            }
            
    def _run_unused_imports_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect unused import statements across codebase.
        
        Args:
            context: Phase context
            
        Returns:
            Phase result with unused import count
        """
        self.logger.info("🎭 Phase transition: orphaned_tests → unused_imports")
        
        try:
            unused_imports = self.ast_engine.find_unused_imports()
            
            self.metrics['unused_imports'] = len(unused_imports)
            
            if unused_imports:
                self.logger.info(f"✅ Found {len(unused_imports)} files with unused imports")
                for file_info in unused_imports[:5]:  # Show top 5
                    self.logger.info(f"  - {file_info.get('file', 'unknown')}: {len(file_info.get('imports', []))} unused")
            else:
                self.logger.info("✅ No unused imports found")
                
            return {
                'success': True,
                'unused_imports': len(unused_imports),
                'files': unused_imports,
                'skipped': False
            }
            
        except Exception as e:
            error_msg = f"Unused import detection failed: {e}"
            self.logger.warning(error_msg)
            self.metrics['errors'].append(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'skipped': False
            }
            
    def _run_finalization_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary report and finalize vacuum operation.
        
        Args:
            context: Phase context
            
        Returns:
            Phase result with summary
        """
        self.logger.info("🎭 Phase transition: unused_imports → finalization")
        
        summary = {
            'space_saved_bytes': self.metrics['space_saved_bytes'],
            'space_saved_mb': self.metrics['space_saved_bytes'] / (1024 * 1024),
            'databases_vacuumed': self.metrics['databases_vacuumed'],
            'duplicates_found': self.metrics['duplicates_found'],
            'orphaned_tests': self.metrics['orphaned_tests'],
            'unused_imports': self.metrics['unused_imports'],
            'total_issues': (
                self.metrics['duplicates_found'] +
                self.metrics['orphaned_tests'] +
                self.metrics['unused_imports']
            ),
            'errors': self.metrics['errors']
        }
        
        self.logger.info("=" * 60)
        self.logger.info("VACUUM SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Space saved: {summary['space_saved_mb']:.2f} MB")
        self.logger.info(f"Databases vacuumed: {summary['databases_vacuumed']}")
        self.logger.info(f"Duplicates found: {summary['duplicates_found']}")
        self.logger.info(f"Orphaned tests: {summary['orphaned_tests']}")
        self.logger.info(f"Unused imports: {summary['unused_imports']}")
        self.logger.info(f"Total issues: {summary['total_issues']}")
        if summary['errors']:
            self.logger.warning(f"Errors: {len(summary['errors'])}")
        self.logger.info("=" * 60)
        
        return {
            'success': True,
            'summary': summary,
            'skipped': False
        }
        
    def execute(self, context: Dict[str, Any] = None) -> VacuumResult:
        """
        Execute full vacuum operation.
        
        Args:
            context: Optional execution context
            
        Returns:
            VacuumResult with success status and metrics
        """
        context = context or {}
        
        try:
            # Execute all phases using BaseOrchestrator
            result = super().execute(context)
            
            return VacuumResult(
                success=result.get('success', False),
                data={
                    'space_saved': self.metrics['space_saved_bytes'],
                    'databases_vacuumed': self.metrics['databases_vacuumed'],
                    'duplicates_found': self.metrics['duplicates_found'],
                    'orphaned_tests': self.metrics['orphaned_tests'],
                    'unused_imports': self.metrics['unused_imports']
                },
                message=result.get('message', ''),
                errors=self.metrics['errors']
            )
            
        except Exception as e:
            self.logger.error(f"Vacuum operation failed: {e}", exc_info=True)
            return VacuumResult(
                success=False,
                data={},
                message=f"Vacuum operation failed: {e}",
                errors=[str(e)]
            )
