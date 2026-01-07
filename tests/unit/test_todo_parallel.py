"""
CORTEX 6.0 - TodoOrchestrator Parallel Tasks Tests
=================================================
Tests for identifying ready tasks and parallel execution groups.

Author: Asif Hussain
Version: 6.0.0
Created: 2026-01-07
Task: task-2.2.5 (Implement parallel execution identification)
TDD Phase: GREEN
"""

import tempfile
from pathlib import Path
import pytest
from src.orchestrators.core.todo_orchestrator import TodoOrchestrator, Priority, TodoStatus
from src.orchestrators.audit_logger import EnterpriseAuditLogger
from src.database.state_manager import StateManager


@pytest.fixture
def temp_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "state.db"

@pytest.fixture
def state_manager(temp_db):
    sm = StateManager(temp_db)
    sm.initialize()
    yield sm
    sm.close()

@pytest.fixture
def orchestrator(state_manager):
    import uuid
    return TodoOrchestrator(
        state_manager=state_manager,
        audit_logger=EnterpriseAuditLogger(),
        name=f"test-orchestrator-{uuid.uuid4().hex[:8]}"
    )


def test_identify_parallel_tasks(orchestrator):
    """Tasks at the same dependency level should be grouped for parallel execution."""
    # Build DAG: A -> B, A -> C, B -> D, C -> E
    a = orchestrator.create_todo(title="A", priority=Priority.P0_CRITICAL)
    b = orchestrator.create_todo(title="B", priority=Priority.P1_HIGH, dependencies=[a])
    c = orchestrator.create_todo(title="C", priority=Priority.P1_HIGH, dependencies=[a])
    d = orchestrator.create_todo(title="D", priority=Priority.P2_MEDIUM, dependencies=[b])
    e = orchestrator.create_todo(title="E", priority=Priority.P2_MEDIUM, dependencies=[c])

    # Identify parallel groups
    parallel_groups = orchestrator.get_parallel_tasks()

    # Expect groups by levels: [ [A], [B, C], [D, E] ]
    assert len(parallel_groups) == 3
    assert {t.title for t in parallel_groups[0]} == {"A"}
    assert {t.title for t in parallel_groups[1]} == {"B", "C"}
    assert {t.title for t in parallel_groups[2]} == {"D", "E"}


def test_identify_ready_tasks(orchestrator):
    """Tasks should be ready when all dependencies are completed."""
    # Create three tasks: A root, B depends on A, C depends on A
    a = orchestrator.create_todo(title="A", priority=Priority.P0_CRITICAL)
    b = orchestrator.create_todo(title="B", priority=Priority.P1_HIGH, dependencies=[a])
    c = orchestrator.create_todo(title="C", priority=Priority.P2_MEDIUM, dependencies=[a])

    # Initially only A is ready (roots)
    ready_initial = orchestrator.get_ready_tasks()
    assert {t.title for t in ready_initial} == {"A"}

    # Complete A; B and C should become ready
    orchestrator.transition_status(a, TodoStatus.IN_PROGRESS)
    orchestrator.transition_status(a, TodoStatus.COMPLETED)

    ready_after = orchestrator.get_ready_tasks()
    assert {t.title for t in ready_after} == {"B", "C"}
