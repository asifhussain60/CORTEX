"""
Test Suite for GitHubCopilotTodoBridge Component

Purpose: Validate conversion of TodoManager tasks to GitHub Copilot format
Test Strategy: TDD RED→GREEN→REFACTOR
AC-IDs: AC-COPILOT-001, AC-COPILOT-002, AC-COPILOT-006, AC-COPILOT-007, AC-COPILOT-008

Author: CORTEX 6.0
Created: 2026-01-10
"""

import pytest
from typing import List, Dict, Any
from datetime import datetime
from unittest.mock import Mock, MagicMock

# Import will fail initially (RED phase) - this is expected
try:
    from src.orchestrators.core.github_copilot_todo_bridge import (
        GitHubCopilotTodoBridge,
        CopilotTodo,
        Task,
        TaskStatus
    )
except ImportError:
    # Expected during RED phase
    pass


# ==============================================================================
# Test Fixtures
# ==============================================================================

@pytest.fixture
def mock_governance_merger():
    """Mock GovernanceMerger for testing governance rule extraction."""
    merger = Mock()
    merger.get_unified_instruction_set.return_value = {
        "rules": [
            {"id": "CORE-001", "description": "Incremental execution (<500 lines)"},
            {"id": "CORE-008", "description": "TDD required (write tests first)"},
            {"id": "CORE-005", "description": "Use pathlib.Path for file operations"},
            {"id": "CORE-019", "description": "TDD-Master required for development"}
        ]
    }
    return merger


@pytest.fixture
def simple_task():
    """Single simple task with no dependencies."""
    return Task(
        id=1,
        title="Implement user authentication",
        description="Create JWT-based authentication system",
        status=TaskStatus.PENDING,
        priority=1,
        ac_id="AC-AUTH-001",
        affected_files=["src/auth/jwt_handler.py", "tests/auth/test_jwt_handler.py"],
        dependencies=[],
        estimated_loc=250
    )


@pytest.fixture
def task_with_dependencies():
    """Task with dependencies on other tasks."""
    return Task(
        id=3,
        title="Implement API endpoint",
        description="Create REST API endpoint for user management",
        status=TaskStatus.PENDING,
        priority=3,
        ac_id="AC-API-001",
        affected_files=["src/api/user_endpoint.py"],
        dependencies=[1, 2],  # Depends on tasks 1 and 2
        estimated_loc=150
    )


@pytest.fixture
def in_progress_task():
    """Task currently in progress."""
    return Task(
        id=2,
        title="Implement database schema",
        description="Create user and role tables",
        status=TaskStatus.IN_PROGRESS,
        priority=2,
        ac_id="AC-DB-001",
        affected_files=["src/models/user.py"],
        dependencies=[],
        estimated_loc=100
    )


@pytest.fixture
def failed_task():
    """Task that failed execution."""
    return Task(
        id=4,
        title="Deploy to production",
        description="Deploy application to production environment",
        status=TaskStatus.FAILED,
        priority=4,
        ac_id="AC-DEPLOY-001",
        affected_files=[],
        dependencies=[1, 2, 3],
        estimated_loc=0,
        failure_reason="Environment credentials missing"
    )


@pytest.fixture
def blocked_task():
    """Task blocked by dependencies."""
    return Task(
        id=5,
        title="Performance testing",
        description="Load test API endpoints",
        status=TaskStatus.BLOCKED,
        priority=5,
        ac_id="AC-PERF-001",
        affected_files=["tests/performance/test_api_load.py"],
        dependencies=[3],
        estimated_loc=200,
        blocked_by="AC-API-001 must complete first"
    )


@pytest.fixture
def bridge(mock_governance_merger):
    """GitHubCopilotTodoBridge instance with mock governance."""
    return GitHubCopilotTodoBridge(governance_merger=mock_governance_merger)


# ==============================================================================
# AC-COPILOT-001: Core Component Tests
# ==============================================================================

