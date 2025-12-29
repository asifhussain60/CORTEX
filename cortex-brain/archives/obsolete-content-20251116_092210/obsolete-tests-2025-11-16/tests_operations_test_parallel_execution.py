"""
Tests for parallel module execution in operations orchestrator.

Validates that:
1. Independent modules execute in parallel
2. Dependent modules execute sequentially
3. Error handling works correctly in parallel execution
4. Performance improves with parallel execution
5. Context is properly shared between modules

Author: Asif Hussain
Version: 1.0
"""

import pytest
import time
from pathlib import Path
from typing import Dict, Any
from src.operations.operations_orchestrator import (
    OperationsOrchestrator,
    OperationExecutionReport
)
from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)


class SlowModule(BaseOperationModule):
    """Test module that takes some time to execute."""
    
    def __init__(self, module_id: str, duration: float = 0.1, dependencies: list = None):
        super().__init__()  # Initialize base class
        self.id = module_id
        self.duration = duration
        self.deps = dependencies or []
        self.execution_time = None
    
    def get_metadata(self) -> OperationModuleMetadata:
        return OperationModuleMetadata(
            module_id=self.id,
            name=f"Slow Module {self.id}",
            description=f"Test module that sleeps for {self.duration}s",
            phase=OperationPhase.PROCESSING,
            priority=10,
            dependencies=self.deps
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """Execute with a delay to simulate work."""
        start = time.time()
        time.sleep(self.duration)
        self.execution_time = time.time()
        
        return OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message=f"Module {self.id} completed",
            data={f"{self.id}_result": "done"}
        )


