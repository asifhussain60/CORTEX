"""
Integration Tests for Autonomous Execution Flow (Task 1.5.7)

End-to-end validation of autonomous execution without user intervention.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 1.0.0
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
from src.orchestrators.session_model import PlanningSession


@pytest.fixture
def orchestrator(tmp_path):
    """Create orchestrator instance for testing."""
    return PlanningOrchestrator(project_root=tmp_path)


class TestAutonomousExecutionFlow:
    """Test suite for end-to-end autonomous execution."""

    def test_autonomous_mode_detected_from_keywords(self, orchestrator):
        """Verifies autonomous keywords trigger correct mode."""
        from src.operations.modules.context.execution_mode_detector import ExecutionModeDetector
        
        detector = ExecutionModeDetector()
        
        # Test various autonomous phrases
        assert detector.detect("execute all phases autonomously") == "autonomous"
        assert detector.detect("run autonomously") == "autonomous"
        assert detector.detect("complete all phases") == "autonomous"
        assert detector.detect("proceed without stopping") == "autonomous"

    def test_interactive_mode_detected_by_default(self, orchestrator):
        """Verifies interactive mode is default."""
        from src.operations.modules.context.execution_mode_detector import ExecutionModeDetector
        
        detector = ExecutionModeDetector()
        
        assert detector.detect("plan user authentication") == "interactive"
        assert detector.detect("help me plan") == "interactive"

    def test_continuation_mode_detected(self, orchestrator):
        """Verifies continuation mode detection."""
        from src.operations.modules.context.execution_mode_detector import ExecutionModeDetector
        
        detector = ExecutionModeDetector()
        
        assert detector.detect("continue with phase 2") == "continuation"
        assert detector.detect("proceed to next phase") == "continuation"
        assert detector.detect("keep going") == "continuation"

    @patch.object(PlanningOrchestrator, '_classify_and_analyze')
    @patch.object(PlanningOrchestrator, '_route_and_execute')
    def test_execution_mode_stored_in_session(
        self, mock_execute, mock_classify, orchestrator
    ):
        """Validates execution mode stored in planning session."""
        # Setup
        mock_classify.return_value = Mock(tier=2)
        mock_execute.return_value = {'success': True}
        
        # Execute with autonomous keywords
        context = {'operation': 'execute all phases autonomously'}
        orchestrator.execute(context)
        
        # Verify
        assert orchestrator.session is not None
        assert hasattr(orchestrator.session, 'execution_mode')
        assert orchestrator.session.execution_mode == "autonomous"

    @patch.object(PlanningOrchestrator, '_classify_and_analyze')
    @patch.object(PlanningOrchestrator, '_route_and_execute')
    @patch.object(PlanningOrchestrator, '_generate_progress_summary')
    def test_template_selection_autonomous_mode(
        self, mock_summary, mock_execute, mock_classify, orchestrator
    ):
        """Validates autonomous template selected in autonomous mode."""
        # Setup
        mock_classify.return_value = Mock(tier=2)
        mock_execute.return_value = {'success': True}
        mock_summary.return_value = "Progress summary"
        
        # Execute with autonomous keywords
        context = {'operation': 'run all phases autonomously'}
        result = orchestrator.execute(context)
        
        # Verify
        assert result.data.get('template_name') == "autonomous_phase_execution"

    @patch.object(PlanningOrchestrator, '_classify_and_analyze')
    @patch.object(PlanningOrchestrator, '_route_and_execute')
    @patch.object(PlanningOrchestrator, '_generate_progress_summary')
    def test_template_selection_interactive_mode(
        self, mock_summary, mock_execute, mock_classify, orchestrator
    ):
        """Validates standard template selected in interactive mode."""
        # Setup
        mock_classify.return_value = Mock(tier=2)
        mock_execute.return_value = {'success': True}
        mock_summary.return_value = "Progress summary"
        
        # Execute without autonomous keywords
        context = {'operation': 'plan user authentication'}
        result = orchestrator.execute(context)
        
        # Verify
        assert result.data.get('template_name') == "plan_execution_standard"

    def test_select_response_template_method(self, orchestrator):
        """Validates _select_response_template() method logic."""
        # Test without session
        orchestrator.session = None
        assert orchestrator._select_response_template() == "plan_execution_standard"
        
        # Test with autonomous mode
        orchestrator.session = Mock()
        orchestrator.session.execution_mode = "autonomous"
        assert orchestrator._select_response_template() == "autonomous_phase_execution"
        
        # Test with continuation mode
        orchestrator.session.execution_mode = "continuation"
        assert orchestrator._select_response_template() == "autonomous_phase_execution"
        
        # Test with interactive mode
        orchestrator.session.execution_mode = "interactive"
        assert orchestrator._select_response_template() == "plan_execution_standard"

    @patch.object(PlanningOrchestrator, '_should_auto_progress')
    @patch.object(PlanningOrchestrator, '_execute_next_phase')
    @patch.object(PlanningOrchestrator, '_update_master_plan_tracker')
    @patch.object(PlanningOrchestrator, '_generate_phase_completion_summary')
    def test_auto_progression_triggers_after_phase(
        self, mock_summary, mock_update, mock_next, mock_should, orchestrator
    ):
        """Validates auto-progression triggers after phase completion."""
        # Setup
        orchestrator.session = Mock()
        orchestrator.session.phases = [{'name': 'Phase 1'}, {'name': 'Phase 2'}]
        orchestrator.session.execution_mode = "autonomous"
        orchestrator.current_plan_id = "test-plan"
        mock_should.return_value = True
        mock_summary.return_value = None
        
        # Execute
        orchestrator._complete_phase_autonomous(1)
        
        # Verify
        mock_next.assert_called_once()

    @patch.object(PlanningOrchestrator, '_should_auto_progress')
    @patch.object(PlanningOrchestrator, '_execute_next_phase')
    @patch.object(PlanningOrchestrator, '_update_master_plan_tracker')
    @patch.object(PlanningOrchestrator, '_generate_phase_completion_summary')
    def test_no_auto_progression_in_interactive_mode(
        self, mock_summary, mock_update, mock_next, mock_should, orchestrator
    ):
        """Ensures no auto-progression in interactive mode."""
        # Setup
        orchestrator.session = Mock()
        orchestrator.session.phases = [{'name': 'Phase 1'}, {'name': 'Phase 2'}]
        orchestrator.session.execution_mode = "interactive"
        orchestrator.current_plan_id = "test-plan"
        mock_should.return_value = False
        mock_summary.return_value = None
        
        # Execute
        orchestrator._complete_phase_autonomous(1)
        
        # Verify
        mock_next.assert_not_called()

    @patch.object(PlanningOrchestrator, '_generate_phase_completion_summary')
    @patch.object(PlanningOrchestrator, '_display_summary')
    @patch.object(PlanningOrchestrator, '_should_auto_progress')
    @patch.object(PlanningOrchestrator, '_update_master_plan_tracker')
    def test_phase_summary_displayed_in_autonomous_mode(
        self, mock_update, mock_should, mock_display, mock_generate, orchestrator
    ):
        """Validates phase completion summaries shown during autonomous execution."""
        # Setup
        orchestrator.session = Mock()
        orchestrator.session.phases = [{'name': 'Phase 1'}, {'name': 'Phase 2'}]
        orchestrator.session.execution_mode = "autonomous"
        orchestrator.current_plan_id = "test-plan"
        mock_generate.return_value = "Test Summary"
        mock_should.return_value = False
        
        # Execute
        orchestrator._complete_phase_autonomous(1)
        
        # Verify
        mock_generate.assert_called_once_with(1)
        mock_display.assert_called_once_with("Test Summary")

    def test_execution_mode_detector_comprehensive(self, orchestrator):
        """Comprehensive test of execution mode detection."""
        from src.operations.modules.context.execution_mode_detector import ExecutionModeDetector
        
        detector = ExecutionModeDetector()
        
        # Autonomous mode variations
        autonomous_phrases = [
            "execute all phases autonomously",
            "run all phases autonomously",
            "complete all autonomously",
            "continue automatically",
            "proceed without stopping",
            "no confirmation needed",
            "automatic execution mode"
        ]
        for phrase in autonomous_phrases:
            assert detector.detect(phrase) == "autonomous", f"Failed for: {phrase}"
        
        # Continuation mode variations
        continuation_phrases = [
            "continue with phase 3",
            "proceed to next phase",
            "continue execution",
            "keep going",
            "resume execution"
        ]
        for phrase in continuation_phrases:
            assert detector.detect(phrase) == "continuation", f"Failed for: {phrase}"
        
        # Interactive mode (default)
        interactive_phrases = [
            "plan authentication",
            "help me with planning",
            "what should I do",
            "create a plan"
        ]
        for phrase in interactive_phrases:
            assert detector.detect(phrase) == "interactive", f"Failed for: {phrase}"


class TestIntegrationWithExistingTests:
    """Validates integration with existing test suites."""

    def test_auto_progression_tests_exist(self):
        """Confirms auto-progression test module exists."""
        from tests.unit import test_auto_progression_logic
        assert hasattr(test_auto_progression_logic, 'TestAutoProgression')

    def test_progress_summaries_tests_exist(self):
        """Confirms progress summaries test module exists."""
        from tests.unit import test_incremental_progress_summaries
        assert hasattr(test_incremental_progress_summaries, 'TestProgressSummaries')

    def test_execution_mode_detector_exists(self):
        """Confirms execution mode detector module exists."""
        from src.operations.modules.context.execution_mode_detector import ExecutionModeDetector
        assert ExecutionModeDetector is not None


class TestResourceLimitsAndSafety:
    """Validates safety mechanisms in autonomous mode."""

    def test_max_phases_limit_enforced(self, orchestrator):
        """Ensures max consecutive phases prevents infinite loops."""
        orchestrator.session = Mock()
        orchestrator.session.execution_mode = "autonomous"
        orchestrator.session.max_consecutive_phases = 5
        orchestrator.current_plan_id = "test-plan"
        orchestrator.current_phase = 5
        orchestrator.metrics = {'errors': []}
        
        # Should not auto-progress when limit reached
        assert orchestrator._should_auto_progress() is False

    def test_error_detection_halts_autonomous_execution(self, orchestrator):
        """Validates errors halt autonomous execution."""
        orchestrator.session = Mock()
        orchestrator.session.execution_mode = "autonomous"
        orchestrator.session.max_consecutive_phases = 20
        orchestrator.current_plan_id = "test-plan"
        orchestrator.current_phase = 1
        orchestrator.metrics = {'errors': ["Critical error"]}
        
        # Should not auto-progress when errors present
        assert orchestrator._should_auto_progress() is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
