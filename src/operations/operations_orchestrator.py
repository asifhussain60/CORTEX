"""
Universal Operations Orchestrator - CORTEX 2.0

This orchestrator coordinates ALL CORTEX operations (setup, story refresh, cleanup, etc.)
by executing modules in dependency-resolved order across defined phases.

Design Principles:
    - Single orchestrator for all operations
    - YAML-driven operation definitions
    - Topological sort for dependency resolution
    - Phase-based execution with priorities
    - Comprehensive error handling and rollback

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationPhase,
    OperationStatus,
    OperationResult,
    ExecutionMode
)
from src.operations.dry_run_mixin import DryRunOrchestratorMixin

logger = logging.getLogger(__name__)


@dataclass
class OperationExecutionReport:
    """
    Report of operation execution.
    
    Universal report for ANY operation (setup, cleanup, story refresh, etc.)
    
    Attributes:
        operation_id: Operation identifier (e.g., 'environment_setup')
        operation_name: Human-readable name
        success: Overall operation success
        modules_executed: List of module IDs that ran
        modules_succeeded: List of module IDs that succeeded
        modules_failed: List of module IDs that failed
        modules_skipped: List of module IDs that were skipped
        module_results: Detailed results for each module
        total_duration_seconds: Total execution time
        timestamp: When operation completed
        context: Final shared context dictionary
        errors: List of error messages
    """
    operation_id: str
    operation_name: str
    success: bool
    modules_executed: List[str] = field(default_factory=list)
    modules_succeeded: List[str] = field(default_factory=list)
    modules_failed: List[str] = field(default_factory=list)
    modules_skipped: List[str] = field(default_factory=list)
    module_results: Dict[str, OperationResult] = field(default_factory=dict)
    total_duration_seconds: float = 0.0
    timestamp: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()


class OperationsOrchestrator(DryRunOrchestratorMixin):
    """
    Universal orchestrator for ALL CORTEX operations.
    
    Coordinates module execution for any operation defined in cortex-operations.yaml:
        - environment_setup (setup command)
        - refresh_cortex_story (story refresh command)
        - workspace_cleanup (cleanup command)
        - update_documentation (docs command)
        - And any future operations
    
    Key Features:
        - Dependency resolution via topological sort
        - Phase-based execution (PRE_VALIDATION → FINALIZATION)
        - Priority ordering within phases
        - Error handling with rollback
        - Comprehensive reporting
        - Dry-run support (preview mode)
        - Copyright header rendering
    
    Example Usage:
        # Setup operation (live mode)
        orchestrator = OperationsOrchestrator(
            operation_id="environment_setup",
            modules=[platform_mod, vision_mod, brain_mod]
        )
        report = orchestrator.execute_operation(
            context={'project_root': Path('...')},
            execution_mode=ExecutionMode.LIVE
        )
        
        # Cleanup operation (dry-run mode)
        orchestrator = OperationsOrchestrator(
            operation_id="workspace_cleanup",
            modules=[scan_mod, cleanup_mod]
        )
        report = orchestrator.execute_operation(
            context={'project_root': Path('...')},
            execution_mode=ExecutionMode.DRY_RUN  # Preview only
        )
    """
    
    def __init__(
        self,
        operation_id: str,
        operation_name: str,
        modules: List[BaseOperationModule],
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize orchestrator for an operation.
        
        Args:
            operation_id: Operation identifier (e.g., 'refresh_cortex_story')
            operation_name: Human-readable name (e.g., 'Refresh CORTEX Story')
            modules: List of modules to execute
            context: Initial shared context dictionary
        """
        self.operation_id = operation_id
        self.operation_name = operation_name
        self.modules = modules
        self.context = context or {}
        self.executed_modules: List[str] = []
    
    def execute_operation(
        self,
        context: Optional[Dict[str, Any]] = None,
        execution_mode: ExecutionMode = ExecutionMode.LIVE
    ) -> OperationExecutionReport:
        """
        Execute the operation by running all modules in dependency-resolved order.
        
        Args:
            context: Additional context to merge with initialization context
            execution_mode: LIVE (apply changes) or DRY_RUN (preview only)
        
        Returns:
            OperationExecutionReport with execution details
        """
        start_time = datetime.now()
        
        # Merge context
        if context:
            self.context.update(context)
        
        # Store execution mode in context
        self.context['execution_mode'] = execution_mode
        
        # Apply execution mode to all modules
        self.apply_mode_to_modules(self.modules, execution_mode)
        
        mode_str = "DRY RUN" if execution_mode == ExecutionMode.DRY_RUN else "LIVE"
        logger.info(f"Starting operation: {self.operation_name} ({self.operation_id}) - {mode_str} mode")
        logger.info(f"Modules to execute: {len(self.modules)}")
        
        # Initialize report
        report = OperationExecutionReport(
            operation_id=self.operation_id,
            operation_name=self.operation_name,
            success=False,
            context=self.context
        )
        
        try:
            # Sort modules by phase and dependency
            sorted_modules = self._sort_modules()
            logger.info(f"Module execution order: {[m.metadata.module_id for m in sorted_modules]}")
            
            # Execute modules in order
            for module in sorted_modules:
                module_id = module.metadata.module_id
                
                try:
                    # Check if module should run
                    if not module.should_run(self.context):
                        logger.info(f"Skipping module: {module_id} (should_run returned False)")
                        report.modules_skipped.append(module_id)
                        continue
                    
                    # Validate prerequisites
                    is_valid, issues = module.validate_prerequisites(self.context)
                    if not is_valid:
                        logger.error(f"Prerequisites not met for {module_id}: {issues}")
                        report.modules_failed.append(module_id)
                        report.errors.extend(issues)
                        
                        if not module.metadata.optional:
                            logger.error(f"Required module {module_id} failed prerequisite check")
                            report.success = False
                            self._rollback_modules(report)
                            return report
                        else:
                            logger.warning(f"Optional module {module_id} skipped due to failed prerequisites")
                            report.modules_skipped.append(module_id)
                            continue
                    
                    # Execute module
                    logger.info(f"Executing module: {module_id} ({module.metadata.name})")
                    logger.info(f"  Phase: {module.metadata.phase.value}, Priority: {module.metadata.priority}")
                    
                    result = module.execute(self.context)
                    report.module_results[module_id] = result
                    report.modules_executed.append(module_id)
                    self.executed_modules.append(module_id)
                    
                    if result.success:
                        logger.info(f"Module {module_id} succeeded: {result.message}")
                        report.modules_succeeded.append(module_id)
                        
                        # Merge module output data into shared context for next modules
                        if result.data:
                            self.context.update(result.data)
                            logger.debug(f"Merged {len(result.data)} context items from {module_id}")
                    else:
                        logger.error(f"Module {module_id} failed: {result.message}")
                        report.modules_failed.append(module_id)
                        report.errors.extend(result.errors)
                        
                        if not module.metadata.optional:
                            logger.error(f"Required module {module_id} failed, rolling back")
                            report.success = False
                            self._rollback_modules(report)
                            return report
                        else:
                            logger.warning(f"Optional module {module_id} failed, continuing")
                
                except Exception as e:
                    logger.error(f"Exception in module {module_id}: {e}", exc_info=True)
                    report.modules_failed.append(module_id)
                    report.errors.append(f"Exception in {module_id}: {str(e)}")
                    
                    if not module.metadata.optional:
                        logger.error(f"Required module {module_id} raised exception, rolling back")
                        report.success = False
                        self._rollback_modules(report)
                        return report
            
            # Operation completed successfully
            report.success = len(report.modules_failed) == 0
            
            if report.success:
                logger.info(f"Operation {self.operation_name} completed successfully")
                logger.info(f"  Modules executed: {len(report.modules_executed)}")
                logger.info(f"  Modules succeeded: {len(report.modules_succeeded)}")
            else:
                logger.warning(f"Operation {self.operation_name} completed with failures")
                logger.warning(f"  Modules failed: {len(report.modules_failed)}")
        
        except Exception as e:
            logger.error(f"Fatal error in operation {self.operation_name}: {e}", exc_info=True)
            report.success = False
            report.errors.append(f"Fatal error: {str(e)}")
            self._rollback_modules(report)
        
        finally:
            # Calculate duration
            end_time = datetime.now()
            report.total_duration_seconds = (end_time - start_time).total_seconds()
            report.timestamp = end_time
            
            logger.info(f"Operation {self.operation_name} finished in {report.total_duration_seconds:.2f}s")
        
        return report
    
    def _sort_modules(self) -> List[BaseOperationModule]:
        """
        Sort modules by phase, dependencies, and priority.
        
        Uses topological sort to resolve dependencies within phases.
        
        Returns:
            Sorted list of modules ready for execution
        """
        # Group modules by phase
        phases: Dict[OperationPhase, List[BaseOperationModule]] = {}
        for module in self.modules:
            phase = module.metadata.phase
            if phase not in phases:
                phases[phase] = []
            phases[phase].append(module)
        
        # Sort modules within each phase
        sorted_modules = []
        for phase in sorted(phases.keys(), key=lambda p: p.order):
            phase_modules = phases[phase]
            
            # Topological sort by dependencies
            sorted_phase = self._topological_sort(phase_modules)
            
            # Sort by priority within dependency order
            sorted_phase.sort(key=lambda m: m.metadata.priority)
            
            sorted_modules.extend(sorted_phase)
        
        return sorted_modules
    
    def _topological_sort(self, modules: List[BaseOperationModule]) -> List[BaseOperationModule]:
        """
        Perform topological sort on modules based on dependencies.
        
        Args:
            modules: List of modules to sort
        
        Returns:
            Sorted list respecting dependency order
        """
        # Build adjacency list
        module_map = {m.metadata.module_id: m for m in modules}
        in_degree = {m.metadata.module_id: 0 for m in modules}
        adj_list = {m.metadata.module_id: [] for m in modules}
        
        for module in modules:
            for dep in module.metadata.dependencies:
                if dep in module_map:
                    adj_list[dep].append(module.metadata.module_id)
                    in_degree[module.metadata.module_id] += 1
        
        # Kahn's algorithm
        queue = [mid for mid, deg in in_degree.items() if deg == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(module_map[current])
            
            for neighbor in adj_list[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(modules):
            logger.warning("Circular dependency detected, using original order")
            return modules
        
        return result
    
    def _rollback_modules(self, report: OperationExecutionReport) -> None:
        """
        Rollback executed modules in reverse order.
        
        Args:
            report: Operation report to update with rollback status
        """
        logger.warning("Rolling back executed modules")
        
        # Rollback in reverse order
        for module_id in reversed(self.executed_modules):
            try:
                module = next((m for m in self.modules if m.metadata.module_id == module_id), None)
                if module:
                    logger.info(f"Rolling back module: {module_id}")
                    success = module.rollback(self.context)
                    if not success:
                        logger.error(f"Rollback failed for module: {module_id}")
                        report.errors.append(f"Rollback failed: {module_id}")
            except Exception as e:
                logger.error(f"Exception during rollback of {module_id}: {e}", exc_info=True)
                report.errors.append(f"Rollback exception in {module_id}: {str(e)}")
    
    def get_module_execution_order(self) -> List[str]:
        """
        Get the execution order of modules without running them.
        
        Returns:
            List of module IDs in execution order
        """
        sorted_modules = self._sort_modules()
        return [m.metadata.module_id for m in sorted_modules]