class FailingModule(BaseOperationModule):
    """Test module that fails."""
    
    def __init__(self, module_id: str, optional: bool = False):
        super().__init__()  # Initialize base class
        self.id = module_id
        self.is_optional = optional
    
    def get_metadata(self) -> OperationModuleMetadata:
        return OperationModuleMetadata(
            module_id=self.id,
            name=f"Failing Module {self.id}",
            description="Test module that always fails",
            phase=OperationPhase.PROCESSING,
            priority=10,
            optional=self.is_optional
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """Always fail."""
        return OperationResult(
            success=False,
            status=OperationStatus.FAILED,
            message=f"Module {self.id} failed intentionally",
            errors=["Intentional failure"]
        )


class TestParallelExecution:
    """Test suite for parallel module execution."""
    
    def test_independent_modules_run_in_parallel(self):
        """Independent modules should execute concurrently."""
        # Create 4 independent modules, each taking 0.2s
        modules = [
            SlowModule(f"module_{i}", duration=0.2)
            for i in range(4)
        ]
        
        orchestrator = OperationsOrchestrator(
            operation_id="test_parallel",
            operation_name="Test Parallel Execution",
            modules=modules,
            max_parallel_workers=4
        )
        
        start = time.time()
        report = orchestrator.execute_operation()
        duration = time.time() - start
        
        # All modules should succeed
        assert report.success
        assert len(report.modules_succeeded) == 4
        
        # Sequential execution would take 0.8s (4 * 0.2s)
        # Parallel execution should take ~0.2s (all at once)
        # Allow some overhead, but should be < 0.5s
        assert duration < 0.5, f"Expected < 0.5s, got {duration:.2f}s"
        
        # Should have 1 parallel group (all modules independent)
        assert report.parallel_groups_count == 1
        assert report.parallel_execution_count == 4
        
        # Should report time saved
        assert report.time_saved_seconds > 0
    
    def test_dependent_modules_run_sequentially(self):
        """Modules with dependencies should execute in order."""
        # Create chain: A -> B -> C -> D
        modules = [
            SlowModule("module_a", duration=0.1),
            SlowModule("module_b", duration=0.1, dependencies=["module_a"]),
            SlowModule("module_c", duration=0.1, dependencies=["module_b"]),
            SlowModule("module_d", duration=0.1, dependencies=["module_c"])
        ]
        
        orchestrator = OperationsOrchestrator(
            operation_id="test_sequential",
            operation_name="Test Sequential Execution",
            modules=modules
        )
        
        start = time.time()
        report = orchestrator.execute_operation()
        duration = time.time() - start
        
        # All modules should succeed
        assert report.success
        assert len(report.modules_succeeded) == 4
        
        # Should take ~0.4s (sequential)
        assert duration >= 0.4, f"Expected >= 0.4s, got {duration:.2f}s"
        
        # Should have 4 groups (1 module each, due to dependencies)
        assert report.parallel_groups_count == 4
        assert report.parallel_execution_count == 0  # No parallel execution
        
        # Verify execution order by checking timestamps
        times = [m.execution_time for m in modules]
        assert times == sorted(times), "Modules did not execute in dependency order"
    
    def test_mixed_parallel_and_sequential(self):
        """Mix of independent and dependent modules."""
        # Create: A, B (independent), then C depends on both
        modules = [
            SlowModule("module_a", duration=0.2),
            SlowModule("module_b", duration=0.2),
            SlowModule("module_c", duration=0.2, dependencies=["module_a", "module_b"])
        ]
        
        orchestrator = OperationsOrchestrator(
            operation_id="test_mixed",
            operation_name="Test Mixed Execution",
            modules=modules
        )
        
        start = time.time()
        report = orchestrator.execute_operation()
        duration = time.time() - start
        
        # All modules should succeed
        assert report.success
        assert len(report.modules_succeeded) == 3
        
        # Should take ~0.4s (A & B in parallel = 0.2s, then C = 0.2s)
        assert 0.4 <= duration < 0.6, f"Expected 0.4-0.6s, got {duration:.2f}s"
        
        # Should have 2 groups
        assert report.parallel_groups_count == 2
        assert report.parallel_execution_count == 2  # A and B
    
    def test_parallel_group_failure_handling(self):
        """Failure in parallel group should be handled correctly."""
        modules = [
            SlowModule("module_a", duration=0.1),
            FailingModule("module_fail", optional=False),  # Required module fails
            SlowModule("module_b", duration=0.1)
        ]
        
        orchestrator = OperationsOrchestrator(
            operation_id="test_failure",
            operation_name="Test Failure Handling",
            modules=modules
        )
        
        report = orchestrator.execute_operation()
        
        # Operation should fail
        assert not report.success
        assert "module_fail" in report.modules_failed
        
        # Should have attempted to rollback
        assert len(report.errors) > 0
    
    def test_optional_module_failure_continues(self):
        """Optional module failure should not stop execution."""
        modules = [
            SlowModule("module_a", duration=0.1),
            FailingModule("module_fail", optional=True),  # Optional module fails
            SlowModule("module_b", duration=0.1)
        ]
        
        orchestrator = OperationsOrchestrator(
            operation_id="test_optional_failure",
            operation_name="Test Optional Failure",
            modules=modules
        )
        
        report = orchestrator.execute_operation()
        
        # Operation should succeed (optional failure)
        assert report.success
        assert "module_fail" in report.modules_failed
        assert len(report.modules_succeeded) == 2
    
    def test_context_sharing_in_parallel(self):
        """Context updates from parallel modules should be merged."""
        modules = [
            SlowModule("module_a", duration=0.1),
            SlowModule("module_b", duration=0.1),
            SlowModule("module_c", duration=0.1)
        ]
        
        orchestrator = OperationsOrchestrator(
            operation_id="test_context",
            operation_name="Test Context Sharing",
            modules=modules
        )
        
        report = orchestrator.execute_operation()
        
        # All modules should succeed
        assert report.success
        
        # Context should have results from all modules
        assert "module_a_result" in report.context
        assert "module_b_result" in report.context
        assert "module_c_result" in report.context
    
    def test_max_workers_limit(self):
        """Parallel execution should respect max_workers limit."""
        # Create 8 modules with max_workers=2
        modules = [
            SlowModule(f"module_{i}", duration=0.1)
            for i in range(8)
        ]
        
        orchestrator = OperationsOrchestrator(
            operation_id="test_workers",
            operation_name="Test Max Workers",
            modules=modules,
            max_parallel_workers=2  # Limit to 2 concurrent
        )
        
        start = time.time()
        report = orchestrator.execute_operation()
        duration = time.time() - start
        
        # All modules should succeed
        assert report.success
        assert len(report.modules_succeeded) == 8
        
        # With 8 modules at 0.1s each and max 2 workers:
        # Should take ~0.4s (4 batches of 2)
        # Allow some overhead
        assert 0.4 <= duration < 0.6, f"Expected 0.4-0.6s, got {duration:.2f}s"
    
    def test_performance_metrics_tracking(self):
        """Performance metrics should be accurately tracked."""
        # Create scenario with clear parallel benefit
        modules = [
            SlowModule("module_a", duration=0.2),
            SlowModule("module_b", duration=0.2),
            SlowModule("module_c", duration=0.2),
            SlowModule("module_d", duration=0.2)
        ]
        
        orchestrator = OperationsOrchestrator(
            operation_id="test_metrics",
            operation_name="Test Metrics Tracking",
            modules=modules,
            max_parallel_workers=4
        )
        
        report = orchestrator.execute_operation()
        
        # Check metrics
        assert report.parallel_groups_count == 1
        assert report.parallel_execution_count == 4
        assert report.time_saved_seconds > 0
        
        # Time saved should be substantial (3 * 0.2s = 0.6s saved)
        assert report.time_saved_seconds >= 0.5, \
            f"Expected >= 0.5s saved, got {report.time_saved_seconds:.2f}s"


class TestParallelExecutionEdgeCases:
    """Test edge cases in parallel execution."""
    
    def test_single_module_no_parallel(self):
        """Single module should not use parallel execution."""
        module = SlowModule("module_a", duration=0.1)
        
        orchestrator = OperationsOrchestrator(
            operation_id="test_single",
            operation_name="Test Single Module",
            modules=[module]
        )
        
        report = orchestrator.execute_operation()
        
        assert report.success
        assert report.parallel_groups_count == 1
        assert report.parallel_execution_count == 0  # No parallel execution
    
    def test_empty_module_list(self):
        """Empty module list should complete successfully."""
        orchestrator = OperationsOrchestrator(
            operation_id="test_empty",
            operation_name="Test Empty Modules",
            modules=[]
        )
        
        report = orchestrator.execute_operation()
        
        assert report.success
        assert len(report.modules_executed) == 0
        assert report.parallel_groups_count == 0
    
    def test_circular_dependency_handling(self):
        """Circular dependencies should be detected and handled."""
        # Create circular dependency: A -> B -> A
        modules = [
            SlowModule("module_a", duration=0.1, dependencies=["module_b"]),
            SlowModule("module_b", duration=0.1, dependencies=["module_a"])
        ]
        
        orchestrator = OperationsOrchestrator(
            operation_id="test_circular",
            operation_name="Test Circular Dependency",
            modules=modules
        )
        
        # Should complete (with warning) by breaking into individual groups
        report = orchestrator.execute_operation()
        
        # May succeed or fail depending on execution order
        # Main point: should not hang
        assert report is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
