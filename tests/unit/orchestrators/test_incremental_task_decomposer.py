# AC-ID: AC-TDD-INCREMENTAL-01 - IncrementalTaskDecomposer Tests
"""
Tests for IncrementalTaskDecomposer.

Validates task decomposition with token budget estimation and
evidence-based sizing using Phase 12 CAP framework.

Governance:
- CORE-008: TDD (tests first)
- CORE-011: Type hints on all functions
- CORE-012: Google-style docstrings
- CORE-013: Specific exception handling

Author: Asif Hussain
Date: 2026-02-02
"""

import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock

from cortex.orchestrators.planning.incremental_task_decomposer import (
    IncrementalTaskDecomposer,
    SubTask,
    TaskDecompositionResult,
)
from cortex.core.result import Ok, Err


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def decomposer() -> IncrementalTaskDecomposer:
    """Create IncrementalTaskDecomposer instance."""
    return IncrementalTaskDecomposer()


@pytest.fixture
def simple_task() -> Dict[str, Any]:
    """Create simple task specification."""
    return {
        "task_id": "TASK-001",
        "description": "Implement user authentication service",
        "module_path": "cortex.auth.service",
        "domain": "security",
        "acceptance_criteria": [
            "User can login with email/password",
            "Session tokens are secure",
            "Failed login attempts are tracked"
        ]
    }


@pytest.fixture
def complex_task() -> Dict[str, Any]:
    """Create complex task specification."""
    return {
        "task_id": "TASK-002",
        "description": "Implement complete REST API with authentication, authorization, CRUD operations, pagination, caching, and logging",
        "module_path": "cortex.api.service",
        "domain": "backend",
        "acceptance_criteria": [
            "All REST endpoints implement CRUD",
            "JWT authentication required",
            "Role-based authorization",
            "Pagination for list endpoints",
            "Redis caching layer",
            "Structured logging"
        ]
    }


# =============================================================================
# AC-TDD-INCREMENTAL-01-01: Initialization Tests
# =============================================================================

class TestIncrementalTaskDecomposerInitialization:
    """Tests for IncrementalTaskDecomposer initialization."""

    def test_initialization_default(
        self,
        decomposer: IncrementalTaskDecomposer
    ) -> None:
        """Initializes with default token budget limits.

        AC-TDD-INCREMENTAL-01-01-01: Default token budget = 10K per subtask
        """
        assert decomposer.max_tokens_per_subtask == 10000
        assert decomposer.evidence_collector is not None

    def test_initialization_custom_token_limit(self) -> None:
        """Initializes with custom token budget limit.

        AC-TDD-INCREMENTAL-01-01-02: Custom token limits supported
        """
        decomposer = IncrementalTaskDecomposer(max_tokens_per_subtask=5000)
        assert decomposer.max_tokens_per_subtask == 5000


# =============================================================================
# AC-TDD-INCREMENTAL-01-02: Task Decomposition Tests
# =============================================================================

class TestTaskDecomposition:
    """Tests for task decomposition logic."""

    def test_decompose_simple_task_single_subtask(
        self,
        decomposer: IncrementalTaskDecomposer,
        simple_task: Dict[str, Any]
    ) -> None:
        """Decomposes simple task into single subtask.

        AC-TDD-INCREMENTAL-01-02-01: Simple tasks remain as single subtask
        """
        result = decomposer.decompose_into_subtasks(simple_task)

        assert result.is_ok()
        decomposition = result.unwrap()
        assert isinstance(decomposition, TaskDecompositionResult)
        assert len(decomposition.subtasks) == 1
        assert decomposition.total_estimated_tokens <= 10000

    def test_decompose_complex_task_multiple_subtasks(
        self,
        decomposer: IncrementalTaskDecomposer,
        complex_task: Dict[str, Any]
    ) -> None:
        """Decomposes complex task into multiple subtasks.

        AC-TDD-INCREMENTAL-01-02-02: Complex tasks split by token budget
        """
        result = decomposer.decompose_into_subtasks(complex_task)

        assert result.is_ok()
        decomposition = result.unwrap()
        assert len(decomposition.subtasks) >= 2
        
        # Each subtask should be within token budget
        for subtask in decomposition.subtasks:
            assert subtask.estimated_tokens <= decomposer.max_tokens_per_subtask

    def test_decompose_preserves_task_metadata(
        self,
        decomposer: IncrementalTaskDecomposer,
        simple_task: Dict[str, Any]
    ) -> None:
        """Preserves task metadata in subtasks.

        AC-TDD-INCREMENTAL-01-02-03: Metadata preserved across decomposition
        """
        result = decomposer.decompose_into_subtasks(simple_task)

        assert result.is_ok()
        decomposition = result.unwrap()
        subtask = decomposition.subtasks[0]
        
        assert subtask.parent_task_id == simple_task["task_id"]
        assert subtask.module_path == simple_task["module_path"]
        assert subtask.domain == simple_task["domain"]

    def test_decompose_invalid_task_fails(
        self,
        decomposer: IncrementalTaskDecomposer
    ) -> None:
        """Returns error for invalid task specification.

        AC-TDD-INCREMENTAL-01-02-04: Validates task structure
        """
        invalid_task = {"task_id": "INVALID"}  # Missing required fields

        result = decomposer.decompose_into_subtasks(invalid_task)

        assert result.is_err()
        assert "description" in result.error.lower()


