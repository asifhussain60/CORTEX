"""Tests for CAP-004: Critical Path Method (CPM).

Test-driven implementation of Critical Path Method for dependency-aware estimation.
Analyzes task dependencies to calculate optimal project duration with parallelization.

Acceptance Criteria:
- AC-CAP-004-AC01: Sequential tasks calculated correctly (sum of durations)
- AC-CAP-004-AC02: Parallel tasks identify critical path (longest path)
- AC-CAP-004-AC03: Complex dependency graphs analyzed with forward pass
- AC-CAP-004-AC04: Circular dependencies detected and raise error
- AC-CAP-004-AC05: Empty task list returns 0 hours
- AC-CAP-004-AC06: Task dependency ordering validated

Author: Asif Hussain
Date: 2026-01-30
Phase: 17 (Track C: Capacity Planning)
"""

import pytest
from cortex.capacity.multi_model_estimation_engine import (
    CriticalPathEstimator,
)


class TestCriticalPathSequential:
    """Test CPM with sequential (linear) task dependencies.
    
    AC-CAP-004-AC01: Sequential tasks calculated correctly
    """

    def test_sequential_three_tasks(self):
        """Test sequential dependency: A → B → C.
        
        Task A (8h) must complete before B (4h) starts.
        Task B must complete before C (6h) starts.
        Total duration = 8 + 4 + 6 = 18 hours
        """
        tasks = {
            "task_a": {"duration": 8.0, "dependencies": []},
            "task_b": {"duration": 4.0, "dependencies": ["task_a"]},
            "task_c": {"duration": 6.0, "dependencies": ["task_b"]},
        }
        
        duration = CriticalPathEstimator.calculate_critical_path(tasks)
        
        assert duration == 18.0, f"Expected 18h for sequential tasks, got {duration}h"

    def test_sequential_two_tasks(self):
        """Test simple two-task sequence: A → B."""
        tasks = {
            "task_a": {"duration": 10.0, "dependencies": []},
            "task_b": {"duration": 5.0, "dependencies": ["task_a"]},
        }
        
        duration = CriticalPathEstimator.calculate_critical_path(tasks)
        
        assert duration == 15.0

    def test_single_task_no_dependencies(self):
        """Test single task with no dependencies."""
        tasks = {
            "task_a": {"duration": 12.0, "dependencies": []},
        }
        
        duration = CriticalPathEstimator.calculate_critical_path(tasks)
        
        assert duration == 12.0


class TestCriticalPathParallel:
    """Test CPM with parallel task execution.
    
    AC-CAP-004-AC02: Parallel tasks identify critical path (longest path)
    """

    def test_parallel_two_branches(self):
        """Test parallel execution: A → [B, C] (B and C can run in parallel).
        
        Task A (8h) completes, then B (4h) and C (6h) run in parallel.
        Critical path = A → C = 14 hours (C is longer)
        """
        tasks = {
            "task_a": {"duration": 8.0, "dependencies": []},
            "task_b": {"duration": 4.0, "dependencies": ["task_a"]},
            "task_c": {"duration": 6.0, "dependencies": ["task_a"]},
        }
        
        duration = CriticalPathEstimator.calculate_critical_path(tasks)
        
        # Critical path: A (8h) → C (6h) = 14h
        assert duration == 14.0, f"Expected 14h (A→C critical path), got {duration}h"

    def test_parallel_three_independent_tasks(self):
        """Test three completely independent tasks (all parallel).
        
        With 3 workers, all can run simultaneously.
        Duration = longest task = 10 hours
        """
        tasks = {
            "task_a": {"duration": 10.0, "dependencies": []},
            "task_b": {"duration": 6.0, "dependencies": []},
            "task_c": {"duration": 4.0, "dependencies": []},
        }
        
        duration = CriticalPathEstimator.calculate_critical_path(tasks)
        
        # All parallel, so duration = max(10, 6, 4) = 10
        assert duration == 10.0

    def test_parallel_diamond_pattern(self):
        """Test diamond dependency pattern: A → [B, C] → D.
        
        A (8h) → B (4h) parallel C (6h) → D (3h)
        Critical path: A → C → D = 8 + 6 + 3 = 17h
        """
        tasks = {
            "task_a": {"duration": 8.0, "dependencies": []},
            "task_b": {"duration": 4.0, "dependencies": ["task_a"]},
            "task_c": {"duration": 6.0, "dependencies": ["task_a"]},
            "task_d": {"duration": 3.0, "dependencies": ["task_b", "task_c"]},
        }
        
        duration = CriticalPathEstimator.calculate_critical_path(tasks)
        
        # Critical path: A (8) → C (6) → D (3) = 17h
        assert duration == 17.0, f"Expected 17h (A→C→D), got {duration}h"


