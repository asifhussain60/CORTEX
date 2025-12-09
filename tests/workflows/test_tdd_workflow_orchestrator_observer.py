"""
Test suite for TDD Workflow Orchestrator observer pattern integration.

Tests observer subscription, event emission at TDD cycle completion,
and integration with LearningObserver for pattern capture.

Author: Asif Hussain
Created: 2025-12-09
Phase: TDD Mastery Phase 5.1 (Task 5.1.3)
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

from src.workflows.tdd_workflow_orchestrator import TDDWorkflowOrchestrator, TDDWorkflowConfig
from src.orchestrators.learning_observer import LearningObserver


@pytest.fixture
def temp_project_dir():
    """Create temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def tdd_config(temp_project_dir):
    """Create TDD workflow configuration for testing."""
    return TDDWorkflowConfig(
        project_root=temp_project_dir,
        enable_session_tracking=True,
        enable_refactoring=True,
        enable_git_checkpoints=False,  # Disable for testing
        enable_terminal_integration=False,  # Disable for testing
        enable_programmatic_execution=False,  # Disable for testing
        enable_caching=False  # Disable for testing
    )


@pytest.fixture
def orchestrator(tdd_config):
    """Create TDD Workflow Orchestrator instance."""
    return TDDWorkflowOrchestrator(tdd_config)


@pytest.fixture
def mock_observer():
    """Create mock observer for testing."""
    observer = Mock()
    observer.on_tdd_cycle_completion = Mock()
    return observer


class TestTDDOrchestratorObserverSubscription:
    """Test observer subscription and unsubscription."""
    
    def test_subscribe_adds_observer_to_list(self, orchestrator, mock_observer):
        """Test that subscribe() adds observer to observers list."""
        orchestrator.subscribe(mock_observer)
        assert mock_observer in orchestrator.observers
    
    def test_subscribe_multiple_observers(self, orchestrator):
        """Test subscribing multiple observers."""
        observer1 = Mock()
        observer2 = Mock()
        observer3 = Mock()
        
        orchestrator.subscribe(observer1)
        orchestrator.subscribe(observer2)
        orchestrator.subscribe(observer3)
        
        assert len(orchestrator.observers) == 3
        assert observer1 in orchestrator.observers
        assert observer2 in orchestrator.observers
        assert observer3 in orchestrator.observers
    
    def test_unsubscribe_removes_observer(self, orchestrator, mock_observer):
        """Test that unsubscribe() removes observer from list."""
        orchestrator.subscribe(mock_observer)
        assert mock_observer in orchestrator.observers
        
        orchestrator.unsubscribe(mock_observer)
        assert mock_observer not in orchestrator.observers
    
    def test_unsubscribe_nonexistent_observer(self, orchestrator, mock_observer):
        """Test unsubscribing observer that was never subscribed."""
        # Should not raise exception
        orchestrator.unsubscribe(mock_observer)
        assert mock_observer not in orchestrator.observers
    
    def test_subscribe_same_observer_twice(self, orchestrator, mock_observer):
        """Test subscribing same observer twice (should add only once)."""
        orchestrator.subscribe(mock_observer)
        orchestrator.subscribe(mock_observer)
        
        # Should appear only once
        assert orchestrator.observers.count(mock_observer) == 1


