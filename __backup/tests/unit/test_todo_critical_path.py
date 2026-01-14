"""
CORTEX 6.0 - TodoOrchestrator Critical Path Tests
===============================================
Tests for calculating the critical path across the DAG.

Author: Asif Hussain
Version: 6.0.0
Created: 2026-01-07
Task: task-2.2.6 (Critical path calculation)
TDD Phase: GREEN
"""

import tempfile
from pathlib import Path
import pytest
from src.orchestrators.core.todo_orchestrator import TodoOrchestrator, Priority
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


def titles(path):
    return [t.title for t in path]


def test_critical_path_linear(orchestrator):
    """Critical path of a linear chain should be the full chain in order."""
    a = orchestrator.create_todo(title="A", priority=Priority.P0_CRITICAL)
    b = orchestrator.create_todo(title="B", priority=Priority.P1_HIGH, dependencies=[a])
    c = orchestrator.create_todo(title="C", priority=Priority.P2_MEDIUM, dependencies=[b])
    d = orchestrator.create_todo(title="D", priority=Priority.P3_LOW, dependencies=[c])

    cp = orchestrator._calculate_critical_path()
    assert titles(cp) == ["A", "B", "C", "D"]


def test_critical_path_branching(orchestrator):
    """Critical path should follow the longest dependency chain."""
    # Branching graph:
    # A -> B -> D
    # A -> C -> E -> F
    a = orchestrator.create_todo(title="A", priority=Priority.P0_CRITICAL)
    b = orchestrator.create_todo(title="B", priority=Priority.P1_HIGH, dependencies=[a])
    c = orchestrator.create_todo(title="C", priority=Priority.P1_HIGH, dependencies=[a])
    d = orchestrator.create_todo(title="D", priority=Priority.P2_MEDIUM, dependencies=[b])
    e = orchestrator.create_todo(title="E", priority=Priority.P2_MEDIUM, dependencies=[c])
    f = orchestrator.create_todo(title="F", priority=Priority.P3_LOW, dependencies=[e])

    cp = orchestrator._calculate_critical_path()
    assert titles(cp) == ["A", "C", "E", "F"]
