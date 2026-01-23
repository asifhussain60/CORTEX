"""Tests for REM-ARCH-001 & REM-ARCH-002: Architecture Refactoring.

Verifies SOLID principles:
- Single Responsibility Principle (SRP)
- Dependency Inversion Principle (DIP)

Test Coverage:
- Scheduler has single responsibility
- LifecycleManager has single responsibility
- PersistenceManager has single responsibility
- Dependency injection container works
- Orchestrator uses injected dependencies
"""

import pytest

from cortex.orchestrators.refactored_architecture import (
    IScheduler,
    ILifecycleManager,
    IPersistenceManager,
    DependencyContainer,
    Orchestrator,
    Scheduler,
    LifecycleManager,
    PersistenceManager,
    ExecutionContext,
    ExecutionResult,
)


class TestSingleResponsibilityPrinciple:
    """Test SRP: Each class has single responsibility."""

    def test_scheduler_single_concern(self) -> None:
        """Verify Scheduler only handles task scheduling."""
        scheduler = Scheduler()
        
        # Should only have scheduling concerns
        assert hasattr(scheduler, 'schedule_task')
        assert hasattr(scheduler, 'cancel_task')
        assert hasattr(scheduler, 'get_scheduled_tasks')
        
        # Should be able to schedule task
        result = scheduler.schedule_task("task_001", {"action": "test"})
        assert result is True
        
        # Should be able to retrieve it
        tasks = scheduler.get_scheduled_tasks()
        assert "task_001" in tasks

    def test_lifecycle_manager_single_concern(self) -> None:
        """Verify LifecycleManager only handles lifecycle operations."""
        lifecycle = LifecycleManager()
        
        # Should only have lifecycle concerns
        assert hasattr(lifecycle, 'start')
        assert hasattr(lifecycle, 'stop')
        assert hasattr(lifecycle, 'pause')
        assert hasattr(lifecycle, 'resume')
        assert hasattr(lifecycle, 'get_status')
        
        # Should handle lifecycle transitions
        assert lifecycle.start() is True
        assert lifecycle.get_status() == "RUNNING"
        assert lifecycle.pause() is True
        assert lifecycle.get_status() == "PAUSED"
        assert lifecycle.resume() is True
        assert lifecycle.stop() is True

    def test_persistence_manager_single_concern(self) -> None:
        """Verify PersistenceManager only handles state persistence."""
        persistence = PersistenceManager()
        
        # Should only have persistence concerns
        assert hasattr(persistence, 'save_state')
        assert hasattr(persistence, 'load_state')
        assert hasattr(persistence, 'delete_state')
        
        # Should handle persistence operations
        state = {"key": "value"}
        assert persistence.save_state(state) is True
        
        loaded = persistence.load_state()
        assert loaded == state
        
        assert persistence.delete_state() is True
        assert persistence.load_state() is None


class TestDependencyInversionPrinciple:
    """Test DIP: Depend on abstractions, not concrete classes."""

    def test_interfaces_defined(self) -> None:
        """Verify interfaces are defined (abstractions)."""
        # These are abstract base classes - cannot instantiate
        assert IScheduler is not None
        assert ILifecycleManager is not None
        assert IPersistenceManager is not None

    def test_concrete_classes_implement_interfaces(self) -> None:
        """Verify concrete classes implement interfaces."""
        scheduler = Scheduler()
        lifecycle = LifecycleManager()
        persistence = PersistenceManager()
        
        # All should be instances of their interfaces
        assert isinstance(scheduler, IScheduler)
        assert isinstance(lifecycle, ILifecycleManager)
        assert isinstance(persistence, IPersistenceManager)

    def test_orchestrator_uses_dependencies(self) -> None:
        """Verify Orchestrator depends on injected abstractions."""
        scheduler = Scheduler()
        lifecycle = LifecycleManager()
        persistence = PersistenceManager()
        
        # Create orchestrator with injected dependencies
        orchestrator = Orchestrator(
            "test_orch",
            scheduler,
            lifecycle,
            persistence,
        )
        
        # Should work with injected dependencies
        assert orchestrator.name == "test_orch"
        assert orchestrator.start() is True
        assert orchestrator.get_status() == "RUNNING"