class TestCriticalPathComplex:
    """Test CPM with complex multi-level dependencies.
    
    AC-CAP-004-AC03: Complex dependency graphs analyzed with forward pass
    """

    def test_multi_level_dependencies(self):
        """Test complex 5-task dependency graph.
        
        A (10h) → B (5h) → D (8h)
        A (10h) → C (7h) → E (4h)
        
        Critical path: A → B → D = 10 + 5 + 8 = 23h
        """
        tasks = {
            "task_a": {"duration": 10.0, "dependencies": []},
            "task_b": {"duration": 5.0, "dependencies": ["task_a"]},
            "task_c": {"duration": 7.0, "dependencies": ["task_a"]},
            "task_d": {"duration": 8.0, "dependencies": ["task_b"]},
            "task_e": {"duration": 4.0, "dependencies": ["task_c"]},
        }
        
        duration = CriticalPathEstimator.calculate_critical_path(tasks)
        
        # Path 1: A → B → D = 10 + 5 + 8 = 23h (critical)
        # Path 2: A → C → E = 10 + 7 + 4 = 21h
        assert duration == 23.0

    def test_converging_paths(self):
        """Test multiple paths converging to final task.
        
        A (5h) → C (3h) → E (2h)
        B (8h) → D (4h) → E (2h)
        
        E depends on both C and D, so must wait for slowest path.
        Critical path: B → D → E = 8 + 4 + 2 = 14h
        """
        tasks = {
            "task_a": {"duration": 5.0, "dependencies": []},
            "task_b": {"duration": 8.0, "dependencies": []},
            "task_c": {"duration": 3.0, "dependencies": ["task_a"]},
            "task_d": {"duration": 4.0, "dependencies": ["task_b"]},
            "task_e": {"duration": 2.0, "dependencies": ["task_c", "task_d"]},
        }
        
        duration = CriticalPathEstimator.calculate_critical_path(tasks)
        
        # Critical path: B (8) → D (4) → E (2) = 14h
        assert duration == 14.0


class TestCriticalPathEdgeCases:
    """Test edge cases and error conditions.
    
    AC-CAP-004-AC04: Circular dependencies detected
    AC-CAP-004-AC05: Empty task list returns 0 hours
    """

    def test_empty_task_list_returns_zero(self):
        """Test empty task dictionary returns 0 hours.
        
        AC-CAP-004-AC05: Empty task list handling
        """
        tasks = {}
        
        duration = CriticalPathEstimator.calculate_critical_path(tasks)
        
        assert duration == 0.0

    def test_circular_dependency_raises_error(self):
        """Test circular dependency detection: A → B → A.
        
        AC-CAP-004-AC04: Circular dependencies detected
        """
        tasks = {
            "task_a": {"duration": 5.0, "dependencies": ["task_b"]},
            "task_b": {"duration": 3.0, "dependencies": ["task_a"]},
        }
        
        with pytest.raises(ValueError, match="[Cc]ircular|[Cc]ycle"):
            CriticalPathEstimator.calculate_critical_path(tasks)

    def test_self_dependency_raises_error(self):
        """Test task depending on itself raises error.
        
        AC-CAP-004-AC04: Self-dependency is circular
        """
        tasks = {
            "task_a": {"duration": 5.0, "dependencies": ["task_a"]},
        }
        
        with pytest.raises(ValueError, match="[Cc]ircular|[Cc]ycle"):
            CriticalPathEstimator.calculate_critical_path(tasks)

    def test_missing_dependency_raises_error(self):
        """Test reference to non-existent task raises error.
        
        AC-CAP-004-AC06: Dependency validation
        """
        tasks = {
            "task_a": {"duration": 5.0, "dependencies": ["task_nonexistent"]},
        }
        
        with pytest.raises((ValueError, KeyError)):
            CriticalPathEstimator.calculate_critical_path(tasks)


class TestCriticalPathParallelization:
    """Test parallelization opportunities identification."""

    def test_identifies_parallelizable_tasks(self):
        """Test CPM correctly identifies tasks that can run in parallel.
        
        In diamond pattern A → [B, C] → D:
        - B and C are parallelizable (both depend only on A)
        - D must wait for both B and C
        """
        tasks = {
            "task_a": {"duration": 5.0, "dependencies": []},
            "task_b": {"duration": 3.0, "dependencies": ["task_a"]},
            "task_c": {"duration": 4.0, "dependencies": ["task_a"]},
            "task_d": {"duration": 2.0, "dependencies": ["task_b", "task_c"]},
        }
        
        duration = CriticalPathEstimator.calculate_critical_path(tasks)
        
        # A (5) → C (4) → D (2) = 11h (C is critical between B and C)
        assert duration == 11.0

    def test_no_parallelization_benefit_for_sequential(self):
        """Test sequential tasks show no parallelization benefit."""
        # Sequential: A → B → C
        sequential_tasks = {
            "task_a": {"duration": 5.0, "dependencies": []},
            "task_b": {"duration": 3.0, "dependencies": ["task_a"]},
            "task_c": {"duration": 2.0, "dependencies": ["task_b"]},
        }
        
        # Parallel: A, B, C all independent
        parallel_tasks = {
            "task_a": {"duration": 5.0, "dependencies": []},
            "task_b": {"duration": 3.0, "dependencies": []},
            "task_c": {"duration": 2.0, "dependencies": []},
        }
        
        sequential_duration = CriticalPathEstimator.calculate_critical_path(sequential_tasks)
        parallel_duration = CriticalPathEstimator.calculate_critical_path(parallel_tasks)
        
        assert sequential_duration == 10.0  # 5 + 3 + 2
        assert parallel_duration == 5.0  # max(5, 3, 2)
        assert sequential_duration > parallel_duration, \
            "Parallel execution should be faster than sequential"
