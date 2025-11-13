"""
Tests for Session-Ambient Correlation (CORTEX 3.0 Phase 3)
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from src.tier1.working_memory import WorkingMemory


class TestSessionAmbientCorrelation:
    """Test session-ambient event correlation."""
    
    @pytest.fixture
    def memory(self):
        """Create temporary working memory instance."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        
        wm = WorkingMemory(db_path=db_path)
        yield wm
        
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
    
    def test_log_ambient_event(self, memory):
        """Test logging ambient events linked to sessions."""
        # Create session first
        result = memory.handle_user_request(
            user_request="add authentication system",
            workspace_path="/projects/myapp"
        )
        
        session_id = result['session_id']
        conversation_id = result['conversation_id']
        
        # Log ambient event
        event_id = memory.log_ambient_event(
            session_id=session_id,
            conversation_id=conversation_id,
            event_type="file_change",
            file_path="/projects/myapp/src/auth.py",
            pattern="FEATURE",
            score=85,
            summary="Created auth.py with login logic",
            metadata={"lines_added": 150}
        )
        
        assert event_id > 0
    
    def test_get_session_events(self, memory):
        """Test retrieving all events for a session."""
        # Create session
        result = memory.handle_user_request(
            user_request="implement dashboard",
            workspace_path="/projects/myapp"
        )
        
        session_id = result['session_id']
        
        # Log multiple events
        memory.log_ambient_event(
            session_id=session_id,
            event_type="file_change",
            file_path="/projects/myapp/dashboard.tsx",
            pattern="FEATURE",
            score=90,
            summary="Created dashboard component"
        )
        
        memory.log_ambient_event(
            session_id=session_id,
            event_type="terminal_command",
            summary="npm run build",
            pattern="BUILD",
            score=70
        )
        
        memory.log_ambient_event(
            session_id=session_id,
            event_type="git_operation",
            summary="git commit -m 'Add dashboard'",
            pattern="FEATURE",
            score=60
        )
        
        # Get all events
        events = memory.get_session_events(session_id)
        
        assert len(events) == 3
        assert events[0]['event_type'] == "file_change"
        assert events[1]['event_type'] == "terminal_command"
        assert events[2]['event_type'] == "git_operation"
    
    def test_filter_events_by_type(self, memory):
        """Test filtering session events by type."""
        result = memory.handle_user_request(
            user_request="add tests",
            workspace_path="/projects/myapp"
        )
        
        session_id = result['session_id']
        
        # Log different event types
        memory.log_ambient_event(
            session_id=session_id,
            event_type="file_change",
            summary="Modified test file"
        )
        
        memory.log_ambient_event(
            session_id=session_id,
            event_type="terminal_command",
            summary="pytest tests/"
        )
        
        memory.log_ambient_event(
            session_id=session_id,
            event_type="file_change",
            summary="Added new test"
        )
        
        # Filter by file_change only
        file_events = memory.get_session_events(session_id, event_type="file_change")
        
        assert len(file_events) == 2
        assert all(e['event_type'] == "file_change" for e in file_events)
    
    def test_filter_events_by_score(self, memory):
        """Test filtering session events by minimum score."""
        result = memory.handle_user_request(
            user_request="optimize performance",
            workspace_path="/projects/myapp"
        )
        
        session_id = result['session_id']
        
        # Log events with different scores
        memory.log_ambient_event(
            session_id=session_id,
            event_type="file_change",
            summary="Minor config tweak",
            score=30
        )
        
        memory.log_ambient_event(
            session_id=session_id,
            event_type="file_change",
            summary="Major optimization",
            score=95
        )
        
        memory.log_ambient_event(
            session_id=session_id,
            event_type="file_change",
            summary="Critical bug fix",
            score=100
        )
        
        # Get high-priority events only (score >= 80)
        high_priority = memory.get_session_events(session_id, min_score=80)
        
        assert len(high_priority) == 2
        assert all(e['score'] >= 80 for e in high_priority)
    
    def test_get_conversation_events(self, memory):
        """Test getting events that occurred during a specific conversation."""
        # Create first conversation
        result1 = memory.handle_user_request(
            user_request="add login page",
            workspace_path="/projects/myapp"
        )
        
        session_id = result1['session_id']
        conv1_id = result1['conversation_id']
        
        # Log events during conversation 1
        memory.log_ambient_event(
            session_id=session_id,
            conversation_id=conv1_id,
            event_type="file_change",
            summary="Created login.tsx",
            score=90
        )
        
        memory.log_ambient_event(
            session_id=session_id,
            conversation_id=conv1_id,
            event_type="file_change",
            summary="Styled login form",
            score=70
        )
        
        # Start new conversation
        result2 = memory.handle_user_request(
            user_request="new conversation - add dashboard",
            workspace_path="/projects/myapp"
        )
        
        conv2_id = result2['conversation_id']
        
        # Log event during conversation 2
        memory.log_ambient_event(
            session_id=session_id,
            conversation_id=conv2_id,
            event_type="file_change",
            summary="Created dashboard.tsx",
            score=85
        )
        
        # Get events for conversation 1 only
        conv1_events = memory.get_conversation_events(conv1_id)
        
        assert len(conv1_events) == 2
        assert all("login" in e['summary'].lower() for e in conv1_events)
    
    def test_generate_session_narrative(self, memory):
        """Test generating complete session narrative."""
        # Create comprehensive session
        result = memory.handle_user_request(
            user_request="implement authentication system",
            workspace_path="/projects/myapp"
        )
        
        session_id = result['session_id']
        conv_id = result['conversation_id']
        
        # Log various events
        memory.log_ambient_event(
            session_id=session_id,
            conversation_id=conv_id,
            event_type="file_change",
            file_path="src/auth.py",
            pattern="FEATURE",
            score=90,
            summary="Created authentication module"
        )
        
        memory.log_ambient_event(
            session_id=session_id,
            conversation_id=conv_id,
            event_type="file_change",
            file_path="tests/test_auth.py",
            pattern="TESTING",
            score=85,
            summary="Added auth tests"
        )
        
        memory.log_ambient_event(
            session_id=session_id,
            conversation_id=conv_id,
            event_type="terminal_command",
            pattern="TESTING",
            score=75,
            summary="Ran pytest suite"
        )
        
        memory.log_ambient_event(
            session_id=session_id,
            conversation_id=conv_id,
            event_type="git_operation",
            pattern="FEATURE",
            score=60,
            summary="Committed auth implementation"
        )
        
        # Generate narrative
        narrative = memory.generate_session_narrative(session_id)
        
        # Verify narrative contains key information
        assert session_id in narrative
        assert "/projects/myapp" in narrative
        assert "Conversations:" in narrative or "conversation" in narrative.lower()
        assert "Activity" in narrative or "events" in narrative.lower()
        
        # Check event summaries appear
        assert "authentication module" in narrative
        assert "auth tests" in narrative
    
    def test_narrative_groups_by_pattern(self, memory):
        """Test that narrative groups events by pattern."""
        result = memory.handle_user_request(
            user_request="comprehensive update",
            workspace_path="/projects/myapp"
        )
        
        session_id = result['session_id']
        
        # Log events with different patterns
        memory.log_ambient_event(
            session_id=session_id,
            event_type="file_change",
            pattern="FEATURE",
            score=90,
            summary="Added new feature A"
        )
        
        memory.log_ambient_event(
            session_id=session_id,
            event_type="file_change",
            pattern="FEATURE",
            score=85,
            summary="Added new feature B"
        )
        
        memory.log_ambient_event(
            session_id=session_id,
            event_type="file_change",
            pattern="BUGFIX",
            score=95,
            summary="Fixed critical bug"
        )
        
        memory.log_ambient_event(
            session_id=session_id,
            event_type="file_change",
            pattern="DOCS",
            score=60,
            summary="Updated README"
        )
        
        narrative = memory.generate_session_narrative(session_id)
        
        # Should contain pattern sections
        assert "FEATURE" in narrative
        assert "BUGFIX" in narrative
        assert "DOCS" in narrative