# =============================================================================
# AC-TDD-INCREMENTAL-01-03: Token Budget Estimation Tests
# =============================================================================

class TestTokenBudgetEstimation:
    """Tests for token budget estimation."""

    def test_estimate_token_budget_for_simple_task(
        self,
        decomposer: IncrementalTaskDecomposer,
        simple_task: Dict[str, Any]
    ) -> None:
        """Estimates reasonable token budget for simple task.

        AC-TDD-INCREMENTAL-01-03-01: Simple task < 5K tokens
        """
        result = decomposer.estimate_token_budget_per_task(simple_task)

        assert result.is_ok()
        tokens = result.unwrap()
        assert 1000 <= tokens <= 5000

    def test_estimate_token_budget_for_complex_task(
        self,
        decomposer: IncrementalTaskDecomposer,
        complex_task: Dict[str, Any]
    ) -> None:
        """Estimates higher token budget for complex task.

        AC-TDD-INCREMENTAL-01-03-02: Complex task > 5K tokens
        """
        result = decomposer.estimate_token_budget_per_task(complex_task)

        assert result.is_ok()
        tokens = result.unwrap()
        assert tokens > 5000

    def test_estimate_uses_evidence_collector(
        self,
        decomposer: IncrementalTaskDecomposer,
        simple_task: Dict[str, Any]
    ) -> None:
        """Uses EvidenceCollector for complexity assessment.

        AC-TDD-INCREMENTAL-01-03-03: Integrates with CAP framework
        """
        with patch.object(decomposer.evidence_collector, 'collect_evidence') as mock_collect:
            mock_collect.return_value = Mock(
                lens_complexity={"score": 3.5},
                git_churn={"frequency": "low"}
            )

            result = decomposer.estimate_token_budget_per_task(simple_task)

            assert result.is_ok()
            mock_collect.assert_called_once()


# =============================================================================
# AC-TDD-INCREMENTAL-01-04: Subtask Dependencies Tests
# =============================================================================

class TestSubtaskDependencies:
    """Tests for subtask dependency tracking."""

    def test_subtasks_have_sequential_order(
        self,
        decomposer: IncrementalTaskDecomposer,
        complex_task: Dict[str, Any]
    ) -> None:
        """Subtasks maintain sequential execution order.

        AC-TDD-INCREMENTAL-01-04-01: Sequential order preserved
        """
        result = decomposer.decompose_into_subtasks(complex_task)

        assert result.is_ok()
        decomposition = result.unwrap()
        
        for i, subtask in enumerate(decomposition.subtasks):
            assert subtask.sequence_number == i + 1

    def test_subtask_dependencies_tracked(
        self,
        decomposer: IncrementalTaskDecomposer,
        complex_task: Dict[str, Any]
    ) -> None:
        """Tracks dependencies between subtasks.

        AC-TDD-INCREMENTAL-01-04-02: Dependencies explicit
        """
        result = decomposer.decompose_into_subtasks(complex_task)

        assert result.is_ok()
        decomposition = result.unwrap()
        
        # Each subtask (except first) depends on previous
        for i in range(1, len(decomposition.subtasks)):
            subtask = decomposition.subtasks[i]
            assert len(subtask.depends_on) >= 1


# =============================================================================
# AC-TDD-INCREMENTAL-01-05: Integration Tests
# =============================================================================

class TestIntegrationWithCAP:
    """Tests for integration with Phase 12 CAP framework."""

    def test_evidence_collector_integration(
        self,
        decomposer: IncrementalTaskDecomposer,
        simple_task: Dict[str, Any]
    ) -> None:
        """Integrates with EvidenceCollector for complexity assessment.

        AC-TDD-INCREMENTAL-01-05-01: CAP framework integration
        """
        result = decomposer.decompose_into_subtasks(simple_task)

        assert result.is_ok()
        decomposition = result.unwrap()
        assert decomposition.evidence_used is not None

    def test_pert_estimation_used(
        self,
        decomposer: IncrementalTaskDecomposer,
        complex_task: Dict[str, Any]
    ) -> None:
        """Uses PERT estimation for subtask sizing.

        AC-TDD-INCREMENTAL-01-05-02: PERT estimation applied
        """
        result = decomposer.decompose_into_subtasks(complex_task)

        assert result.is_ok()
        decomposition = result.unwrap()
        
        # Verify each subtask has PERT-based estimates
        for subtask in decomposition.subtasks:
            assert subtask.estimated_tokens > 0
            assert hasattr(subtask, 'confidence_score')
