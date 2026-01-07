"""
CORTEX 6.0 - TodoOrchestrator Persistence Tests
================================================
Tests for DAG integration with StateManager.

Author: Asif Hussain
Version: 6.0.0
Created: 2026-01-07
Task: task-2.2.2 (Integrate DAG with StateManager)
"""

import pytest
import tempfile
from pathlib import Path
from src.orchestrators.core.todo_orchestrator import TodoOrchestrator, Priority, TodoStatus
from src.database.state_manager import StateManager
from src.orchestrators.audit_logger import EnterpriseAuditLogger


class TestTodoOrchestratorPersistence:
    """Test suite for TodoOrchestrator persistence with StateManager."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_state.db"
            yield db_path
    
    @pytest.fixture
    def state_manager(self, temp_db):
        """Create StateManager instance."""
        sm = StateManager(temp_db)
        sm.initialize()
        yield sm
        sm.close()
    
    @pytest.fixture
    def orchestrator(self, state_manager):
        """Create TodoOrchestrator instance."""
        audit_logger = EnterpriseAuditLogger()
        return TodoOrchestrator(
            state_manager=state_manager,
            audit_logger=audit_logger,
            name="test-orchestrator"
        )
    
    def test_persist_creates_new_state(self, orchestrator):
        """Test persist() creates new state when none exists."""
        # Create some TODOs
        todo1 = orchestrator.create_todo(
            title="Task 1",
            description="First task",
            priority=Priority.P0_CRITICAL
        )
        todo2 = orchestrator.create_todo(
            title="Task 2",
            description="Second task",
            priority=Priority.P1_HIGH,
            dependencies=[todo1]
        )
        
        # Persist
        orchestrator.persist()
        
        # Verify state was created in StateManager
        state_key = f"{orchestrator.name}-state"
        state_result = orchestrator.state_manager.read_state(state_key)
        
        assert state_result is not None
        assert state_result["version"] == 1
        assert "todos" in state_result["value"]
        assert "dag_state" in state_result["value"]
        assert len(state_result["value"]["todos"]) == 2
    
    def test_persist_updates_existing_state(self, orchestrator):
        """Test persist() updates state with optimistic locking."""
        # Create and persist initial state
        todo1 = orchestrator.create_todo(title="Task 1", priority=Priority.P0_CRITICAL)
        orchestrator.persist()
        
        # Verify initial version
        state_key = f"{orchestrator.name}-state"
        state_v1 = orchestrator.state_manager.read_state(state_key)
        assert state_v1["version"] == 1
        
        # Add more TODOs and persist again
        todo2 = orchestrator.create_todo(title="Task 2", priority=Priority.P1_HIGH)
        orchestrator.persist()
        
        # Verify version incremented
        state_v2 = orchestrator.state_manager.read_state(state_key)
        assert state_v2["version"] == 2
        assert len(state_v2["value"]["todos"]) == 2
    
    def test_load_restores_todos(self, orchestrator, state_manager):
        """Test load() restores TODOs from StateManager."""
        # Create TODOs and persist
        todo1 = orchestrator.create_todo(
            title="Task 1",
            description="First task",
            priority=Priority.P0_CRITICAL,
            tags={"backend", "api"}
        )
        todo2 = orchestrator.create_todo(
            title="Task 2",
            description="Second task",
            priority=Priority.P1_HIGH,
            dependencies=[todo1]
        )
        orchestrator.persist()
        
        # Create new orchestrator and load state
        orchestrator2 = TodoOrchestrator(
            state_manager=state_manager,
            audit_logger=EnterpriseAuditLogger(),
            name="test-orchestrator"  # Same name to load same state
        )
        orchestrator2.load()
        
        # Verify TODOs restored
        assert len(orchestrator2.todos) == 2
        assert todo1 in orchestrator2.todos
        assert todo2 in orchestrator2.todos
        
        # Verify TODO details
        restored_todo1 = orchestrator2.todos[todo1]
        assert restored_todo1.title == "Task 1"
        assert restored_todo1.description == "First task"
        assert restored_todo1.priority == Priority.P0_CRITICAL
        assert restored_todo1.tags == {"backend", "api"}
    
    def test_load_restores_dag(self, orchestrator, state_manager):
        """Test load() restores DAG structure."""
        # Create TODOs with dependencies
        todo1 = orchestrator.create_todo(title="Task 1", priority=Priority.P0_CRITICAL)
        todo2 = orchestrator.create_todo(title="Task 2", priority=Priority.P1_HIGH, dependencies=[todo1])
        todo3 = orchestrator.create_todo(title="Task 3", priority=Priority.P2_MEDIUM, dependencies=[todo1, todo2])
        orchestrator.persist()
        
        # Create new orchestrator and load
        orchestrator2 = TodoOrchestrator(
            state_manager=state_manager,
            audit_logger=EnterpriseAuditLogger(),
            name="test-orchestrator"
        )
        orchestrator2.load()
        
        # Verify DAG restored
        assert len(orchestrator2.dag.nodes) == 3
        
        # Verify dependencies
        assert orchestrator2.dag.has_edge(todo1, todo2)
        assert orchestrator2.dag.has_edge(todo1, todo3)
        assert orchestrator2.dag.has_edge(todo2, todo3)
    
    def test_load_restores_statistics(self, orchestrator, state_manager):
        """Test load() restores statistics."""
        # Create and complete some TODOs
        todo1 = orchestrator.create_todo(title="Task 1", priority=Priority.P0_CRITICAL)
        orchestrator.transition_status(todo1, TodoStatus.IN_PROGRESS)
        orchestrator.transition_status(todo1, TodoStatus.COMPLETED)
        
        todo2 = orchestrator.create_todo(title="Task 2", priority=Priority.P1_HIGH)
        orchestrator.transition_status(todo2, TodoStatus.IN_PROGRESS)
        orchestrator.transition_status(todo2, TodoStatus.FAILED)
        
        orchestrator.persist()
        
        # Load into new orchestrator
        orchestrator2 = TodoOrchestrator(
            state_manager=state_manager,
            audit_logger=EnterpriseAuditLogger(),
            name="test-orchestrator"
        )
        orchestrator2.load()
        
        # Verify statistics
        stats = orchestrator2.get_statistics()
        assert stats["total_created"] == 2
        assert stats["total_completed"] == 1
        assert stats["total_failed"] == 1
    
    def test_persist_and_recover_empty_orchestrator(self, orchestrator, state_manager):
        """Test persist/load with no TODOs."""
        # Persist empty orchestrator
        orchestrator.persist()
        
        # Load into new orchestrator
        orchestrator2 = TodoOrchestrator(
            state_manager=state_manager,
            audit_logger=EnterpriseAuditLogger(),
            name="test-orchestrator"
        )
        orchestrator2.load()
        
        # Verify empty state
        assert len(orchestrator2.todos) == 0
        assert len(orchestrator2.dag.nodes) == 0
    
    def test_persist_and_recover_with_status_transitions(self, orchestrator, state_manager):
        """Test persist/recover preserves TODO status."""
        # Create TODOs with different statuses
        todo1 = orchestrator.create_todo(title="Task 1", priority=Priority.P0_CRITICAL)
        orchestrator.transition_status(todo1, TodoStatus.IN_PROGRESS)
        
        todo2 = orchestrator.create_todo(title="Task 2", priority=Priority.P1_HIGH)
        orchestrator.transition_status(todo2, TodoStatus.IN_PROGRESS)
        orchestrator.transition_status(todo2, TodoStatus.COMPLETED)
        
        todo3 = orchestrator.create_todo(title="Task 3", priority=Priority.P2_MEDIUM)
        # Leave as NOT_STARTED
        
        orchestrator.persist()
        
        # Load into new orchestrator
        orchestrator2 = TodoOrchestrator(
            state_manager=state_manager,
            audit_logger=EnterpriseAuditLogger(),
            name="test-orchestrator"
        )
        orchestrator2.load()
        
        # Verify statuses preserved
        assert orchestrator2.todos[todo1].status == TodoStatus.IN_PROGRESS
        assert orchestrator2.todos[todo2].status == TodoStatus.COMPLETED
        assert orchestrator2.todos[todo3].status == TodoStatus.NOT_STARTED
    
    def test_persist_tracks_versions_correctly(self, orchestrator, state_manager):
        """Test persist() correctly increments versions."""
        # Create initial state
        todo1 = orchestrator.create_todo(title="Task 1", priority=Priority.P0_CRITICAL)
        orchestrator.persist()
        
        # Verify initial version
        state_key = f"{orchestrator.name}-state"
        version_1 = state_manager.read_state(state_key)["version"]
        assert version_1 == 1
        
        # Add another TODO and persist
        todo2 = orchestrator.create_todo(title="Task 2", priority=Priority.P1_HIGH)
        orchestrator.persist()
        
        # Version should increment
        version_2 = state_manager.read_state(state_key)["version"]
        assert version_2 == 2
        
        # Multiple persists increment version each time
        orchestrator.persist()
        version_3 = state_manager.read_state(state_key)["version"]
        assert version_3 == 3
    
    def test_load_with_no_existing_state(self, orchestrator):
        """Test load() when no state exists (should not crash)."""
        # Try to load when nothing has been persisted
        orchestrator.load()
        
        # Verify orchestrator is still empty
        assert len(orchestrator.todos) == 0
        assert len(orchestrator.dag.nodes) == 0
    
    def test_persist_and_recover_complex_dag(self, orchestrator, state_manager):
        """Test persist/recover with complex DAG structure."""
        # Create complex dependency graph
        #     t1
        #    /  \
        #   t2  t3
        #    \  /
        #     t4
        t1 = orchestrator.create_todo(title="T1", priority=Priority.P0_CRITICAL)
        t2 = orchestrator.create_todo(title="T2", priority=Priority.P1_HIGH, dependencies=[t1])
        t3 = orchestrator.create_todo(title="T3", priority=Priority.P1_HIGH, dependencies=[t1])
        t4 = orchestrator.create_todo(title="T4", priority=Priority.P2_MEDIUM, dependencies=[t2, t3])
        
        orchestrator.persist()
        
        # Load into new orchestrator
        orchestrator2 = TodoOrchestrator(
            state_manager=state_manager,
            audit_logger=EnterpriseAuditLogger(),
            name="test-orchestrator"
        )
        orchestrator2.load()
        
        # Verify complex DAG structure
        assert len(orchestrator2.dag.nodes) == 4
        assert orchestrator2.dag.has_edge(t1, t2)
        assert orchestrator2.dag.has_edge(t1, t3)
        assert orchestrator2.dag.has_edge(t2, t4)
        assert orchestrator2.dag.has_edge(t3, t4)
        
        # Verify execution order preserved
        exec_order = orchestrator2.dag.topological_sort()
        assert exec_order.index(t1) < exec_order.index(t2)
        assert exec_order.index(t1) < exec_order.index(t3)
        assert exec_order.index(t2) < exec_order.index(t4)
        assert exec_order.index(t3) < exec_order.index(t4)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