class TestGitHubCopilotTodoBridgeCore:
    """Test core bridge functionality."""
    
    def test_bridge_instantiation(self, mock_governance_merger):
        """Bridge instantiates with governance merger dependency."""
        bridge = GitHubCopilotTodoBridge(governance_merger=mock_governance_merger)
        assert bridge is not None
        assert bridge.governance_merger == mock_governance_merger
    
    def test_format_for_copilot_with_empty_list(self, bridge):
        """Empty task list returns empty Copilot todo list."""
        result = bridge.format_for_copilot([])
        assert result == []
        assert isinstance(result, list)
    
    def test_format_for_copilot_with_single_task(self, bridge, simple_task):
        """Single task converts to Copilot format with all required fields."""
        result = bridge.format_for_copilot([simple_task])
        
        assert len(result) == 1
        copilot_todo = result[0]
        
        # Validate required fields
        assert "id" in copilot_todo
        assert "title" in copilot_todo
        assert "description" in copilot_todo
        assert "status" in copilot_todo
        
        # Validate types
        assert isinstance(copilot_todo["id"], int)
        assert isinstance(copilot_todo["title"], str)
        assert isinstance(copilot_todo["description"], str)
        assert copilot_todo["status"] in ["not-started", "in-progress", "completed"]
    
    def test_format_for_copilot_with_multiple_tasks(self, bridge, simple_task, in_progress_task):
        """Multiple tasks convert correctly with preserved order."""
        tasks = [simple_task, in_progress_task]
        result = bridge.format_for_copilot(tasks)
        
        assert len(result) == 2
        assert result[0]["id"] == simple_task.id
        assert result[1]["id"] == in_progress_task.id
    
    def test_format_for_copilot_performance(self, bridge):
        """Bridge processes 100 tasks in <5ms."""
        import time
        
        # Create 100 simple tasks
        tasks = [
            Task(
                id=i,
                title=f"Task {i}",
                description=f"Description {i}",
                status=TaskStatus.PENDING,
                priority=i,
                ac_id=f"AC-TEST-{i:03d}",
                affected_files=[],
                dependencies=[],
                estimated_loc=100
            )
            for i in range(1, 101)
        ]
        
        start = time.perf_counter()
        result = bridge.format_for_copilot(tasks)
        duration_ms = (time.perf_counter() - start) * 1000
        
        assert len(result) == 100
        assert duration_ms < 5.0, f"Bridge took {duration_ms:.2f}ms (threshold: 5ms)"


# ==============================================================================
# AC-COPILOT-006: Title Generation Tests
# ==============================================================================

class TestTitleGeneration:
    """Test title generation algorithm."""
    
    def test_generate_title_action_verb_extraction(self, bridge):
        """Extracts action verb correctly."""
        task = Task(
            id=1,
            title="implement user authentication system",
            description="",
            status=TaskStatus.PENDING,
            priority=1,
            ac_id="AC-TEST-001",
            affected_files=[],
            dependencies=[],
            estimated_loc=100
        )
        
        title = bridge._generate_title(task)
        assert title.startswith("Implement")
        assert "User Authentication" in title
    
    def test_generate_title_max_length_truncation(self, bridge):
        """Title truncated to 50 chars max."""
        task = Task(
            id=1,
            title="implement comprehensive enterprise-grade authentication and authorization system",
            description="",
            status=TaskStatus.PENDING,
            priority=1,
            ac_id="AC-TEST-001",
            affected_files=[],
            dependencies=[],
            estimated_loc=100
        )
        
        title = bridge._generate_title(task)
        assert len(title) <= 50
    
    def test_generate_title_title_case_formatting(self, bridge, simple_task):
        """Title uses Title Case formatting."""
        title = bridge._generate_title(simple_task)
        
        # Should be "Implement User Authentication", not "implement user authentication"
        words = title.split()
        for word in words:
            if len(word) > 3:  # Skip short words like "and", "for"
                assert word[0].isupper(), f"Word '{word}' should start with uppercase"
    
    def test_generate_title_empty_task_name(self, bridge):
        """Handles empty task name gracefully."""
        task = Task(
            id=1,
            title="",
            description="Some description",
            status=TaskStatus.PENDING,
            priority=1,
            ac_id="AC-TEST-001",
            affected_files=[],
            dependencies=[],
            estimated_loc=100
        )
        
        title = bridge._generate_title(task)
        assert title != ""
        assert len(title) > 0


