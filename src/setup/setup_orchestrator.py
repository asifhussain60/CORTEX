"""
Setup Orchestrator - Coordinates all setup modules

SOLID Principles:
- Single Responsibility: Only orchestrates module execution
- Open/Closed: Add modules via registration, no code changes
- Dependency Inversion: Depends on BaseSetupModule abstraction

Responsibilities:
1. Discover and register setup modules
2. Resolve dependencies between modules
3. Execute modules in correct phase/priority order
4. Handle failures and rollback
5. Provide comprehensive setup report

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Type
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from .base_setup_module import (
    BaseSetupModule,
    SetupModuleMetadata,
    SetupResult,
    SetupStatus,
    SetupPhase
)


class SetupOrchestrator:
    """
    Orchestrates execution of all setup modules.
    
    Features:
    - Automatic module discovery
    - Dependency resolution
    - Phase-based execution
    - Failure handling with rollback
    - Comprehensive reporting
    
    Usage:
        orchestrator = SetupOrchestrator()
        
        # Register modules
        orchestrator.register_module(PlatformSetupModule())
        orchestrator.register_module(VisionAPISetupModule())
        
        # Execute setup
        context = {'project_root': Path('/path/to/project')}
        results = orchestrator.execute_setup(context)
        
        # Check results
        if results.overall_success:
            print("✅ Setup complete!")
        else:
            print(f"❌ Setup failed: {results.summary}")
    """
    
    def __init__(self):
        """Initialize orchestrator."""
        self.logger = logging.getLogger(__name__)
        self._modules: Dict[str, BaseSetupModule] = {}
        self._execution_order: List[str] = []
        self._results: List[SetupResult] = []
    
    def register_module(self, module: BaseSetupModule) -> bool:
        """
        Register a setup module.
        
        Args:
            module: Instance of BaseSetupModule
        
        Returns:
            True if registered successfully
        """
        module_id = module.metadata.module_id
        
        if module_id in self._modules:
            self.logger.warning(f"Module already registered: {module_id}")
            return False
        
        self._modules[module_id] = module
        self.logger.info(f"✓ Registered module: {module_id} ({module.metadata.name})")
        
        # Invalidate execution order (will be recalculated)
        self._execution_order = []
        
        return True
    
    def register_modules(self, modules: List[BaseSetupModule]) -> int:
        """
        Register multiple modules.
        
        Args:
            modules: List of module instances
        
        Returns:
            Number of modules successfully registered
        """
        count = 0
        for module in modules:
            if self.register_module(module):
                count += 1
        return count
    
    def get_module(self, module_id: str) -> Optional[BaseSetupModule]:
        """Get a registered module by ID."""
        return self._modules.get(module_id)
    
    def get_all_modules(self) -> List[BaseSetupModule]:
        """Get all registered modules."""
        return list(self._modules.values())
    
    def _resolve_execution_order(self) -> List[str]:
        """
        Resolve module execution order based on phases, priorities, and dependencies.
        
        Returns:
            List of module IDs in execution order
        
        Raises:
            ValueError: If circular dependencies detected
        """
        if self._execution_order:
            return self._execution_order
        
        # Group modules by phase
        by_phase: Dict[SetupPhase, List[BaseSetupModule]] = defaultdict(list)
        for module in self._modules.values():
            by_phase[module.metadata.phase].append(module)
        
        # Sort within each phase by priority and dependencies
        execution_order = []
        
        for phase in sorted(SetupPhase, key=lambda p: p.value):
            if phase not in by_phase:
                continue
            
            phase_modules = by_phase[phase]
            
            # Topological sort for dependencies
            sorted_modules = self._topological_sort(phase_modules)
            execution_order.extend([m.metadata.module_id for m in sorted_modules])
        
        self._execution_order = execution_order
        return execution_order
    
    def _topological_sort(self, modules: List[BaseSetupModule]) -> List[BaseSetupModule]:
        """
        Sort modules by dependencies and priority using topological sort.
        
        Args:
            modules: Modules to sort
        
        Returns:
            Sorted list of modules
        """
        # Build dependency graph
        graph: Dict[str, List[str]] = {}
        in_degree: Dict[str, int] = {}
        module_map: Dict[str, BaseSetupModule] = {}
        
        for module in modules:
            module_id = module.metadata.module_id
            module_map[module_id] = module
            graph[module_id] = module.metadata.dependencies.copy()
            in_degree[module_id] = len(module.metadata.dependencies)
        
        # Find modules with no dependencies
        queue = []
        for module in modules:
            if in_degree[module.metadata.module_id] == 0:
                queue.append(module)
        
        # Sort queue by priority
        queue.sort(key=lambda m: m.metadata.priority)
        
        # Process queue
        result = []
        while queue:
            # Take module with highest priority (lowest number)
            module = queue.pop(0)
            result.append(module)
            
            # Remove this module from dependencies of others
            for other_id, deps in graph.items():
                if module.metadata.module_id in deps:
                    deps.remove(module.metadata.module_id)
                    in_degree[other_id] -= 1
                    
                    if in_degree[other_id] == 0:
                        # Add to queue maintaining priority order
                        other_module = module_map[other_id]
                        queue.append(other_module)
                        queue.sort(key=lambda m: m.metadata.priority)
        
        # Check for circular dependencies
        if len(result) != len(modules):
            remaining = [m.metadata.module_id for m in modules if m not in result]
            raise ValueError(f"Circular dependencies detected: {remaining}")
        
        return result
    
    def execute_setup(
        self,
        context: Dict[str, Any],
        selected_modules: Optional[List[str]] = None
    ) -> 'SetupExecutionReport':
        """
        Execute setup with all registered modules.
        
        Args:
            context: Shared context dictionary
                - Must include: project_root, platform info
                - Modules can add data for downstream modules
            selected_modules: Optional list of module IDs to run
                (if None, runs all enabled modules)
        
        Returns:
            SetupExecutionReport with all results
        """
        self.logger.info("=" * 60)
        self.logger.info("🚀 CORTEX Setup - Starting")
        self.logger.info("=" * 60)
        
        start_time = datetime.now()
        self._results = []
        
        # Resolve execution order
        try:
            execution_order = self._resolve_execution_order()
        except ValueError as e:
            self.logger.error(f"Failed to resolve execution order: {e}")
            return SetupExecutionReport(
                overall_success=False,
                context=context,
                results=[],
                summary=f"Setup failed: {e}",
                duration_ms=0
            )
        
        # Filter by selected modules
        if selected_modules:
            execution_order = [
                mid for mid in execution_order 
                if mid in selected_modules
            ]
        
        self.logger.info(f"\n📋 Execution plan:")
        for i, module_id in enumerate(execution_order, 1):
            module = self._modules[module_id]
            self.logger.info(
                f"  {i}. {module.metadata.name} "
                f"(phase: {module.metadata.phase.name}, "
                f"priority: {module.metadata.priority})"
            )
        
        # Execute modules
        failed_modules = []
        for module_id in execution_order:
            module = self._modules[module_id]
            
            # Check if should run
            if not module.should_run(context):
                result = SetupResult(
                    module_id=module_id,
                    status=SetupStatus.SKIPPED,
                    message=f"{module.metadata.name} skipped (conditional)"
                )
                self._results.append(result)
                self.logger.info(f"\n⏭️  Skipped: {module.metadata.name}")
                continue
            
            # Validate prerequisites
            is_valid, issues = module.validate_prerequisites(context)
            if not is_valid:
                result = SetupResult(
                    module_id=module_id,
                    status=SetupStatus.FAILED,
                    message=f"Prerequisites not met: {', '.join(issues)}",
                    errors=issues
                )
                self._results.append(result)
                failed_modules.append(module_id)
                
                self.logger.error(f"\n❌ {module.metadata.name} - Prerequisites failed")
                for issue in issues:
                    self.logger.error(f"   - {issue}")
                
                # Stop if not optional
                if not module.metadata.optional:
                    self.logger.error("⛔ Required module failed. Stopping setup.")
                    break
                continue
            
            # Execute module
            self.logger.info(f"\n🔧 Executing: {module.metadata.name}")
            
            module_start = datetime.now()
            try:
                result = module.execute(context)
                result.duration_ms = (datetime.now() - module_start).total_seconds() * 1000
            except Exception as e:
                self.logger.exception(f"Module execution failed: {e}")
                result = SetupResult(
                    module_id=module_id,
                    status=SetupStatus.FAILED,
                    message=f"Execution failed: {str(e)}",
                    errors=[str(e)],
                    duration_ms=(datetime.now() - module_start).total_seconds() * 1000
                )
            
            self._results.append(result)
            
            # Log result
            if result.status == SetupStatus.SUCCESS:
                self.logger.info(f"   ✅ {result.message}")
            elif result.status == SetupStatus.WARNING:
                self.logger.warning(f"   ⚠️  {result.message}")
                for warning in result.warnings:
                    self.logger.warning(f"      - {warning}")
            elif result.status == SetupStatus.FAILED:
                self.logger.error(f"   ❌ {result.message}")
                for error in result.errors:
                    self.logger.error(f"      - {error}")
                
                failed_modules.append(module_id)
                
                # Stop if not optional
                if not module.metadata.optional:
                    self.logger.error("⛔ Required module failed. Stopping setup.")
                    break
        
        # Calculate overall success
        total_duration = (datetime.now() - start_time).total_seconds() * 1000
        overall_success = len(failed_modules) == 0
        
        # Generate report
        report = SetupExecutionReport(
            overall_success=overall_success,
            context=context,
            results=self._results,
            summary=self._generate_summary(overall_success, failed_modules),
            duration_ms=total_duration,
            failed_modules=failed_modules
        )
        
        # Print summary
        self.logger.info("\n" + "=" * 60)
        self.logger.info(report.summary)
        self.logger.info("=" * 60)
        
        return report
    
    def _generate_summary(self, success: bool, failed_modules: List[str]) -> str:
        """Generate human-readable summary."""
        if success:
            return f"✅ Setup completed successfully! All {len(self._results)} modules passed."
        else:
            return (
                f"❌ Setup failed. {len(failed_modules)} module(s) failed: "
                f"{', '.join(failed_modules)}"
            )
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback all executed modules in reverse order.
        
        Args:
            context: Shared context
        
        Returns:
            True if rollback successful
        """
        self.logger.info("\n🔄 Rolling back setup...")
        
        # Reverse order
        for result in reversed(self._results):
            if result.status not in [SetupStatus.SUCCESS, SetupStatus.WARNING]:
                continue
            
            module = self._modules.get(result.module_id)
            if module:
                self.logger.info(f"  Rolling back: {module.metadata.name}")
                try:
                    module.rollback(context)
                except Exception as e:
                    self.logger.error(f"  Rollback failed: {e}")
        
        self.logger.info("✓ Rollback complete")
        return True


