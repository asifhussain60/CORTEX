"""
Unit Tests for Incremental Progress Summaries (Task 1.5.4)

Tests the phase completion summary generation and display.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 1.0.0
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta

from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
from src.orchestrators.session_model import PlanningSession


@pytest.fixture
def orchestrator(tmp_path):
    """Create orchestrator instance for testing."""
    orch = PlanningOrchestrator(project_root=tmp_path)
    orch.current_plan_id = "test-plan-1"
    return orch


@pytest.fixture
def mock_session():
    """Create mock planning session."""
    session = Mock(spec=PlanningSession)
    session.execution_mode = "autonomous"
    session.started_at = datetime.now() - timedelta(minutes=30)
    session.phases = [
        {'name': 'Phase 1', 'duration': 600},  # 10 minutes
        {'name': 'Phase 2', 'duration': 900},  # 15 minutes
        {'name': 'Phase 3', 'duration': 0}
    ]
    return session


class TestProgressSummaries:
    """Test suite for progress summary generation."""

    def test_generate_progress_bar_empty(self, orchestrator):
        """Validates empty progress bar at 0%."""
        bar = orchestrator._generate_progress_bar(0, width=10)
        assert bar == '░░░░░░░░░░'
        assert len(bar) == 10

    def test_generate_progress_bar_half(self, orchestrator):
        """Validates half-filled progress bar at 50%."""
        bar = orchestrator._generate_progress_bar(50, width=10)
        assert bar == '█████░░░░░'
        assert len(bar) == 10

    def test_generate_progress_bar_full(self, orchestrator):
        """Validates full progress bar at 100%."""
        bar = orchestrator._generate_progress_bar(100, width=10)
        assert bar == '██████████'
        assert len(bar) == 10

    def test_generate_progress_bar_custom_width(self, orchestrator):
        """Validates custom width progress bars."""
        bar = orchestrator._generate_progress_bar(25, width=20)
        assert len(bar) == 20
        assert bar.count('█') == 5
        assert bar.count('░') == 15

    def test_format_duration_seconds(self, orchestrator):
        """Validates duration formatting for seconds."""
        assert orchestrator._format_duration(30) == "30s"
        assert orchestrator._format_duration(59) == "59s"

    def test_format_duration_minutes(self, orchestrator):
        """Validates duration formatting for minutes."""
        assert orchestrator._format_duration(60) == "1m"
        assert orchestrator._format_duration(90) == "1m 30s"
        assert orchestrator._format_duration(600) == "10m"

    def test_format_duration_hours(self, orchestrator):
        """Validates duration formatting for hours."""
        assert orchestrator._format_duration(3600) == "1h 0m"
        assert orchestrator._format_duration(3660) == "1h 1m"
        assert orchestrator._format_duration(7200) == "2h 0m"

    def test_get_total_elapsed_time_without_session(self, orchestrator):
        """Ensures N/A returned when no session."""
        orchestrator.session = None
        assert orchestrator._get_total_elapsed_time() == "N/A"

    def test_get_total_elapsed_time_without_start(self, orchestrator, mock_session):
        """Ensures N/A returned when session has no start time."""
        delattr(mock_session, 'started_at')
        orchestrator.session = mock_session
        assert orchestrator._get_total_elapsed_time() == "N/A"

    def test_get_total_elapsed_time_calculates_correctly(self, orchestrator, mock_session):
        """Validates total elapsed time calculation."""
        orchestrator.session = mock_session
        elapsed = orchestrator._get_total_elapsed_time()
        
        # Should be around 30 minutes
        assert 'm' in elapsed
        assert elapsed != "N/A"

    @patch.object(PlanningOrchestrator, '_parse_phases_from_master_plan')
    def test_generate_phase_completion_summary_without_plan(
        self, mock_parse, orchestrator, mock_session, tmp_path
    ):
        """Ensures None returned when no active plan."""
        orchestrator.current_plan_id = None
        orchestrator.session = mock_session
        
        summary = orchestrator._generate_phase_completion_summary(1)
        
        assert summary is None

    @patch.object(PlanningOrchestrator, '_parse_phases_from_master_plan')
    def test_generate_phase_completion_summary_contains_required_sections(
        self, mock_parse, orchestrator, mock_session, tmp_path
    ):
        """Validates summary contains all required sections."""
        # Setup
        orchestrator.session = mock_session
        orchestrator.temp_plan_manager.active_dir = tmp_path / "active"
        plan_dir = orchestrator.temp_plan_manager.active_dir / "test-plan-1"
        plan_dir.mkdir(parents=True, exist_ok=True)
        master_plan = plan_dir / "00-master-plan.md"
        master_plan.write_text("# Master Plan\n")
        
        mock_parse.return_value = [
            {'name': 'Phase 1', 'tasks': [{'completed': True}, {'completed': True}]},
            {'name': 'Phase 2', 'tasks': []},
            {'name': 'Phase 3', 'tasks': []}
        ]
        
        # Execute
        summary = orchestrator._generate_phase_completion_summary(1)
        
        # Verify
        assert summary is not None
        assert "## 🧠 CORTEX Phase 1 Complete" in summary
        assert "Asif Hussain" in summary  # Flexible format check
        assert "### ✅ Phase Summary" in summary
        assert "### 📊 Overall Progress" in summary
        assert "### ⏭️ Continuing Execution" in summary
        assert "Phase 1: Phase 1" in summary

    @patch.object(PlanningOrchestrator, '_parse_phases_from_master_plan')
    def test_generate_phase_completion_summary_shows_progress_bar(
        self, mock_parse, orchestrator, mock_session, tmp_path
    ):
        """Validates progress bar appears in summary."""
        # Setup
        orchestrator.session = mock_session
        orchestrator.temp_plan_manager.active_dir = tmp_path / "active"
        plan_dir = orchestrator.temp_plan_manager.active_dir / "test-plan-1"
        plan_dir.mkdir(parents=True, exist_ok=True)
        master_plan = plan_dir / "00-master-plan.md"
        master_plan.write_text("# Master Plan\n")
        
        mock_parse.return_value = [
            {'name': 'Phase 1', 'tasks': []},
            {'name': 'Phase 2', 'tasks': []},
            {'name': 'Phase 3', 'tasks': []},
            {'name': 'Phase 4', 'tasks': []}
        ]
        
        # Execute - complete phase 2 of 4 (50%)
        summary = orchestrator._generate_phase_completion_summary(2)
        
        # Verify
        assert summary is not None
        assert '[' in summary and ']' in summary  # Progress bar markers
        assert '50%' in summary
        assert '(2/4 phases)' in summary

    @patch.object(PlanningOrchestrator, '_parse_phases_from_master_plan')
    def test_generate_phase_completion_summary_shows_next_phase(
        self, mock_parse, orchestrator, mock_session, tmp_path
    ):
        """Validates next phase information appears."""
        # Setup
        orchestrator.session = mock_session
        orchestrator.temp_plan_manager.active_dir = tmp_path / "active"
        plan_dir = orchestrator.temp_plan_manager.active_dir / "test-plan-1"
        plan_dir.mkdir(parents=True, exist_ok=True)
        master_plan = plan_dir / "00-master-plan.md"
        master_plan.write_text("# Master Plan\n")
        
        mock_parse.return_value = [
            {'name': 'Phase 1', 'tasks': []},
            {'name': 'Semantic Organization', 'tasks': [], 'estimated_duration': '2 hours'}
        ]
        
        # Execute
        summary = orchestrator._generate_phase_completion_summary(1)
        
        # Verify
        assert summary is not None
        assert "Next Phase:** Semantic Organization" in summary
        assert "Estimated Duration:** 2 hours" in summary
        assert "🎭 **Auto-progressing to Phase 2" in summary

    @patch.object(PlanningOrchestrator, '_parse_phases_from_master_plan')
    def test_generate_phase_completion_summary_final_phase(
        self, mock_parse, orchestrator, mock_session, tmp_path
    ):
        """Validates final phase shows completion message."""
        # Setup
        orchestrator.session = mock_session
        orchestrator.temp_plan_manager.active_dir = tmp_path / "active"
        plan_dir = orchestrator.temp_plan_manager.active_dir / "test-plan-1"
        plan_dir.mkdir(parents=True, exist_ok=True)
        master_plan = plan_dir / "00-master-plan.md"
        master_plan.write_text("# Master Plan\n")
        
        mock_parse.return_value = [
            {'name': 'Phase 1', 'tasks': []},
            {'name': 'Phase 2', 'tasks': []}
        ]
        
        # Execute - complete final phase
        summary = orchestrator._generate_phase_completion_summary(2)
        
        # Verify
        assert summary is not None
        assert "100%" in summary
        assert "(2/2 phases)" in summary
        assert "None - All phases complete" in summary

    def test_display_summary_logs_output(self, orchestrator, caplog):
        """Validates summary is logged for visibility."""
        import logging
        caplog.set_level(logging.INFO)
        
        test_summary = "Test Summary Content"
        orchestrator._display_summary(test_summary)
        
        # Verify logging
        assert "Phase Completion Summary" in caplog.text
        assert "Test Summary Content" in caplog.text

    @patch.object(PlanningOrchestrator, '_generate_phase_completion_summary')
    @patch.object(PlanningOrchestrator, '_display_summary')
    @patch.object(PlanningOrchestrator, '_should_auto_progress')
    @patch.object(PlanningOrchestrator, '_execute_next_phase')
    def test_complete_phase_autonomous_generates_summary(
        self, mock_next, mock_should, mock_display, mock_generate, 
        orchestrator, mock_session
    ):
        """Validates summary generation integrated into phase completion."""
        # Setup
        orchestrator.session = mock_session
        mock_generate.return_value = "Test Summary"
        mock_should.return_value = False
        
        # Execute
        orchestrator._complete_phase_autonomous(1)
        
        # Verify
        mock_generate.assert_called_once_with(1)
        mock_display.assert_called_once_with("Test Summary")

    @patch.object(PlanningOrchestrator, '_generate_phase_completion_summary')
    @patch.object(PlanningOrchestrator, '_display_summary')
    @patch.object(PlanningOrchestrator, '_should_auto_progress')
    def test_complete_phase_autonomous_skips_display_when_no_summary(
        self, mock_should, mock_display, mock_generate, 
        orchestrator, mock_session
    ):
        """Ensures no display when summary generation fails."""
        # Setup
        orchestrator.session = mock_session
        mock_generate.return_value = None
        mock_should.return_value = False
        
        # Execute
        orchestrator._complete_phase_autonomous(1)
        
        # Verify
        mock_generate.assert_called_once()
        mock_display.assert_not_called()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