class TestDependencyContainer:
    """Test dependency injection container (REM-ARCH-002)."""

    def test_singleton_registration(self) -> None:
        """Verify singleton registration and retrieval."""
        container = DependencyContainer()
        
        # Register singleton
        scheduler = Scheduler()
        container.register_singleton("scheduler", scheduler)
        
        # Retrieve it
        retrieved = container.get("scheduler")
        assert retrieved is scheduler  # Same instance

    def test_factory_registration(self) -> None:
        """Verify factory registration and retrieval."""
        container = DependencyContainer()
        
        # Register factory
        def create_scheduler() -> Scheduler:
            return Scheduler()
        
        container.register_factory("scheduler_factory", create_scheduler)
        
        # Retrieve from factory
        scheduler1 = container.get("scheduler_factory")
        scheduler2 = container.get("scheduler_factory")
        
        # Different instances from factory
        assert scheduler1 is not scheduler2

    def test_interface_registration(self) -> None:
        """Verify interface registration."""
        container = DependencyContainer()
        
        # Register interface
        container.register_interface("scheduler_interface", IScheduler)
        
        # Retrieve interface
        interface = container.get_interface("scheduler_interface")
        assert interface is IScheduler

    def test_multiple_services(self) -> None:
        """Verify managing multiple services."""
        container = DependencyContainer()
        
        # Register multiple services
        scheduler = Scheduler()
        lifecycle = LifecycleManager()
        persistence = PersistenceManager()
        
        container.register_singleton("scheduler", scheduler)
        container.register_singleton("lifecycle", lifecycle)
        container.register_singleton("persistence", persistence)
        
        # Retrieve all
        assert container.get("scheduler") is scheduler
        assert container.get("lifecycle") is lifecycle
        assert container.get("persistence") is persistence

    def test_service_not_found(self) -> None:
        """Verify error on service not found."""
        container = DependencyContainer()
        
        with pytest.raises(KeyError):
            container.get("unknown_service")

    def test_interface_not_found(self) -> None:
        """Verify error on interface not found."""
        container = DependencyContainer()
        
        with pytest.raises(KeyError):
            container.get_interface("unknown_interface")


class TestArchitectureIntegration:
    """Test integrated refactored architecture."""

    def test_end_to_end_orchestration(self) -> None:
        """Verify end-to-end orchestration with DI."""
        # Setup with dependency injection
        container = DependencyContainer()
        
        # Create and register implementations
        scheduler = Scheduler()
        lifecycle = LifecycleManager()
        persistence = PersistenceManager()
        
        container.register_singleton("scheduler", scheduler)
        container.register_singleton("lifecycle", lifecycle)
        container.register_singleton("persistence", persistence)
        
        # Create orchestrator with injected dependencies
        orchestrator = Orchestrator(
            "main_orchestrator",
            container.get("scheduler"),
            container.get("lifecycle"),
            container.get("persistence"),
        )
        
        # Use the orchestrator
        assert orchestrator.start() is True
        assert orchestrator.get_status() == "RUNNING"
        
        # Schedule task
        scheduler.schedule_task("work_001", {"work": "important"})
        assert len(scheduler.get_scheduled_tasks()) > 0
        
        # Persist state
        state = {"orchestrator": "running", "tasks": 1}
        assert persistence.save_state(state) is True
        
        assert orchestrator.stop() is True

    def test_multiple_orchestrators_same_dependencies(self) -> None:
        """Verify multiple orchestrators can share dependencies."""
        scheduler = Scheduler()
        lifecycle = LifecycleManager()
        persistence = PersistenceManager()
        
        # Create multiple orchestrators sharing same dependencies
        orch1 = Orchestrator("orch1", scheduler, lifecycle, persistence)
        orch2 = Orchestrator("orch2", scheduler, lifecycle, persistence)
        
        assert orch1.start() is True
        assert orch2.start() is True
        
        # Both should work independently
        assert orch1.get_status() == "RUNNING"
        assert orch2.get_status() == "RUNNING"

    def test_execution_context_and_result(self) -> None:
        """Verify execution context and result structures."""
        # Create context
        context = ExecutionContext(
            execution_id="exec_001",
            parameters={"key": "value"},
            metadata={"user": "test"},
        )
        
        assert context.execution_id == "exec_001"
        assert context.parameters["key"] == "value"
        
        # Create result
        result = ExecutionResult(
            status="success",
            output={"result": "ok"},
            metadata={"duration_ms": 100},
        )
        
        assert result.status == "success"
        assert result.output["result"] == "ok"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
