"""
Tests for Phase Boundary Reporter
==================================
Tests phase-boundary progress reporting logic.

Author: GitHub Copilot (for CORTEX)
Created: 2026-01-08
Feature: feat04-core-orchestration
Phase: 3 Task: 3.3
TDD Phase: RED → GREEN → REFACTOR
"""

import pytest

from src.orchestrators.middleware.phase_boundary_reporter import (
    PhaseBoundaryReporter,
    PhaseEvent,
    PhaseUpdate
)


class TestPhaseBoundaryReporter:
    """Test phase boundary reporter"""
    
    def test_initializes_empty(self):
        """Should initialize with empty state"""
        reporter = PhaseBoundaryReporter()
        assert reporter.current_phase is None
        assert len(reporter.phase_updates) == 0
    
    def test_phase_started_creates_update(self):
        """Should create update for phase start"""
        reporter = PhaseBoundaryReporter()
        
        update = reporter.phase_started("Phase 1", total_tasks=5)
        
        assert update.phase_name == "Phase 1"
        assert update.event == PhaseEvent.STARTED
        assert update.tasks_total == 5
        assert reporter.current_phase == "Phase 1"
    
    def test_task_completed_suppressed_by_default(self):
        """Should suppress task completion by default"""
        reporter = PhaseBoundaryReporter()
        reporter.phase_started("Phase 1", total_tasks=3)
        
        update = reporter.task_completed("task1")
        
        assert update is None  # Suppressed
        assert reporter.suppressed_task_count == 1
    
    def test_task_completed_tracked_internally(self):
        """Should track task completion internally"""
        reporter = PhaseBoundaryReporter()
        reporter.phase_started("Phase 1", total_tasks=3)
        
        reporter.task_completed("task1")
        reporter.task_completed("task2")
        
        assert reporter.phase_task_count["Phase 1"] == 2
    
    def test_task_completed_not_suppressed_when_requested(self):
        """Should allow non-silent task updates"""
        reporter = PhaseBoundaryReporter()
        reporter.phase_started("Phase 1", total_tasks=3)
        
        update = reporter.task_completed("task1", silent=False)
        
        assert update is not None
        assert update.event == PhaseEvent.COMPLETED
        assert update.tasks_completed == 1
    
    def test_phase_completed_includes_summary(self):
        """Should include summary in completion update"""
        reporter = PhaseBoundaryReporter()
        reporter.phase_started("Phase 1", total_tasks=3)
        
        reporter.task_completed("task1")
        reporter.task_completed("task2")
        reporter.task_completed("task3")
        
        update = reporter.phase_completed("Phase 1")
        
        assert update.event == PhaseEvent.COMPLETED
        assert update.tasks_completed == 3
        assert update.tasks_total == 3
        assert "3 task updates suppressed" in update.message
    
    def test_phase_completed_resets_current_phase(self):
        """Should reset current phase on completion"""
        reporter = PhaseBoundaryReporter()
        reporter.phase_started("Phase 1")
        reporter.phase_completed("Phase 1")
        
        assert reporter.current_phase is None
    
    def test_phase_failed_creates_error_update(self):
        """Should create error update for phase failure"""
        reporter = PhaseBoundaryReporter()
        reporter.phase_started("Phase 1", total_tasks=5)
        reporter.task_completed("task1")
        
        update = reporter.phase_failed("Phase 1", "Test error")
        
        assert update.event == PhaseEvent.FAILED
        assert "Test error" in update.message
        assert update.metadata["error"] == "Test error"
        assert reporter.current_phase is None
    
    def test_get_phase_updates_returns_all(self):
        """Should return all phase updates"""
        reporter = PhaseBoundaryReporter()
        reporter.phase_started("Phase 1")
        reporter.phase_completed("Phase 1")
        
        updates = reporter.get_phase_updates()
        
        assert len(updates) == 2
    
    def test_get_phase_updates_filters_by_phase(self):
        """Should filter updates by phase name"""
        reporter = PhaseBoundaryReporter()
        reporter.phase_started("Phase 1")
        reporter.phase_completed("Phase 1")
        reporter.phase_started("Phase 2")
        reporter.phase_completed("Phase 2")
        
        updates = reporter.get_phase_updates("Phase 1")
        
        assert len(updates) == 2
        assert all(u.phase_name == "Phase 1" for u in updates)
    
    def test_multiple_phases_tracked_separately(self):
        """Should track multiple phases separately"""
        reporter = PhaseBoundaryReporter()
        
        reporter.phase_started("Phase 1", total_tasks=2)
        reporter.task_completed("task1")
        reporter.phase_completed("Phase 1")
        
        reporter.phase_started("Phase 2", total_tasks=3)
        reporter.task_completed("task2")
        reporter.task_completed("task3")
        reporter.phase_completed("Phase 2")
        
        phase1_updates = reporter.get_phase_updates("Phase 1")
        phase2_updates = reporter.get_phase_updates("Phase 2")
        
        assert len(phase1_updates) == 2  # Start + Complete
        assert len(phase2_updates) == 2
    
    def test_reset_clears_all_state(self):
        """Should clear all state on reset"""
        reporter = PhaseBoundaryReporter()
        reporter.phase_started("Phase 1")
        reporter.task_completed("task1")
        
        reporter.reset()
        
        assert reporter.current_phase is None
        assert len(reporter.phase_updates) == 0
        assert reporter.suppressed_task_count == 0
