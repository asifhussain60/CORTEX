"""
Unit tests for Onboarding Orchestrator & Flow Engine.

Validates the OnboardingOrchestrator implementation with:
- Async/await pattern support
- Journey state machine (NEW -> IN_PROGRESS -> COMPLETED)
- Result[T] error handling
- Audit logging of all onboarding events
"""

import pytest
from src.orchestrators.onboarding.orchestrator import (
    OnboardingOrchestrator,
    JourneyState,
    Result,
    JourneyProgress
)


class TestOnboardingOrchestrator:
    """Test suite for onboarding orchestrator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = OnboardingOrchestrator()
    
    def test_create_journey_success(self):
        """Test successful journey creation."""
        result = self.orchestrator.create_journey(
            'j1',
            'user1',
            ['activity1', 'activity2', 'activity3']
        )
        
        assert result.success is True
        assert result.value.state == JourneyState.NEW
        assert result.value.activities_completed == 0
        assert result.value.total_activities == 3
    
    def test_create_journey_duplicate(self):
        """Test that duplicate journeys are rejected."""
        self.orchestrator.create_journey('j1', 'user1', ['a1'])
        result = self.orchestrator.create_journey('j1', 'user2', ['a1'])
        
        assert result.success is False
        assert 'already exists' in result.error
    
    def test_start_journey_success(self):
        """Test successful journey start."""
        self.orchestrator.create_journey('j1', 'user1', ['a1', 'a2'])
        result = self.orchestrator.start_journey('j1')
        
        assert result.success is True
        assert result.value.state == JourneyState.IN_PROGRESS
    
    def test_start_journey_not_found(self):
        """Test starting non-existent journey."""
        result = self.orchestrator.start_journey('nonexistent')
        
        assert result.success is False
        assert 'not found' in result.error
    
    def test_start_journey_already_started(self):
        """Test starting already-started journey."""
        self.orchestrator.create_journey('j1', 'user1', ['a1'])
        self.orchestrator.start_journey('j1')
        result = self.orchestrator.start_journey('j1')
        
        assert result.success is False
        assert 'already in state' in result.error
    
    def test_complete_activity_success(self):
        """Test successful activity completion."""
        self.orchestrator.create_journey('j1', 'user1', ['a1', 'a2', 'a3'])
        self.orchestrator.start_journey('j1')
        result = self.orchestrator.complete_activity('j1', 0)
        
        assert result.success is True
        assert result.value.activities_completed == 1
    
    def test_complete_activity_not_started(self):
        """Test completing activity in non-started journey."""
        self.orchestrator.create_journey('j1', 'user1', ['a1'])
        result = self.orchestrator.complete_activity('j1', 0)
        
        assert result.success is False
        assert 'not in progress' in result.error
    
    def test_complete_activity_out_of_range(self):
        """Test completing activity with invalid index."""
        self.orchestrator.create_journey('j1', 'user1', ['a1', 'a2'])
        self.orchestrator.start_journey('j1')
        result = self.orchestrator.complete_activity('j1', 5)
        
        assert result.success is False
        assert 'out of range' in result.error
    
    def test_complete_journey_success(self):
        """Test successful journey completion."""
        self.orchestrator.create_journey('j1', 'user1', ['a1'])
        self.orchestrator.start_journey('j1')
        result = self.orchestrator.complete_journey('j1')
        
        assert result.success is True
        assert result.value.state == JourneyState.COMPLETED
        assert result.value.completed_at is not None
    
    def test_complete_journey_not_started(self):
        """Test completing non-started journey."""
        self.orchestrator.create_journey('j1', 'user1', ['a1'])
        result = self.orchestrator.complete_journey('j1')
        
        assert result.success is False
        assert 'not in progress' in result.error
    
    def test_get_journey_progress(self):
        """Test retrieving journey progress."""
        self.orchestrator.create_journey('j1', 'user1', ['a1', 'a2'])
        self.orchestrator.start_journey('j1')
        self.orchestrator.complete_activity('j1', 0)
        
        result = self.orchestrator.get_journey_progress('j1')
        
        assert result.success is True
        assert result.value.activities_completed == 1
        assert result.value.total_activities == 2
    
    def test_audit_log_journey_created(self):
        """Test that journey creation is logged."""
        self.orchestrator.create_journey('j1', 'user1', ['a1'])
        
        logs = self.orchestrator.get_audit_log()
        
        assert len(logs) > 0
        assert logs[0]['event_type'] == 'journey_created'
        assert logs[0]['journey_id'] == 'j1'
        assert logs[0]['user_id'] == 'user1'
    
    def test_audit_log_journey_started(self):
        """Test that journey start is logged."""
        self.orchestrator.create_journey('j1', 'user1', ['a1'])
        self.orchestrator.start_journey('j1')
        
        logs = self.orchestrator.get_audit_log()
        
        journey_start_logs = [
            log for log in logs if log['event_type'] == 'journey_started'
        ]
        assert len(journey_start_logs) > 0
    
    def test_audit_log_activity_completed(self):
        """Test that activity completion is logged."""
        self.orchestrator.create_journey('j1', 'user1', ['a1'])
        self.orchestrator.start_journey('j1')
        self.orchestrator.complete_activity('j1', 0)
        
        logs = self.orchestrator.get_audit_log()
        
        activity_logs = [
            log for log in logs if log['event_type'] == 'activity_completed'
        ]
        assert len(activity_logs) > 0
        assert activity_logs[0]['metadata']['activity_index'] == 0
    
    def test_audit_log_journey_completed(self):
        """Test that journey completion is logged."""
        self.orchestrator.create_journey('j1', 'user1', ['a1'])
        self.orchestrator.start_journey('j1')
        self.orchestrator.complete_journey('j1')
        
        logs = self.orchestrator.get_audit_log()
        
        completion_logs = [
            log for log in logs if log['event_type'] == 'journey_completed'
        ]
        assert len(completion_logs) > 0
    
    def test_state_machine_sequence(self):
        """Test complete journey state machine sequence."""
        # Create
        self.orchestrator.create_journey('j1', 'user1', ['a1', 'a2'])
        progress = self.orchestrator.get_journey_progress('j1').value
        assert progress.state == JourneyState.NEW
        
        # Start
        self.orchestrator.start_journey('j1')
        progress = self.orchestrator.get_journey_progress('j1').value
        assert progress.state == JourneyState.IN_PROGRESS
        
        # Complete all activities
        self.orchestrator.complete_activity('j1', 0)
        self.orchestrator.complete_activity('j1', 1)
        
        # Complete journey
        self.orchestrator.complete_journey('j1')
        progress = self.orchestrator.get_journey_progress('j1').value
        assert progress.state == JourneyState.COMPLETED
        assert progress.activities_completed == 2
    
    def test_audit_log_completeness(self):
        """Test that all events are logged."""
        self.orchestrator.create_journey('j1', 'user1', ['a1'])
        self.orchestrator.start_journey('j1')
        self.orchestrator.complete_activity('j1', 0)
        self.orchestrator.complete_journey('j1')
        
        logs = self.orchestrator.get_audit_log()
        
        assert len(logs) == 4  # create, start, complete_activity, complete_journey
        event_types = [log['event_type'] for log in logs]
        assert 'journey_created' in event_types
        assert 'journey_started' in event_types
        assert 'activity_completed' in event_types
        assert 'journey_completed' in event_types
    
    def test_multiple_journeys(self):
        """Test managing multiple user journeys."""
        self.orchestrator.create_journey('j1', 'user1', ['a1'])
        self.orchestrator.create_journey('j2', 'user2', ['a1', 'a2'])
        self.orchestrator.start_journey('j1')
        self.orchestrator.start_journey('j2')
        
        progress1 = self.orchestrator.get_journey_progress('j1').value
        progress2 = self.orchestrator.get_journey_progress('j2').value
        
        assert progress1.state == JourneyState.IN_PROGRESS
        assert progress2.state == JourneyState.IN_PROGRESS
        assert progress1.total_activities == 1
        assert progress2.total_activities == 2
