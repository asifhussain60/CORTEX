"""
Universal Operations Orchestrator - CORTEX 2.0

This orchestrator coordinates ALL CORTEX operations (setup, story refresh, cleanup, etc.)
by executing modules in dependency-resolved order across defined phases.

Design Principles:
    - Single orchestrator for all operations
    - YAML-driven operation definitions
    - Topological sort for dependency resolution
    - Phase-based execution with priorities
    - Parallel execution of independent modules
    - Comprehensive error handling and rollback

Author: Asif Hussain
Version: 2.1 (Parallel Execution Optimization)
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationPhase,
    OperationStatus,
    OperationResult,
    ExecutionMode
)
from src.cortex_agents.learning_capture_agent import capture_operation_learning

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
        parallel_execution_count: Number of modules executed in parallel
        parallel_groups_count: Number of parallel execution groups
        time_saved_seconds: Estimated time saved by parallel execution
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
    parallel_execution_count: int = 0
    parallel_groups_count: int = 0
    time_saved_seconds: float = 0.0
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()


class OperationsOrchestrator:
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
        - Copyright header rendering
    
    Example Usage:
        # Setup operation
        orchestrator = OperationsOrchestrator(
            operation_id="environment_setup",
            modules=[platform_mod, vision_mod, brain_mod]
        )
        report = orchestrator.execute_operation(
            context={'project_root': Path('...')}
        )
        
        # Cleanup operation
        orchestrator = OperationsOrchestrator(
            operation_id="workspace_cleanup",
            modules=[scan_mod, cleanup_mod]
        )
        report = orchestrator.execute_operation(
            context={'project_root': Path('...')}
        )
    """
    
    def __init__(
        self,
        operation_id: str,
        operation_name: str,
        modules: List[BaseOperationModule],
        context: Optional[Dict[str, Any]] = None,
        max_parallel_workers: int = 4
    ):
        """
        Initialize orchestrator for an operation.
        
        Args:
            operation_id: Operation identifier (e.g., 'refresh_cortex_story')
            operation_name: Human-readable name (e.g., 'Refresh CORTEX Story')
            modules: List of modules to execute
            context: Initial shared context dictionary
            max_parallel_workers: Maximum number of modules to execute in parallel (default: 4)
        """
        self.operation_id = operation_id
        self.operation_name = operation_name
        self.modules = modules
        self.context = context or {}
        self.max_parallel_workers = max_parallel_workers
        self.executed_modules: List[str] = []
    
    def execute_operation(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> OperationExecutionReport:
        """
        Execute the operation by running all modules in dependency-resolved order.
        
        Args:
            context: Additional context to merge with initialization context
        
        Returns:
            OperationExecutionReport with execution details
        """
        start_time = datetime.now()
        
        # Merge context
        if context:
            self.context.update(context)
        
        # Store execution mode in context (always LIVE)
        self.context['execution_mode'] = ExecutionMode.LIVE
        
        logger.info(f"Starting operation: {self.operation_name} ({self.operation_id}) - LIVE mode")
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
            
            # Group modules for parallel execution
            module_groups = self._group_independent_modules(sorted_modules)
            logger.info(f"Parallel execution groups: {len(module_groups)}")
            report.parallel_groups_count = len(module_groups)
            
            # Track time saved by parallel execution
            sequential_time_estimate = 0.0
            parallel_time_actual = 0.0
            
            # Execute module groups (each group runs in parallel)
            for group_idx, module_group in enumerate(module_groups):
                group_start = datetime.now()
                
                if len(module_group) == 1:
                    # Single module - execute directly
                    module = module_group[0]
                    result = self._execute_single_module(module, report)
                    
                    if result is False:  # Critical failure
                        return report
                else:
                    # Multiple modules - execute in parallel
                    logger.info(f"Executing group {group_idx + 1}/{len(module_groups)}: "
                              f"{len(module_group)} modules in parallel")
                    report.parallel_execution_count += len(module_group)
                    
                    success = self._execute_parallel_group(module_group, report)
                    
                    if not success:  # Critical failure in parallel group
                        return report
                
                # Track timing
                group_duration = (datetime.now() - group_start).total_seconds()
                parallel_time_actual += group_duration
                
                # Estimate sequential time (sum of all module times in group)
                # For parallel groups, sequential would be sum of all times
                # For single module, no savings
                if len(module_group) > 1:
                    # Parallel execution: all modules ran concurrently
                    # Sequential would be: module1_time + module2_time + ...
                    # We approximate each module took group_duration (they ran concurrently)
                    sequential_time_estimate += group_duration * len(module_group)
                else:
                    # Single module: no parallel benefit
                    sequential_time_estimate += group_duration
            
            # Calculate time saved
            report.time_saved_seconds = max(0, sequential_time_estimate - parallel_time_actual)
            
            # Operation completed successfully if no REQUIRED modules failed
            # Optional module failures are acceptable
            required_failures = [
                module_id for module_id in report.modules_failed
                if not any(m.metadata.module_id == module_id and m.metadata.optional 
                          for m in self.modules)
            ]
            report.success = len(required_failures) == 0
            
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
            
            # Capture learning from operation result
            try:
                learning_event = capture_operation_learning(
                    operation_name=self.operation_name,
                    result=report,
                    context={
                        'operation_id': self.operation_id,
                        'execution_mode': self.execution_mode.value if hasattr(self, 'execution_mode') else 'live',
                        'modules_count': len(self.modules)
                    }
                )
                if learning_event:
                    logger.info(f"Learning captured from {self.operation_name}")
            except Exception as e:
                logger.warning(f"Failed to capture learning: {e}")
        
        return report
    
    def _execute_single_module(
        self, 
        module: BaseOperationModule, 
        report: OperationExecutionReport
    ) -> bool:
        """
        Execute a single module and update report.
        
        Args:
            module: Module to execute
            report: Report to update with results
        
        Returns:
            True if execution should continue, False if critical failure occurred
        """
        module_id = module.metadata.module_id
        
        try:
            # Check if module should run
            if not module.should_run(self.context):
                logger.info(f"Skipping module: {module_id} (should_run returned False)")
                report.modules_skipped.append(module_id)
                return True
            
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
                    return False
                else:
                    logger.warning(f"Optional module {module_id} skipped due to failed prerequisites")
                    report.modules_skipped.append(module_id)
                    return True
            
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
                return True
            else:
                logger.error(f"Module {module_id} failed: {result.message}")
                report.modules_failed.append(module_id)
                report.errors.extend(result.errors)
                
                if not module.metadata.optional:
                    logger.error(f"Required module {module_id} failed, rolling back")
                    report.success = False
                    self._rollback_modules(report)
                    return False
                else:
                    logger.warning(f"Optional module {module_id} failed, continuing")
                    return True
        
        except Exception as e:
            logger.error(f"Exception in module {module_id}: {e}", exc_info=True)
            report.modules_failed.append(module_id)
            report.errors.append(f"Exception in {module_id}: {str(e)}")
            
            if not module.metadata.optional:
                logger.error(f"Required module {module_id} raised exception, rolling back")
                report.success = False
                self._rollback_modules(report)
                return False
            
            return True
    
    def _execute_parallel_group(
        self,
        modules: List[BaseOperationModule],
        report: OperationExecutionReport
    ) -> bool:
        """
        Execute a group of modules in parallel.
        
        Args:
            modules: List of modules to execute concurrently
            report: Report to update with results
        
        Returns:
            True if execution should continue, False if critical failure occurred
        """
        with ThreadPoolExecutor(max_workers=self.max_parallel_workers) as executor:
            # Submit all modules for execution
            future_to_module: Dict[Future, BaseOperationModule] = {
                executor.submit(self._execute_module_worker, module): module
                for module in modules
            }
            
            # Collect results as they complete
            critical_failure = False
            
            for future in as_completed(future_to_module):
                module = future_to_module[future]
                module_id = module.metadata.module_id
                
                try:
                    result, should_continue = future.result()
                    
                    if result:  # Module executed (not skipped)
                        report.module_results[module_id] = result
                        report.modules_executed.append(module_id)
                        self.executed_modules.append(module_id)
                        
                        if result.success:
                            logger.info(f"Module {module_id} succeeded: {result.message}")
                            report.modules_succeeded.append(module_id)
                            
                            # Merge module output data into shared context
                            # Note: In parallel execution, context updates are merged after all modules complete
                            if result.data:
                                self.context.update(result.data)
                                logger.debug(f"Merged {len(result.data)} context items from {module_id}")
                        else:
                            logger.error(f"Module {module_id} failed: {result.message}")
                            report.modules_failed.append(module_id)
                            report.errors.extend(result.errors)
                            
                            if not module.metadata.optional:
                                critical_failure = True
                    
                    if not should_continue:
                        critical_failure = True
                
                except Exception as e:
                    logger.error(f"Exception in parallel module {module_id}: {e}", exc_info=True)
                    report.modules_failed.append(module_id)
                    report.errors.append(f"Exception in {module_id}: {str(e)}")
                    
                    if not module.metadata.optional:
                        critical_failure = True
            
            # If critical failure occurred, rollback
            if critical_failure:
                logger.error("Critical failure in parallel group, rolling back")
                report.success = False
                self._rollback_modules(report)
                return False
        
        return True
    
    def _execute_module_worker(
        self, 
        module: BaseOperationModule
    ) -> Tuple[Optional[OperationResult], bool]:
        """
        Worker function for executing a module in a thread.
        
        Args:
            module: Module to execute
        
        Returns:
            Tuple of (result, should_continue) where:
                - result: OperationResult if module executed, None if skipped
                - should_continue: False if critical failure, True otherwise
        """
        module_id = module.metadata.module_id
        
        try:
            # Check if module should run
            if not module.should_run(self.context):
                logger.info(f"Skipping module: {module_id} (should_run returned False)")
                return None, True
            
            # Validate prerequisites
            is_valid, issues = module.validate_prerequisites(self.context)
            if not is_valid:
                logger.error(f"Prerequisites not met for {module_id}: {issues}")
                
                if not module.metadata.optional:
                    return OperationResult(
                        success=False,
                        status=OperationStatus.FAILED,
                        message=f"Prerequisites not met: {', '.join(issues)}",
                        errors=issues
                    ), False
                else:
                    logger.warning(f"Optional module {module_id} skipped due to failed prerequisites")
                    return None, True
            
            # Execute module
            logger.info(f"Executing module: {module_id} ({module.metadata.name}) [parallel]")
            logger.info(f"  Phase: {module.metadata.phase.value}, Priority: {module.metadata.priority}")
            
            result = module.execute(self.context)
            return result, True
        
        except Exception as e:
            logger.error(f"Exception in module worker {module_id}: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Exception: {str(e)}",
                errors=[str(e)]
            ), not module.metadata.optional
    
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
    
    def _group_independent_modules(
        self, 
        modules: List[BaseOperationModule]
    ) -> List[List[BaseOperationModule]]:
        """
        Group modules into batches that can be executed in parallel.
        
        Modules can run in parallel if they:
        1. Have no dependencies on each other
        2. Are in the same phase
        3. Have already had their dependencies satisfied
        
        Args:
            modules: List of modules (assumed to be in dependency-resolved order)
        
        Returns:
            List of module groups, where each group can be executed in parallel
        """
        if not modules:
            return []
        
        # Build dependency graph
        module_map = {m.metadata.module_id: m for m in modules}
        
        # Track which modules have been scheduled
        scheduled: Set[str] = set()
        groups: List[List[BaseOperationModule]] = []
        
        while len(scheduled) < len(modules):
            # Find modules whose dependencies are all satisfied
            current_group = []
            
            for module in modules:
                module_id = module.metadata.module_id
                
                # Skip if already scheduled
                if module_id in scheduled:
                    continue
                
                # Check if all dependencies are satisfied
                dependencies_met = all(
                    dep in scheduled or dep not in module_map
                    for dep in module.metadata.dependencies
                )
                
                if dependencies_met:
                    current_group.append(module)
            
            # If no modules can be scheduled, we have a circular dependency
            if not current_group:
                logger.error("Circular dependency detected in module grouping")
                # Return remaining modules as individual groups to proceed
                remaining = [m for m in modules if m.metadata.module_id not in scheduled]
                groups.extend([[m] for m in remaining])
                break
            
            # Add current group and mark as scheduled
            groups.append(current_group)
            scheduled.update(m.metadata.module_id for m in current_group)
        
        return groups
    
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