# ==============================================================================
# AC-COPILOT-007: Description Generation Tests
# ==============================================================================

class TestDescriptionGeneration:
    """Test description generation with context."""
    
    def test_generate_description_includes_objective(self, bridge, simple_task):
        """Description includes clear objective."""
        description = bridge._generate_description(simple_task)
        
        # Should include task description
        assert "JWT-based authentication" in description or "authentication" in description
    
    def test_generate_description_includes_governance_rules(self, bridge, simple_task):
        """Description includes top governance rules."""
        description = bridge._generate_description(simple_task)
        
        # Should include governance section
        assert "**Governance:**" in description or "Governance:" in description
        
        # Should include at least one SKULL rule
        assert "CORE-" in description
    
    def test_generate_description_includes_ac_id(self, bridge, simple_task):
        """Description includes AC-ID for traceability."""
        description = bridge._generate_description(simple_task)
        
        assert "**AC-ID:**" in description or "AC-ID:" in description
        assert simple_task.ac_id in description
    
    def test_generate_description_includes_affected_files(self, bridge, simple_task):
        """Description includes file paths."""
        description = bridge._generate_description(simple_task)
        
        assert "**Files:**" in description or "Files:" in description
        assert "src/auth/jwt_handler.py" in description
        assert "tests/auth/test_jwt_handler.py" in description
    
    def test_generate_description_includes_dependencies(self, bridge, task_with_dependencies):
        """Description includes dependency information."""
        description = bridge._generate_description(task_with_dependencies)
        
        assert "**Dependencies:**" in description or "Dependencies:" in description
        assert "Task 1" in description or "1" in description
        assert "Task 2" in description or "2" in description
    
    def test_generate_description_max_length(self, bridge, simple_task):
        """Description respects 2000 char limit."""
        description = bridge._generate_description(simple_task)
        
        assert len(description) <= 2000


# ==============================================================================
# AC-COPILOT-008: Status Mapping Tests
# ==============================================================================

class TestStatusMapping:
    """Test TodoManager status to Copilot status mapping."""
    
    def test_map_status_pending_to_not_started(self, bridge, simple_task):
        """PENDING maps to not-started."""
        status = bridge._map_status(simple_task)
        assert status == "not-started"
    
    def test_map_status_in_progress(self, bridge, in_progress_task):
        """IN_PROGRESS maps to in-progress."""
        status = bridge._map_status(in_progress_task)
        assert status == "in-progress"
    
    def test_map_status_complete(self, bridge):
        """COMPLETE maps to completed."""
        task = Task(
            id=1,
            title="Completed task",
            description="",
            status=TaskStatus.COMPLETE,
            priority=1,
            ac_id="AC-TEST-001",
            affected_files=[],
            dependencies=[],
            estimated_loc=100
        )
        
        status = bridge._map_status(task)
        assert status == "completed"
    
    def test_map_status_failed_to_not_started(self, bridge, failed_task):
        """FAILED maps to not-started (with failure note in description)."""
        status = bridge._map_status(failed_task)
        assert status == "not-started"
        
        # Verify failure reason is included
        description = bridge._generate_description(failed_task)
        assert "Environment credentials missing" in description
    
    def test_map_status_blocked_to_not_started(self, bridge, blocked_task):
        """BLOCKED maps to not-started (with blocker note)."""
        status = bridge._map_status(blocked_task)
        assert status == "not-started"
        
        # Verify blocker info is included
        description = bridge._generate_description(blocked_task)
        assert "AC-API-001 must complete first" in description
    
    def test_map_status_cancelled_excluded(self, bridge):
        """CANCELLED tasks are excluded from output."""
        task = Task(
            id=1,
            title="Cancelled task",
            description="",
            status=TaskStatus.CANCELLED,
            priority=1,
            ac_id="AC-TEST-001",
            affected_files=[],
            dependencies=[],
            estimated_loc=100
        )
        
        result = bridge.format_for_copilot([task])
        assert len(result) == 0  # CANCELLED tasks excluded


