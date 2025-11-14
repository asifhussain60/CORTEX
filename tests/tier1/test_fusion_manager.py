"""
CORTEX 3.0 Milestone 2 - Fusion Manager Tests

Test suite for the FusionManager integration API that provides
high-level fusion operations for dual-channel memory.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import pytest
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from src.tier1.fusion_manager import FusionManager
from src.tier1.working_memory import WorkingMemory


class TestFusionManager:
    """Test the FusionManager integration API."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Initialize working memory to create schema
        wm = WorkingMemory(Path(db_path))
        wm.add_conversation(
            conversation_id="test-conversation-123",
            title="Test session",
            messages=[{"role": "user", "content": "Test message"}]
        )
        
        # Apply conversation import migration
        from src.tier1.migration_add_conversation_import import migrate_add_conversation_import
        migrate_add_conversation_import(db_path)
        
        yield db_path
        
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def fusion_manager(self, temp_db):
        """Create FusionManager instance."""
        return FusionManager(temp_db)
    
    @pytest.fixture
    def sample_conversation_with_events(self, temp_db):
        """Create sample conversation and correlated ambient events."""
        wm = WorkingMemory(Path(temp_db))
        
        # Import conversation with file mentions and phases
        conversation_turns = [
            {
                'user': 'Implement authentication system',
                'assistant': '''🧠 **CORTEX Feature Implementation**

🎯 **My Understanding:** Create secure user authentication

⚠️ **Challenge:** ✓ **Accept** - Standard auth flow

💬 **Response:** I'll implement this in phases:

Phase 1: Core Authentication
- Create `auth/login.py` for login logic
- Update `config/database.py` for user storage

Phase 2: Security Features  
- Implement `utils/encryption.py` for password hashing

📝 **Your Request:** Implement authentication system'''
            }
        ]
        
        result = wm.import_conversation(
            conversation_turns=conversation_turns,
            import_source="auth-implementation.md",
            workspace_path="/test/workspace"
        )
        
        conversation_id = result['conversation_id']
        
        # Add correlated ambient events
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Get the actual message timestamp to correlate properly (TemporalCorrelator uses message timestamps)
        cursor.execute("SELECT timestamp FROM messages WHERE conversation_id = ? ORDER BY id LIMIT 1", (conversation_id,))
        conv_row = cursor.fetchone()
        if conv_row:
            # Use the first message time as base (TemporalCorrelator correlates based on message timestamps)
            from datetime import datetime
            conv_time = datetime.fromisoformat(conv_row[0].replace(' ', 'T'))
        else:
            conv_time = datetime.now()
        
        events = [
            # High confidence file matches - created slightly after conversation
            (
                'test-session', 'file_change', 'auth/login.py',
                'FEATURE', 90, 'Created authentication login module',
                (conv_time + timedelta(minutes=15)).isoformat(),
                '{"lines_added": 67}'
            ),
            (
                'test-session', 'file_change', 'config/database.py',
                'FEATURE', 85, 'Updated database for user storage',
                (conv_time + timedelta(minutes=30)).isoformat(),
                '{"tables_modified": ["users"]}'
            ),
            # Plan verification event
            (
                'test-session', 'file_change', 'utils/encryption.py',
                'FEATURE', 88, 'Implemented phase 2 encryption features',
                (conv_time + timedelta(minutes=45)).isoformat(),
                '{"security_level": "high"}'
            ),
            # Lower relevance event
            (
                'test-session', 'terminal_command', None,
                'MAINTENANCE', 30, 'Updated dependencies',
                (conv_time + timedelta(hours=1, minutes=30)).isoformat(),
                '{"command": "pip install bcrypt"}'
            )
        ]
        
        for event in events:
            cursor.execute("""
                INSERT INTO ambient_events 
                (session_id, event_type, file_path, pattern, score, summary, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, event)
        
        conn.commit()
        conn.close()
        
        return conversation_id, wm
    
    def test_fusion_manager_initialization(self, temp_db):
        """Test FusionManager initialization."""
        fm = FusionManager(temp_db)
        
        assert fm.db_path == temp_db
        assert fm.temporal_correlator is not None
    
    def test_correlate_imported_conversation_success(self, fusion_manager, sample_conversation_with_events):
        """Test successful conversation correlation."""
        conversation_id, wm = sample_conversation_with_events
        
        # Run correlation
        result = fusion_manager.correlate_imported_conversation(conversation_id)
        
        # Check result structure
        assert result['conversation_id'] == conversation_id
        assert result['auto_correlate'] is True
        assert result['correlations'] > 0
        assert result['high_confidence'] >= 0
        assert result['file_matches'] > 0
        assert isinstance(result['summary'], str)
        
        # Should find file correlations
        assert result['file_matches'] >= 2  # auth/login.py and config/database.py
        
        # Should have high confidence correlations
        assert result['high_confidence'] > 0
    
    def test_correlate_imported_conversation_disabled(self, fusion_manager, sample_conversation_with_events):
        """Test correlation with auto_correlate disabled."""
        conversation_id, wm = sample_conversation_with_events
        
        # Disable auto-correlation
        result = fusion_manager.correlate_imported_conversation(conversation_id, auto_correlate=False)
        
        assert result['conversation_id'] == conversation_id
        assert result['auto_correlate'] is False
        assert result['correlations'] == []
        assert 'Auto-correlation disabled' in result['message']
    
    def test_get_conversation_development_story(self, fusion_manager, sample_conversation_with_events):
        """Test development story generation."""
        conversation_id, wm = sample_conversation_with_events
        
        # Generate development story
        story_data = fusion_manager.get_conversation_development_story(conversation_id)
        
        assert story_data['conversation_id'] == conversation_id
        assert isinstance(story_data['story'], str)
        assert len(story_data['timeline']) > 0
        assert story_data['correlations_count'] >= 0
        
        # Story should contain key sections
        story = story_data['story']
        assert '# Development Story:' in story
        assert 'Strategic Planning' in story or 'Implementation Activity' in story
    
    def test_get_fusion_insights_with_correlations(self, fusion_manager, sample_conversation_with_events):
        """Test fusion insights generation with good correlations."""
        conversation_id, wm = sample_conversation_with_events
        
        # Generate insights
        insights_data = fusion_manager.get_fusion_insights(conversation_id)
        
        assert insights_data['conversation_id'] == conversation_id
        assert len(insights_data['insights']) > 0
        assert len(insights_data['recommendations']) >= 0
        assert insights_data['execution_score'] >= 0
        assert insights_data['planning_effectiveness'] in ['Poor', 'Fair', 'Good', 'Excellent']
        assert insights_data['total_correlations'] > 0
        
        # Should have correlation type breakdown
        assert 'file_mention' in insights_data['correlation_types']
        assert 'plan_verification' in insights_data['correlation_types']
        assert 'temporal' in insights_data['correlation_types']
    
    def test_get_fusion_insights_no_recommendations(self, fusion_manager, sample_conversation_with_events):
        """Test fusion insights without recommendations."""
        conversation_id, wm = sample_conversation_with_events
        
        # Generate insights without recommendations
        insights_data = fusion_manager.get_fusion_insights(conversation_id, include_recommendations=False)
        
        assert insights_data['conversation_id'] == conversation_id
        assert len(insights_data['insights']) > 0
        assert insights_data['recommendations'] == []
    
    def test_empty_conversation_correlation(self, fusion_manager, temp_db):
        """Test correlation with conversation that has no correlations."""
        # Create conversation with no matching events
        wm = WorkingMemory(Path(temp_db))
        
        result = wm.import_conversation(
            conversation_turns=[{
                'user': 'Discuss strategy',
                'assistant': 'High-level strategic discussion with no specific implementation details.'
            }],
            import_source="strategy-only.md"
        )
        
        conversation_id = result['conversation_id']
        
        # Test correlation
        correlation_result = fusion_manager.correlate_imported_conversation(conversation_id)
        
        assert correlation_result['conversation_id'] == conversation_id
        assert correlation_result['correlations'] == 0
        assert correlation_result['high_confidence'] == 0
        assert correlation_result['file_matches'] == 0
    
    def test_empty_conversation_story(self, fusion_manager, temp_db):
        """Test story generation for conversation with no events."""
        # Create conversation with no matching events
        wm = WorkingMemory(Path(temp_db))
        
        result = wm.import_conversation(
            conversation_turns=[{
                'user': 'General discussion',
                'assistant': 'Generic conversation with no specific files or plans.'
            }],
            import_source="general.md"
        )
        
        conversation_id = result['conversation_id']
        
        # Test story generation
        story_data = fusion_manager.get_conversation_development_story(conversation_id)
        
        assert story_data['conversation_id'] == conversation_id
        assert len(story_data['timeline']) >= 1  # At least the conversation turn
        assert story_data['correlations_count'] == 0
    
    def test_empty_conversation_insights(self, fusion_manager, temp_db):
        """Test insights for conversation with no correlations."""
        # Create conversation with no matching events
        wm = WorkingMemory(Path(temp_db))
        
        result = wm.import_conversation(
            conversation_turns=[{
                'user': 'Abstract discussion',
                'assistant': 'Pure strategic discussion with no implementation aspects.'
            }],
            import_source="abstract.md"
        )
        
        conversation_id = result['conversation_id']
        
        # Test insights generation
        insights_data = fusion_manager.get_fusion_insights(conversation_id)
        
        assert insights_data['conversation_id'] == conversation_id
        assert len(insights_data['insights']) > 0
        assert 'No correlations found' in insights_data['insights'][0]
        assert insights_data['execution_score'] == 0
        assert insights_data['planning_effectiveness'] == 'Unknown'
    
    def test_correlation_statistics_calculation(self, fusion_manager):
        """Test internal correlation statistics calculation."""
        from src.tier1.temporal_correlator import CorrelationResult
        
        # Create mock correlations
        correlations = [
            CorrelationResult(
                conversation_id='test',
                event_id=1,
                correlation_type='file_mention',
                confidence_score=0.9,
                time_diff_seconds=900,
                match_details={}
            ),
            CorrelationResult(
                conversation_id='test',
                event_id=2,
                correlation_type='temporal',
                confidence_score=0.6,
                time_diff_seconds=1800,
                match_details={}
            ),
            CorrelationResult(
                conversation_id='test',
                event_id=3,
                correlation_type='plan_verification',
                confidence_score=0.8,
                time_diff_seconds=600,
                match_details={}
            )
        ]
        
        stats = fusion_manager._calculate_correlation_stats(correlations)
        
        assert stats['high_confidence_count'] == 2  # 0.9 and 0.8
        assert stats['file_match_count'] == 1
        assert stats['plan_verification_count'] == 1
        assert stats['temporal_count'] == 1
        assert stats['confidence_distribution']['excellent'] == 1  # 0.9
        assert stats['confidence_distribution']['high'] == 1  # 0.8
        assert stats['confidence_distribution']['medium'] == 1  # 0.6
    
    def test_correlation_summary_generation(self, fusion_manager):
        """Test correlation summary text generation."""
        from src.tier1.temporal_correlator import CorrelationResult
        
        correlations = [
            CorrelationResult('test', 1, 'file_mention', 0.9, 900, {}),
            CorrelationResult('test', 2, 'temporal', 0.8, 1800, {}),
        ]
        
        stats = fusion_manager._calculate_correlation_stats(correlations)
        summary = fusion_manager._generate_correlation_summary('test-conv', correlations, stats)
        
        assert 'Found 2 correlations' in summary
        assert '2 high-confidence' in summary
        assert '1 file mentions verified' in summary
        assert 'Strong correlation quality' in summary


class TestFusionManagerIntegration:
    """Test FusionManager integration with WorkingMemory."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Initialize working memory to create schema
        wm = WorkingMemory(Path(db_path))
        
        # Apply conversation import migration
        from src.tier1.migration_add_conversation_import import migrate_add_conversation_import
        migrate_add_conversation_import(db_path)
        
        yield db_path
        Path(db_path).unlink(missing_ok=True)
    
    def test_end_to_end_fusion_workflow(self, temp_db):
        """Test complete fusion workflow from import to insights."""
        wm = WorkingMemory(Path(temp_db))
        fm = FusionManager(temp_db)
        
        # 1. Import conversation
        result = wm.import_conversation(
            conversation_turns=[{
                'user': 'Create user dashboard',
                'assistant': '''Phase 1: Dashboard Core
                - Create `dashboard/main.py`
                - Update `templates/dashboard.html`
                Phase 2: User Integration
                - Modify `auth/user.py`'''
            }],
            import_source="dashboard-planning.md"
        )
        
        conversation_id = result['conversation_id']
        
        # 2. Add ambient events
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ambient_events 
            (session_id, event_type, file_path, pattern, score, summary, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'dashboard-session',
            'file_change',
            'dashboard/main.py',
            'FEATURE',
            85,
            'Implemented dashboard core functionality',
            datetime.now().isoformat(),
            '{}'
        ))
        
        conn.commit()
        conn.close()
        
        # 3. Run correlation
        correlation_result = fm.correlate_imported_conversation(conversation_id)
        
        assert correlation_result['correlations'] > 0
        assert correlation_result['file_matches'] > 0
        
        # 4. Generate story
        story = fm.get_conversation_development_story(conversation_id)
        
        assert len(story['timeline']) > 0
        assert 'Development Story:' in story['story']
        
        # 5. Get insights
        insights = fm.get_fusion_insights(conversation_id)
        
        assert insights['total_correlations'] > 0
        assert len(insights['insights']) > 0