class SetupExecutionReport:
    """
    Comprehensive report of setup execution.
    
    Attributes:
        overall_success: Whether all modules succeeded
        context: Final context state
        results: List of all module results
        summary: Human-readable summary
        duration_ms: Total execution time
        failed_modules: List of failed module IDs
    """
    
    def __init__(
        self,
        overall_success: bool,
        context: Dict[str, Any],
        results: List[SetupResult],
        summary: str,
        duration_ms: float,
        failed_modules: List[str] = None
    ):
        self.overall_success = overall_success
        self.context = context
        self.results = results
        self.summary = summary
        self.duration_ms = duration_ms
        self.failed_modules = failed_modules or []
    
    def get_module_result(self, module_id: str) -> Optional[SetupResult]:
        """Get result for a specific module."""
        for result in self.results:
            if result.module_id == module_id:
                return result
        return None
    
    def get_successful_modules(self) -> List[str]:
        """Get list of successful module IDs."""
        return [
            r.module_id for r in self.results 
            if r.status == SetupStatus.SUCCESS
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            'overall_success': self.overall_success,
            'summary': self.summary,
            'duration_ms': self.duration_ms,
            'failed_modules': self.failed_modules,
            'results': [
                {
                    'module_id': r.module_id,
                    'status': r.status.value,
                    'message': r.message,
                    'duration_ms': r.duration_ms
                }
                for r in self.results
            ]
        }
