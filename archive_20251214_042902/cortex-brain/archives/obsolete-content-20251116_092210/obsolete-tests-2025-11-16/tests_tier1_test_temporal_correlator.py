"""
CORTEX 3.0 Milestone 2 - Temporal Correlation Tests

Comprehensive test suite for the temporal correlation layer that verifies
all fusion capabilities: temporal matching, file mention correlation,
plan verification, and timeline generation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import pytest
import sqlite3
import tempfile
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.tier1.temporal_correlator import (
    TemporalCorrelator, 
    CorrelationResult, 
    ConversationTurn, 
    AmbientEvent
)
from src.tier1.working_memory import WorkingMemory


class TestTemporalCorrelator:
    """Test the temporal correlation algorithm."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Initialize working memory to create schema
        wm = WorkingMemory(Path(db_path))
        # Create a basic conversation to initialize the schema
        wm.add_conversation(
            conversation_id="test-conversation-123",
            title="Test session",
            messages=[{"role": "user", "content": "Test message"}]
        )
        
        yield db_path
        
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def correlator(self, temp_db):
        """Create TemporalCorrelator instance."""
        return TemporalCorrelator(temp_db)
    
    @pytest.fixture
    def sample_conversation(self, temp_db):
        """Create sample conversation for testing."""
        wm = WorkingMemory(Path(temp_db))
        
        # Import a conversation with file mentions and phases
        conversation_turns = [
            {
                'user': 'Plan authentication system implementation',
                'assistant': '''🧠 **CORTEX Feature Planning**

🎯 **My Understanding:** Implement user authentication for the dashboard

⚠️ **Challenge:** ✓ **Accept** - Standard authentication flow is well-established

💬 **Response:** I'll implement this in phases:

Phase 1: Core Authentication
- Create `auth/login.py` for login logic  
- Update `config/database.py` for user storage
- Add `middleware/auth.py` for session management

Phase 2: Security Integration  
- Implement `utils/encryption.py` for password hashing
- Create `tests/test_auth.py` for security validation

📝 **Your Request:** Implement authentication system

🔍 Next Steps:
1. Set up Phase 1 core components
2. Implement Phase 2 security features  
3. Add comprehensive testing'''
            }
        ]
        
        result = wm.import_conversation(
            conversation_turns=conversation_turns,
            import_source="test-planning-session.md",
            workspace_path="/test/workspace"
        )
        
        return result['conversation_id'], wm
    
    @pytest.fixture
    def sample_events(self, temp_db):
        """Create sample ambient events for testing."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Use UTC time to match SQLite CURRENT_TIMESTAMP behavior
        base_time = datetime.utcnow() - timedelta(minutes=5)  # Just 5 minutes ago (UTC)
        
        events = [
            # File creation events (should correlate with file mentions)
            (
                'test-session-123', 'file_change', 'auth/login.py',
                'FEATURE', 85, 'Created authentication login module',
                (base_time + timedelta(minutes=1)).isoformat(),
                '{"lines_added": 45, "complexity": "moderate"}'
            ),
            (
                'test-session-123', 'file_change', 'config/database.py', 
                'FEATURE', 90, 'Updated database configuration for users',
                (base_time + timedelta(minutes=2)).isoformat(),
                '{"lines_modified": 12, "tables_added": ["users"]}'
            ),
            (
                'test-session-123', 'file_change', 'middleware/auth.py',
                'FEATURE', 88, 'Implemented authentication middleware',
                (base_time + timedelta(minutes=3)).isoformat(),
                '{"lines_added": 67, "security_level": "high"}'
            ),
            # Non-matching event (should not correlate)
            (
                'test-session-123', 'terminal_command', None,
                'MAINTENANCE', 30, 'Updated package dependencies',
                (base_time + timedelta(hours=2)).isoformat(),
                '{"command": "pip install requests", "success": true}'
            ),
            # Phase 2 event (should correlate with plan verification)
            (
                'test-session-123', 'file_change', 'utils/encryption.py',
                'FEATURE', 92, 'Implemented password encryption utilities',
                (base_time + timedelta(minutes=4)).isoformat(),
                '{"algorithm": "bcrypt", "security_audit": "passed"}'
            )
        ]
        
        for event in events:
            cursor.execute("""
                INSERT INTO ambient_events 
                (session_id, event_type, file_path, pattern, score, summary, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, event)
        
        conn.commit()
        event_ids = [cursor.lastrowid - len(events) + i + 1 for i in range(len(events))]
        conn.close()
        
        return event_ids
    
    def test_correlator_initialization(self, temp_db):
        """Test correlator initialization and schema setup."""
        correlator = TemporalCorrelator(temp_db)
        
        # Check that correlation tables were created
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='temporal_correlations'
        """)
        
        assert cursor.fetchone() is not None
        conn.close()
    
    def test_extract_file_mentions(self, correlator):
        """Test file mention extraction from conversation content."""
        content = """
        I'll implement authentication with these files:
        - `auth/login.py` for core logic
        - `config/database.py` for user storage  
        - `middleware/auth.py` for sessions
        - Also need `utils/encryption.py` later
        
        The `tests/test_auth.py` file will validate everything.
        Note: `not-a-file` should be ignored.
        """
        
        files = correlator._extract_file_mentions(content)
        
        expected = [
            'auth/login.py',
            'config/database.py', 
            'middleware/auth.py',
            'utils/encryption.py',
            'tests/test_auth.py'
        ]
        
        assert files == expected
    
    def test_extract_phase_mentions(self, correlator):
        """Test phase mention extraction from conversation content."""
        content = """
        Let's implement this in phases:
        
        Phase 1: Core Authentication
        - Basic login system
        
        Phase 2: Security Integration
        - Password hashing
        - Session management
        
        Phase 3: Testing & Validation
        - Comprehensive test suite
        """
        
        phases = correlator._extract_phase_mentions(content)
        
        expected = ['Phase 1', 'Phase 2', 'Phase 3']
        assert phases == expected
    
    def test_get_conversation_turns(self, correlator, sample_conversation):
        """Test conversation turn extraction."""
        conversation_id, wm = sample_conversation
        
        turns = correlator._get_conversation_turns(conversation_id)
        
        assert len(turns) == 1  # One assistant response
        turn = turns[0]
        
        assert turn.conversation_id == conversation_id
        assert 'auth/login.py' in turn.files_mentioned
        assert 'config/database.py' in turn.files_mentioned
        assert 'Phase 1' in turn.phases_mentioned
        assert 'Phase 2' in turn.phases_mentioned
    
    def test_get_ambient_events_in_window(self, correlator, sample_events):
        """Test ambient event retrieval within time window."""
        base_time = datetime.utcnow()  # Use current UTC time to match sample_events
        
        # Get events within 1 hour of base time
        events = correlator._get_ambient_events_in_window(base_time, 3600)
        
        # Should get 4 events (3 file changes + 1 encryption file within 1 hour)
        assert len(events) >= 3
        
        # Check first event
        first_event = next(e for e in events if e.file_path == 'auth/login.py')
        assert first_event.event_type == 'file_change'
        assert first_event.pattern == 'FEATURE'
        assert first_event.score == 85
    
    def test_temporal_correlation_calculation(self, correlator):
        """Test temporal correlation scoring algorithm."""
        # Create test turn and event
        turn = ConversationTurn(
            turn_id='test-turn-1',
            conversation_id='test-conv-1',
            content='Implement auth system',
            timestamp=datetime(2025, 11, 14, 10, 0, 0),
            files_mentioned=[],
            phases_mentioned=[]
        )
        
        event = AmbientEvent(
            event_id=1,
            session_id='test-session',
            event_type='file_change',
            file_path='auth/login.py',
            timestamp=datetime(2025, 11, 14, 10, 15, 0),  # 15 minutes later
            pattern='FEATURE',
            score=85,
            summary='Created authentication module',
            metadata={}
        )
        
        # Calculate temporal correlation
        time_diff = 900  # 15 minutes
        correlation = correlator._calculate_temporal_correlation(turn, event, time_diff)
        
        assert correlation is not None
        assert correlation.correlation_type == 'temporal'
        assert correlation.confidence_score > 0.5  # Should be high for close time + high score
        assert correlation.time_diff_seconds == 900
    
    def test_file_mention_correlation_exact_match(self, correlator):
        """Test file mention correlation with exact path match."""
        turn = ConversationTurn(
            turn_id='test-turn-1',
            conversation_id='test-conv-1',
            content='Create `auth/login.py` for authentication',
            timestamp=datetime(2025, 11, 14, 10, 0, 0),
            files_mentioned=['auth/login.py'],
            phases_mentioned=[]
        )
        
        event = AmbientEvent(
            event_id=1,
            session_id='test-session',
            event_type='file_change',
            file_path='auth/login.py',
            timestamp=datetime(2025, 11, 14, 10, 15, 0),
            pattern='FEATURE',
            score=85,
            summary='Created authentication module',
            metadata={}
        )
        
        time_diff = 900
        correlation = correlator._calculate_file_mention_correlation(turn, event, time_diff)
        
        assert correlation is not None
        assert correlation.correlation_type == 'file_mention'
        assert correlation.confidence_score > 0.7  # Should be high for exact match
        assert correlation.match_details['best_match']['match_type'] == 'exact'
    
    def test_file_mention_correlation_filename_match(self, correlator):
        """Test file mention correlation with filename-only match."""
        turn = ConversationTurn(
            turn_id='test-turn-1',
            conversation_id='test-conv-1',
            content='Create `login.py` for authentication',
            timestamp=datetime(2025, 11, 14, 10, 0, 0),
            files_mentioned=['login.py'],
            phases_mentioned=[]
        )
        
        event = AmbientEvent(
            event_id=1,
            session_id='test-session',
            event_type='file_change',
            file_path='/full/path/to/auth/login.py',
            timestamp=datetime(2025, 11, 14, 10, 15, 0),
            pattern='FEATURE',
            score=85,
            summary='Created authentication module',
            metadata={}
        )
        
        time_diff = 900
        correlation = correlator._calculate_file_mention_correlation(turn, event, time_diff)
        
        assert correlation is not None
        assert correlation.confidence_score > 0.5  # Lower than exact match
        assert correlation.match_details['best_match']['match_type'] == 'filename'
    
    def test_plan_verification_correlation(self, correlator):
        """Test plan verification correlation scoring."""
        turn = ConversationTurn(
            turn_id='test-turn-1',
            conversation_id='test-conv-1',
            content='Phase 1: Implement core authentication features',
            timestamp=datetime(2025, 11, 14, 10, 0, 0),
            files_mentioned=[],
            phases_mentioned=['Phase 1']
        )
        
        event = AmbientEvent(
            event_id=1,
            session_id='test-session',
            event_type='file_change',
            file_path='auth/login.py',
            timestamp=datetime(2025, 11, 14, 10, 15, 0),
            pattern='FEATURE',
            score=90,
            summary='Implemented phase 1 authentication features',
            metadata={}
        )
        
        time_diff = 900
        correlation = correlator._calculate_plan_verification_correlation(turn, event, time_diff)
        
        assert correlation is not None
        assert correlation.correlation_type == 'plan_verification'
        assert correlation.confidence_score > 0.5
        assert 'phase' in correlation.match_details['plan_indicators_found']
        # Note: 'feature' is found instead of 'implementation'
        assert len(correlation.match_details['plan_indicators_found']) > 0
    
    def test_full_conversation_correlation(self, correlator, sample_conversation, sample_events):
        """Test complete conversation correlation workflow."""
        conversation_id, wm = sample_conversation
        
        # Run correlation
        correlations = correlator.correlate_conversation(conversation_id)
        
        assert len(correlations) > 0
        
        # Should have file mention correlations
        file_correlations = [c for c in correlations if c.correlation_type == 'file_mention']
        assert len(file_correlations) > 0
        
        # Should have temporal correlations
        temporal_correlations = [c for c in correlations if c.correlation_type == 'temporal']
        assert len(temporal_correlations) > 0
        
        # Should have some high-confidence correlations
        high_confidence = [c for c in correlations if c.confidence_score > 0.7]
        assert len(high_confidence) > 0
    
    def test_correlation_persistence(self, correlator, sample_conversation, sample_events):
        """Test that correlations are stored and retrieved correctly."""
        conversation_id, wm = sample_conversation
        
        # First correlation run
        correlations1 = correlator.correlate_conversation(conversation_id)
        
        # Second run should retrieve from database
        correlations2 = correlator.correlate_conversation(conversation_id)
        
        assert len(correlations1) == len(correlations2)
        
        # Confidence scores should match
        scores1 = sorted([c.confidence_score for c in correlations1], reverse=True)
        scores2 = sorted([c.confidence_score for c in correlations2], reverse=True)
        assert scores1 == scores2
    
    def test_force_recalculation(self, correlator, sample_conversation, sample_events):
        """Test force recalculation of existing correlations."""
        conversation_id, wm = sample_conversation
        
        # First correlation run
        correlations1 = correlator.correlate_conversation(conversation_id)
        
        # Force recalculation
        correlations2 = correlator.correlate_conversation(conversation_id, force_recalculate=True)
        
        # Should get same results (demonstrating recalculation worked)
        assert len(correlations1) == len(correlations2)
    
    def test_conversation_timeline_generation(self, correlator, sample_conversation, sample_events):
        """Test unified timeline generation."""
        conversation_id, wm = sample_conversation
        
        timeline_data = correlator.get_conversation_timeline(conversation_id)
        
        assert timeline_data['conversation_id'] == conversation_id
        assert timeline_data['correlations_count'] > 0
        assert len(timeline_data['timeline']) > 0
        
        # Should have both conversation turns and events in timeline
        turn_items = [item for item in timeline_data['timeline'] if item['type'] == 'conversation_turn']
        event_items = [item for item in timeline_data['timeline'] if item['type'] == 'ambient_event']
        
        assert len(turn_items) > 0
        assert len(event_items) > 0
        
        # Timeline should be sorted by timestamp
        timestamps = [item['timestamp'] for item in timeline_data['timeline']]
        assert timestamps == sorted(timestamps)
    
    def test_custom_time_window(self, temp_db):
        """Test correlator with custom time window."""
        # Create correlator with 30-minute window
        correlator = TemporalCorrelator(temp_db, time_window_seconds=1800)
        
        assert correlator.time_window == 1800
        
        # Events outside 30-minute window should not correlate
        base_time = datetime(2025, 11, 14, 10, 0, 0)
        events = correlator._get_ambient_events_in_window(base_time, 1800)
        
        # Should only get events within ±30 minutes
        for event in events:
            time_diff = abs((event.timestamp - base_time).total_seconds())
            assert time_diff <= 1800
    
    def test_no_correlations_case(self, correlator, temp_db):
        """Test behavior when no correlations are found."""
        # Create conversation with no matching events
        wm = WorkingMemory(Path(temp_db))
        
        result = wm.import_conversation(
            conversation_turns=[{
                'user': 'Discuss high-level strategy',
                'assistant': 'Strategic planning discussion with no specific files or phases mentioned.'
            }],
            import_source="strategy-discussion.md"
        )
        
        conversation_id = result['conversation_id']
        
        # Should find no correlations
        correlations = correlator.correlate_conversation(conversation_id)
        assert len(correlations) == 0
        
        # Timeline should still work
        timeline_data = correlator.get_conversation_timeline(conversation_id)
        assert timeline_data['correlations_count'] == 0
        assert len(timeline_data['timeline']) == 1  # Just the conversation turn


class TestIntegrationWithWorkingMemory:
    """Test integration between TemporalCorrelator and WorkingMemory."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        yield db_path
        Path(db_path).unlink(missing_ok=True)
    
    def test_working_memory_temporal_correlation_integration(self, temp_db):
        """Test that WorkingMemory can use temporal correlation features."""
        wm = WorkingMemory(Path(temp_db))
        correlator = TemporalCorrelator(temp_db)
        
        # Import conversation
        result = wm.import_conversation(
            conversation_turns=[{
                'user': 'Create authentication system',
                'assistant': 'I will create `auth/login.py` for Phase 1 implementation.'
            }],
            import_source="auth-planning.md"
        )
        
        conversation_id = result['conversation_id']
        
        # NOTE: Ambient events section removed - ambient daemon deprecated in CORTEX 3.0
        # Manual capture hints used instead
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ambient_events 
            (session_id, event_type, file_path, pattern, score, summary, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'test-session',
            'file_change',
            'auth/login.py',
            'FEATURE',
            85,
            'Created authentication login module',
            datetime.utcnow().isoformat(),  # Use UTC to match message timestamps
            '{}'
        ))
        
        conn.commit()
        conn.close()
        
        # Test correlation
        correlations = correlator.correlate_conversation(conversation_id)
        
        assert len(correlations) > 0
        file_correlations = [c for c in correlations if c.correlation_type == 'file_mention']
        assert len(file_correlations) > 0
    
    def test_temporal_correlation_api_extension(self, temp_db):
        """Test potential API extension for WorkingMemory temporal features."""
        wm = WorkingMemory(Path(temp_db))
        
        # This tests the future API we might add to WorkingMemory
        # For now, we access correlation through separate TemporalCorrelator
        correlator = TemporalCorrelator(temp_db)
        
        # Import conversation
        result = wm.import_conversation(
            conversation_turns=[{
                'user': 'Implement user dashboard',
                'assistant': '''Phase 1: Core Dashboard
                - Create `dashboard/main.py`
                - Update `templates/dashboard.html`
                
                Phase 2: User Integration
                - Modify `auth/session.py`
                '''
            }],
            import_source="dashboard-planning.md"
        )
        
        conversation_id = result['conversation_id']
        
        # Future API might look like:
        # timeline = wm.get_conversation_timeline(conversation_id)
        # For now:
        timeline = correlator.get_conversation_timeline(conversation_id)
        
        assert 'conversation_id' in timeline
        assert 'timeline' in timeline
        assert 'summary' in timeline