class TestSessionCorrelationIntegration:
    """Integration tests for session correlation with handle_user_request."""
    
    @pytest.fixture
    def memory(self):
        """Create temporary working memory instance."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        
        wm = WorkingMemory(db_path=db_path)
        yield wm
        
        Path(db_path).unlink(missing_ok=True)
    
    def test_workflow_with_ambient_events(self, memory):
        """Test complete workflow: conversation + ambient events + narrative."""
        # Step 1: Start development work
        result1 = memory.handle_user_request(
            user_request="let's implement a purple button",
            workspace_path="/projects/myapp"
        )
        
        session_id = result1['session_id']
        conv_id = result1['conversation_id']
        
        # Step 2: Log file changes
        memory.log_ambient_event(
            session_id=session_id,
            conversation_id=conv_id,
            event_type="file_change",
            file_path="src/Button.tsx",
            pattern="FEATURE",
            score=85,
            summary="Created purple button component"
        )
        
        # Step 3: Continue conversation
        result2 = memory.handle_user_request(
            user_request="test the button functionality",
            workspace_path="/projects/myapp"
        )
        
        # Should be same conversation (workflow progression)
        assert result2['conversation_id'] == conv_id
        assert result2['workflow_state'] == "TESTING"
        
        # Step 4: Log test file creation
        memory.log_ambient_event(
            session_id=session_id,
            conversation_id=conv_id,
            event_type="file_change",
            file_path="tests/Button.test.tsx",
            pattern="TESTING",
            score=80,
            summary="Added button tests"
        )
        
        # Step 5: Get conversation events
        conv_events = memory.get_conversation_events(conv_id)
        
        assert len(conv_events) == 2
        assert conv_events[0]['summary'] == "Created purple button component"
        assert conv_events[1]['summary'] == "Added button tests"
        
        # Step 6: Generate narrative
        narrative = memory.generate_session_narrative(session_id)
        
        assert "purple button" in narrative.lower()
        assert "button tests" in narrative.lower()
        assert "FEATURE" in narrative
        assert "TESTING" in narrative
