"""
Tests for YAML to TODO conversion (Phase 4, task-2.4.1).

Tests the TodoOrchestrator's ability to load and parse feature YAML files
and convert them into TODO items with proper DAG dependencies.
"""

import json
import pytest
import yaml
from pathlib import Path

from src.orchestrators.core.todo_orchestrator import TodoOrchestrator, TodoStatus, Priority
from src.orchestrators.state_manager import StateManager
from src.orchestrators.audit_logger import EnterpriseAuditLogger


@pytest.fixture
def sample_feature_yaml(tmp_path: Path) -> Path:
    """Create a sample feature YAML file for testing."""
    feature_yaml = {
        "feature": {
            "id": "feat-test-01",
            "name": "Test Feature",
            "description": "A test feature for YAML parsing",
            "priority": "P0_CRITICAL",
            "phases": [
                {
                    "id": 1,
                    "name": "Phase 1: Setup",
                    "tasks": [
                        {
                            "id": "1.1",
                            "name": "Task 1.1: Initialize",
                            "priority": "P0_CRITICAL",
                            "estimated_minutes": 30,
                            "dependencies": [],
                        },
                        {
                            "id": "1.2",
                            "name": "Task 1.2: Configure",
                            "priority": "P1_HIGH",
                            "estimated_minutes": 45,
                            "dependencies": ["1.1"],
                        },
                    ],
                },
                {
                    "id": 2,
                    "name": "Phase 2: Implementation",
                    "tasks": [
                        {
                            "id": "2.1",
                            "name": "Task 2.1: Build core",
                            "priority": "P0_CRITICAL",
                            "estimated_minutes": 120,
                            "dependencies": ["1.2"],
                        },
                    ],
                },
            ],
        }
    }
    
    yaml_file = tmp_path / "test-feature.yaml"
    with open(yaml_file, "w") as f:
        yaml.dump(feature_yaml, f)
    
    return yaml_file


def test_load_from_yaml(tmp_path: Path, sample_feature_yaml: Path):
    """Test loading TODOs from a YAML feature file."""
    # Setup
    state_mgr = StateManager(state_file=str(tmp_path / "test.db"))
    audit_logger = EnterpriseAuditLogger(log_dir=str(tmp_path / "logs"))
    orchestrator = TodoOrchestrator(state_manager=state_mgr, audit_logger=audit_logger)
    
    # RED: This should fail until load_from_yaml is implemented
    todos = orchestrator.load_from_yaml(str(sample_feature_yaml))
    
    # Verify TODOs were created
    assert len(todos) == 3, "Should create 3 TODOs from sample YAML"
    
    # Verify todo details
    todo_ids = {t.id for t in todos}
    assert len(todo_ids) == 3, "All TODO IDs should be unique"
    
    # Verify task 1.1 (no dependencies)
    task_1_1 = next(t for t in todos if "1.1" in t.title)
    assert task_1_1.priority == Priority.P0_CRITICAL
    assert task_1_1.status == TodoStatus.READY  # No dependencies, so ready
    
    # Verify task 1.2 (depends on 1.1)
    task_1_2 = next(t for t in todos if "1.2" in t.title)
    assert task_1_2.priority == Priority.P1_HIGH
    assert task_1_2.status == TodoStatus.BLOCKED  # Has dependencies
    
    # Verify task 2.1 (depends on 1.2)
    task_2_1 = next(t for t in todos if "2.1" in t.title)
    assert task_2_1.priority == Priority.P0_CRITICAL
    assert task_2_1.status == TodoStatus.BLOCKED


def test_parse_feature_yaml(tmp_path: Path, sample_feature_yaml: Path):
    """Test internal YAML parsing method."""
    state_mgr = StateManager(state_file=str(tmp_path / "test.db"))
    audit_logger = EnterpriseAuditLogger(log_dir=str(tmp_path / "logs"))
    orchestrator = TodoOrchestrator(state_manager=state_mgr, audit_logger=audit_logger)
    
    # Load and parse
    with open(sample_feature_yaml) as f:
        data = yaml.safe_load(f)
    
    # RED: This should fail until _parse_feature_yaml is implemented
    tasks = orchestrator._parse_feature_yaml(data)
    
    # Verify parsed tasks
    assert len(tasks) == 3, "Should parse 3 tasks"
    assert all("name" in t for t in tasks), "All tasks should have names"
    assert all("priority" in t for t in tasks), "All tasks should have priorities"
    assert all("dependencies" in t for t in tasks), "All tasks should have dependencies list"


def test_build_dag_from_tasks(tmp_path: Path):
    """Test DAG construction from parsed task list."""
    state_mgr = StateManager(state_file=str(tmp_path / "test.db"))
    audit_logger = EnterpriseAuditLogger(log_dir=str(tmp_path / "logs"))
    orchestrator = TodoOrchestrator(state_manager=state_mgr, audit_logger=audit_logger)
    
    # Create sample tasks
    tasks = [
        {
            "id": "task-1",
            "name": "Task 1",
            "priority": "P0_CRITICAL",
            "dependencies": [],
        },
        {
            "id": "task-2",
            "name": "Task 2",
            "priority": "P1_HIGH",
            "dependencies": ["task-1"],
        },
        {
            "id": "task-3",
            "name": "Task 3",
            "priority": "P1_HIGH",
            "dependencies": ["task-1"],
        },
        {
            "id": "task-4",
            "name": "Task 4",
            "priority": "P2_MEDIUM",
            "dependencies": ["task-2", "task-3"],
        },
    ]
    
    # RED: This should fail until _build_dag_from_tasks is implemented
    task_mapping = orchestrator._build_dag_from_tasks(tasks)
    
    # Verify DAG structure (using todo IDs, not task IDs)
    assert orchestrator.dag.has_node(task_mapping["task-1"])
    assert orchestrator.dag.has_node(task_mapping["task-2"])
    assert orchestrator.dag.has_node(task_mapping["task-3"])
    assert orchestrator.dag.has_node(task_mapping["task-4"])
    
    # Verify dependencies
    deps_2 = orchestrator.dag.get_dependencies(task_mapping["task-2"])
    assert task_mapping["task-1"] in deps_2
    
    deps_4 = orchestrator.dag.get_dependencies(task_mapping["task-4"])
    assert task_mapping["task-2"] in deps_4
    assert task_mapping["task-3"] in deps_4


def test_resolve_dependencies(tmp_path: Path):
    """Test dependency resolution from task IDs to todo IDs."""
    state_mgr = StateManager(state_file=str(tmp_path / "test.db"))
    audit_logger = EnterpriseAuditLogger(log_dir=str(tmp_path / "logs"))
    orchestrator = TodoOrchestrator(state_manager=state_mgr, audit_logger=audit_logger)
    
    # Create TODOs
    todo1_id = orchestrator.create_todo(
        title="Task 1",
        description="First task",
        priority=Priority.P0_CRITICAL
    )
    todo2_id = orchestrator.create_todo(
        title="Task 2",
        description="Second task",
        priority=Priority.P1_HIGH
    )
    
    # Build task mapping
    task_mapping = {
        "task-1": todo1_id,
        "task-2": todo2_id,
    }
    
    # Test dependency resolution
    task_deps = ["task-1"]
    resolved = orchestrator._resolve_dependencies(task_deps, task_mapping)
    
    assert resolved == [todo1_id], "Should resolve task ID to todo ID"