# ==============================================================================
# AC-COPILOT-002: Governance Context Injection Tests
# ==============================================================================

class TestGovernanceInjection:
    """Test governance rule extraction and injection."""
    
    def test_extract_relevant_rules(self, bridge, simple_task):
        """Extracts top 3-5 relevant SKULL rules."""
        rules = bridge._extract_relevant_rules(simple_task)
        
        assert len(rules) >= 1
        assert len(rules) <= 5
        
        # Each rule should have id and description
        for rule in rules:
            assert "id" in rule
            assert "description" in rule
    
    def test_governance_rules_in_description(self, bridge, simple_task):
        """Governance rules appear in task description."""
        description = bridge._generate_description(simple_task)
        
        # Should have governance section
        assert "Governance" in description
        
        # Should list SKULL rules
        assert "CORE-" in description
    
    def test_rule_formatting_concise(self, bridge, simple_task):
        """Rule formatting is concise (not full text)."""
        description = bridge._generate_description(simple_task)
        
        # Should be formatted as "CORE-XXX: Brief description"
        # Not multi-paragraph full rule text
        lines = description.split("\n")
        governance_lines = [line for line in lines if "CORE-" in line]
        
        for line in governance_lines:
            # Each line should be reasonably short
            assert len(line) < 200


# ==============================================================================
# Edge Cases and Error Handling
# ==============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_handles_none_task_gracefully(self, bridge):
        """Handles None in task list gracefully."""
        result = bridge.format_for_copilot([None])
        
        # Should either skip None or raise clear error
        # (Implementation choice - both acceptable)
        assert isinstance(result, list)
    
    def test_handles_missing_optional_fields(self, bridge):
        """Handles tasks with missing optional fields."""
        minimal_task = Task(
            id=1,
            title="Minimal task",
            description="",
            status=TaskStatus.PENDING,
            priority=1,
            ac_id="AC-TEST-001",
            affected_files=[],
            dependencies=[],
            estimated_loc=0
        )
        
        result = bridge.format_for_copilot([minimal_task])
        assert len(result) == 1
        assert result[0]["title"] != ""
        assert result[0]["description"] != ""
    
    def test_handles_very_long_description(self, bridge):
        """Handles tasks with very long descriptions."""
        long_task = Task(
            id=1,
            title="Long task",
            description="x" * 5000,  # 5000 chars
            status=TaskStatus.PENDING,
            priority=1,
            ac_id="AC-TEST-001",
            affected_files=[],
            dependencies=[],
            estimated_loc=100
        )
        
        result = bridge.format_for_copilot([long_task])
        
        # Description should be truncated to 2000 chars
        assert len(result[0]["description"]) <= 2000


# ==============================================================================
# Integration with TodoManager (Smoke Tests)
# ==============================================================================

class TestTodoManagerIntegration:
    """Smoke tests for TodoManager integration."""
    
    def test_accepts_todo_manager_task_objects(self, bridge, simple_task):
        """Bridge accepts Task objects from TodoManager."""
        # This test validates the interface contract
        result = bridge.format_for_copilot([simple_task])
        assert len(result) == 1
    
    def test_preserves_task_order(self, bridge):
        """Task order is preserved in output."""
        tasks = [
            Task(id=i, title=f"Task {i}", description="", status=TaskStatus.PENDING,
                 priority=i, ac_id=f"AC-{i}", affected_files=[], dependencies=[], estimated_loc=100)
            for i in range(1, 6)
        ]
        
        result = bridge.format_for_copilot(tasks)
        
        for i, copilot_todo in enumerate(result, start=1):
            assert copilot_todo["id"] == i
