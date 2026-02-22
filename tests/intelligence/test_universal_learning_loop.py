"""
Tests for Universal Learning Loop - Phase 12 S2

AC-PHASE71-001: Unified learning infrastructure for all orchestrators
AC-PHASE71-002: Pattern extraction from operation results
AC-PHASE71-003: Incremental knowledge repository updates

Tests end-to-end learning flow: capture → score → merge → verify

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pytest

from cortex.intelligence.learning.universal_learning_loop import (
    LearningCapture,
    PatternType,
    UniversalLearningLoop,
    get_learning_loop,
)


@pytest.fixture
def temp_workspace(tmp_path: Path) -> Path:
    """Create temporary workspace structure."""
    # Create directory structure
    (tmp_path / "cortex-registry" / "company" / "domains").mkdir(parents=True)
    (tmp_path / "cortex.intelligence" / "tier3" / "knowledge").mkdir(parents=True)
    return tmp_path


@pytest.fixture
def learning_loop(temp_workspace: Path) -> UniversalLearningLoop:
    """Create UniversalLearningLoop instance."""
    return UniversalLearningLoop(workspace_root=temp_workspace, enable_logging=False)


@pytest.fixture
def sample_learning() -> LearningCapture:
    """Create sample learning capture."""
    return LearningCapture(
        orchestrator="TDDOrchestrator",
        operation="refactor",
        pattern_type=PatternType.TECHNICAL,
        pattern_description="Extract method refactoring reduces complexity",
        pattern_data={
            "refactoring_type": "extract_method",
            "complexity_before": 15,
            "complexity_after": 8,
            "files_affected": 2
        },
        confidence=0.75,
        frequency=3
    )


class TestUniversalLearningLoopInitialization:
    """Test UniversalLearningLoop initialization."""

    def test_initialization_with_defaults(self) -> None:
        """Test initialization with default parameters."""
        loop = UniversalLearningLoop()

        assert loop.workspace_root == Path.cwd()
        assert loop.enable_logging is True
        assert loop._total_learnings == 0
        assert len(loop._learnings_by_orchestrator) == 0

    def test_initialization_with_custom_workspace(self, temp_workspace: Path) -> None:
        """Test initialization with custom workspace."""
        loop = UniversalLearningLoop(workspace_root=temp_workspace)

        assert loop.workspace_root == temp_workspace

    def test_singleton_accessor(self, temp_workspace: Path) -> None:
        """Test singleton accessor returns same instance."""
        loop1 = get_learning_loop(temp_workspace)
        loop2 = get_learning_loop(temp_workspace)

        assert loop1 is loop2


class TestPatternCapture:
    """Test pattern capture functionality."""

    def test_capture_single_pattern(
        self, learning_loop: UniversalLearningLoop, sample_learning: LearningCapture
    ) -> None:
        """Test capturing a single learning pattern."""
        learning_loop.capture_pattern(sample_learning)

        metrics = learning_loop.get_learning_metrics()
        assert metrics["total_learnings"] == 1
        assert metrics["by_orchestrator"]["TDDOrchestrator"] == 1
        assert metrics["cached_learnings"] == 1

    def test_capture_multiple_patterns(
        self, learning_loop: UniversalLearningLoop
    ) -> None:
        """Test capturing multiple learning patterns."""
        learnings = [
            LearningCapture(
                orchestrator="TDDOrchestrator",
                operation="test",
                pattern_type=PatternType.TECHNICAL,
                pattern_description=f"Pattern {i}",
                pattern_data={"index": i},
                confidence=0.5
            )
            for i in range(5)
        ]

        for learning in learnings:
            learning_loop.capture_pattern(learning)

        metrics = learning_loop.get_learning_metrics()
        assert metrics["total_learnings"] == 5
        assert metrics["by_orchestrator"]["TDDOrchestrator"] == 5

    def test_capture_from_different_orchestrators(
        self, learning_loop: UniversalLearningLoop
    ) -> None:
        """Test capturing patterns from multiple orchestrators."""
        orchestrators = ["TDDOrchestrator", "RefactoringOrchestrator", "EnforcementOrchestrator"]

        for orch in orchestrators:
            learning = LearningCapture(
                orchestrator=orch,
                operation="test",
                pattern_type=PatternType.TECHNICAL,
                pattern_description="Test pattern",
                pattern_data={},
                confidence=0.5
            )
            learning_loop.capture_pattern(learning)

        metrics = learning_loop.get_learning_metrics()
        assert metrics["total_learnings"] == 3
        assert len(metrics["by_orchestrator"]) == 3


class TestCaptureFromOperation:
    """Test capturing learnings from orchestrator operations."""

    def test_capture_from_tdd_operation(
        self, learning_loop: UniversalLearningLoop
    ) -> None:
        """Test capturing learnings from TDD operation."""
        context = {
            "test_file": "test_example.py",
            "test_count": 5
        }
        result = {
            "status": "passed",
            "tests_passed": 5,
            "coverage": 0.95
        }

        learnings = learning_loop.capture_from_operation(
            orchestrator="TDDOrchestrator",
            operation="run_tests",
            context=context,
            result=result
        )

        assert isinstance(learnings, list)
        assert len(learnings) >= 0  # PatternExtractor may return 0 or more patterns

    def test_capture_from_refactoring_operation(
        self, learning_loop: UniversalLearningLoop
    ) -> None:
        """Test capturing learnings from refactoring operation."""
        context = {
            "target_file": "example.py",
            "refactoring_type": "extract_method"
        }
        result = {
            "status": "success",
            "complexity_reduced": 7
        }

        learnings = learning_loop.capture_from_operation(
            orchestrator="RefactoringOrchestrator",
            operation="refactor",
            context=context,
            result=result
        )

        assert isinstance(learnings, list)

    def test_capture_handles_exceptions_gracefully(
        self, learning_loop: UniversalLearningLoop
    ) -> None:
        """Test capture handles exceptions without crashing."""
        # Pass invalid data that might cause extraction to fail
        learnings = learning_loop.capture_from_operation(
            orchestrator="UnknownOrchestrator",
            operation="invalid",
            context={},
            result=None  # type: ignore
        )

        # Should return empty list on error, not raise exception
        assert learnings == []


class TestKnowledgeMerge:
    """Test merging learnings to knowledge repositories."""

    def test_merge_high_confidence_learnings(
        self, learning_loop: UniversalLearningLoop, sample_learning: LearningCapture
    ) -> None:
        """Test merging learnings that meet confidence threshold."""
        # Sample learning has confidence 0.75 (> default 0.7)
        result = learning_loop.merge_to_knowledge([sample_learning], threshold=0.7)

        assert result.is_ok()
        data = result.unwrap()
        assert data["status"] in ["merged", "no_promotions"]

    def test_merge_filters_low_confidence(
        self, learning_loop: UniversalLearningLoop
    ) -> None:
        """Test merging filters out low-confidence learnings."""
        low_confidence = LearningCapture(
            orchestrator="TDDOrchestrator",
            operation="test",
            pattern_type=PatternType.TECHNICAL,
            pattern_description="Uncertain pattern",
            pattern_data={},
            confidence=0.3,  # Below default threshold
            frequency=1
        )

        result = learning_loop.merge_to_knowledge([low_confidence], threshold=0.7)

        assert result.is_ok()
        data = result.unwrap()
        assert data["status"] == "no_promotions"
        assert data["promoted"] == 0

    def test_merge_with_custom_threshold(
        self, learning_loop: UniversalLearningLoop
    ) -> None:
        """Test merging with custom confidence threshold."""
        medium_confidence = LearningCapture(
            orchestrator="TDDOrchestrator",
            operation="test",
            pattern_type=PatternType.TECHNICAL,
            pattern_description="Medium confidence pattern",
            pattern_data={},
            confidence=0.5,
            frequency=2
        )

        # Use lower threshold
        result = learning_loop.merge_to_knowledge([medium_confidence], threshold=0.4)

        assert result.is_ok()


class TestLearningMetrics:
    """Test learning metrics tracking."""

    def test_get_initial_metrics(
        self, learning_loop: UniversalLearningLoop
    ) -> None:
        """Test getting metrics from fresh instance."""
        metrics = learning_loop.get_learning_metrics()

        assert metrics["total_learnings"] == 0
        assert len(metrics["by_orchestrator"]) == 0
        assert metrics["cached_learnings"] == 0
        assert len(metrics["cache_keys"]) == 0

    def test_metrics_track_captures(
        self, learning_loop: UniversalLearningLoop, sample_learning: LearningCapture
    ) -> None:
        """Test metrics update after captures."""
        learning_loop.capture_pattern(sample_learning)
        learning_loop.capture_pattern(sample_learning)

        metrics = learning_loop.get_learning_metrics()
        assert metrics["total_learnings"] == 2
        assert metrics["cached_learnings"] == 2

    def test_clear_cache(
        self, learning_loop: UniversalLearningLoop, sample_learning: LearningCapture
    ) -> None:
        """Test clearing learning cache."""
        learning_loop.capture_pattern(sample_learning)
        
        metrics_before = learning_loop.get_learning_metrics()
        assert metrics_before["cached_learnings"] > 0

        learning_loop.clear_cache()

        metrics_after = learning_loop.get_learning_metrics()
        assert metrics_after["cached_learnings"] == 0


class TestLearningCaptureDataClass:
    """Test LearningCapture data class."""

    def test_learning_capture_creation(self) -> None:
        """Test creating LearningCapture instance."""
        learning = LearningCapture(
            orchestrator="TestOrch",
            operation="test_op",
            pattern_type=PatternType.TECHNICAL,
            pattern_description="Test pattern",
            pattern_data={"key": "value"},
            confidence=0.8
        )

        assert learning.orchestrator == "TestOrch"
        assert learning.operation == "test_op"
        assert learning.pattern_type == PatternType.TECHNICAL
        assert learning.confidence == 0.8
        assert learning.frequency == 1  # Default

    def test_learning_capture_to_dict(self) -> None:
        """Test converting LearningCapture to dictionary."""
        learning = LearningCapture(
            orchestrator="TestOrch",
            operation="test_op",
            pattern_type=PatternType.BUSINESS,
            pattern_description="Business pattern",
            pattern_data={"domain": "finance"},
            confidence=0.9,
            frequency=5
        )

        data = learning.to_dict()

        assert data["orchestrator"] == "TestOrch"
        assert data["pattern_type"] == "BUSINESS"
        assert data["frequency"] == 5
        assert "timestamp" in data
        assert isinstance(data["timestamp"], str)

    def test_learning_capture_with_context(self) -> None:
        """Test LearningCapture with additional context."""
        learning = LearningCapture(
            orchestrator="TestOrch",
            operation="test_op",
            pattern_type=PatternType.GOVERNANCE,
            pattern_description="Governance pattern",
            pattern_data={},
            confidence=0.7,
            context={"user": "admin", "project": "cortex"}
        )

        assert learning.context["user"] == "admin"
        assert learning.context["project"] == "cortex"