class TestTDDOrchestratorEventEmission:
    """Test event emission at TDD cycle completion."""
    
    def test_cycle_completion_emits_event(self, orchestrator, mock_observer, temp_project_dir):
        """Test that completing TDD cycle emits event to observers."""
        orchestrator.subscribe(mock_observer)
        
        # Start session and complete cycle
        source_file = Path(temp_project_dir) / "test_module.py"
        source_file.write_text("def sample_function():\n    return True\n")
        
        orchestrator.start_session("test_feature")
        
        # Mock state machine to simulate cycle completion
        with patch.object(orchestrator, 'state_machine') as mock_state:
            mock_state.get_cycle_metrics.return_value = [{
                'cycle_number': 1,
                'red_duration': 5.0,
                'green_duration': 10.0,
                'refactor_duration': 8.0,
                'total_duration': 23.0,
                'tests_written': 5,
                'tests_passing': 5,
                'code_lines_added': 25,
                'code_lines_refactored': 10
            }]
            
            orchestrator.complete_cycle()
        
        # Verify event was emitted
        assert mock_observer.on_tdd_cycle_completion.called
    
    def test_event_payload_contains_required_fields(self, orchestrator, mock_observer):
        """Test that event payload contains all required fields."""
        orchestrator.subscribe(mock_observer)
        orchestrator.start_session("test_feature")
        
        with patch.object(orchestrator, 'state_machine') as mock_state:
            mock_state.get_cycle_metrics.return_value = [{
                'cycle_number': 1,
                'red_duration': 5.0,
                'green_duration': 10.0,
                'refactor_duration': 8.0,
                'total_duration': 23.0,
                'tests_written': 5,
                'tests_passing': 5,
                'code_lines_added': 25,
                'code_lines_refactored': 10
            }]
            
            orchestrator.complete_cycle()
        
        # Extract event payload
        call_args = mock_observer.on_tdd_cycle_completion.call_args
        event_data = call_args[0][0] if call_args else {}
        
        # Verify required fields
        assert 'session_id' in event_data
        assert 'feature_name' in event_data
        assert 'cycle_number' in event_data
        assert 'red_duration' in event_data
        assert 'green_duration' in event_data
        assert 'refactor_duration' in event_data
        assert 'total_duration' in event_data
        assert 'tests_written' in event_data
        assert 'tests_passing' in event_data
        assert 'timestamp' in event_data
    
    def test_multiple_observers_notified(self, orchestrator):
        """Test that all subscribed observers receive events."""
        observer1 = Mock()
        observer2 = Mock()
        observer3 = Mock()
        
        observer1.on_tdd_cycle_completion = Mock()
        observer2.on_tdd_cycle_completion = Mock()
        observer3.on_tdd_cycle_completion = Mock()
        
        orchestrator.subscribe(observer1)
        orchestrator.subscribe(observer2)
        orchestrator.subscribe(observer3)
        
        orchestrator.start_session("test_feature")
        
        with patch.object(orchestrator, 'state_machine') as mock_state:
            mock_state.get_cycle_metrics.return_value = [{'cycle_number': 1}]
            orchestrator.complete_cycle()
        
        # Verify all observers notified
        assert observer1.on_tdd_cycle_completion.called
        assert observer2.on_tdd_cycle_completion.called
        assert observer3.on_tdd_cycle_completion.called
    
    def test_observer_failure_does_not_break_other_observers(self, orchestrator):
        """Test that one observer failure doesn't prevent others from being notified."""
        failing_observer = Mock()
        failing_observer.on_tdd_cycle_completion = Mock(side_effect=Exception("Observer error"))
        
        working_observer = Mock()
        working_observer.on_tdd_cycle_completion = Mock()
        
        orchestrator.subscribe(failing_observer)
        orchestrator.subscribe(working_observer)
        
        orchestrator.start_session("test_feature")
        
        with patch.object(orchestrator, 'state_machine') as mock_state:
            mock_state.get_cycle_metrics.return_value = [{'cycle_number': 1}]
            orchestrator.complete_cycle()
        
        # Working observer should still be notified
        assert working_observer.on_tdd_cycle_completion.called
    
    def test_no_event_emitted_if_no_observers(self, orchestrator):
        """Test that cycle completion works even with no observers."""
        orchestrator.start_session("test_feature")
        
        with patch.object(orchestrator, 'state_machine') as mock_state:
            mock_state.get_cycle_metrics.return_value = [{'cycle_number': 1}]
            
            # Should not raise exception
            result = orchestrator.complete_cycle()
            assert result is not None
    
    def test_event_includes_test_to_code_ratio(self, orchestrator, mock_observer):
        """Test that event includes test-to-code ratio calculation."""
        orchestrator.subscribe(mock_observer)
        orchestrator.start_session("test_feature")
        
        with patch.object(orchestrator, 'state_machine') as mock_state:
            mock_state.get_cycle_metrics.return_value = [{
                'cycle_number': 1,
                'tests_written': 10,
                'code_lines_added': 50
            }]
            
            orchestrator.complete_cycle()
        
        call_args = mock_observer.on_tdd_cycle_completion.call_args
        event_data = call_args[0][0] if call_args else {}
        
        # Should calculate ratio: tests_written / code_lines_added
        assert 'test_to_code_ratio' in event_data
        expected_ratio = 10 / 50  # 0.2
        assert abs(event_data['test_to_code_ratio'] - expected_ratio) < 0.01


class TestTDDOrchestratorLearningObserverIntegration:
    """Test end-to-end integration with LearningObserver."""
    
    def test_learning_observer_receives_tdd_events(self, orchestrator, temp_project_dir):
        """Test that LearningObserver receives and processes TDD cycle events."""
        # Create mock KG for observer
        mock_kg = Mock()
        mock_kg.store_pattern = Mock(return_value=None)
        
        observer = LearningObserver(mock_kg)
        orchestrator.subscribe(observer)
        
        orchestrator.start_session("test_feature")
        
        with patch.object(orchestrator, 'state_machine') as mock_state:
            mock_state.get_cycle_metrics.return_value = [{
                'cycle_number': 1,
                'red_duration': 5.0,
                'green_duration': 10.0,
                'refactor_duration': 8.0,
                'total_duration': 23.0,
                'tests_written': 5,
                'tests_passing': 5,
                'code_lines_added': 25,
                'code_lines_refactored': 10
            }]
            
            orchestrator.complete_cycle()
        
        # Verify KG received pattern
        assert mock_kg.store_pattern.called
        
        # Verify pattern content
        call_args = mock_kg.store_pattern.call_args
        pattern_type = call_args[1]['pattern_type']
        
        # LearningObserver uses 'tdd_cycle' as pattern type
        assert pattern_type == 'tdd_cycle'
