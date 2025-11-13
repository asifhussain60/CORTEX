"""
Tests for CORTEX 3.0 Conversation Import Feature

Tests the dual-channel memory system's manual conversation import capability.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from src.tier1.working_memory import WorkingMemory


class TestConversationImport:
    """Test conversation import functionality."""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create temporary database for testing."""
        db_path = tmp_path / "test_import.db"
        wm = WorkingMemory(db_path)
        yield wm
        # Cleanup handled by tmp_path
    
    def test_import_basic_conversation(self, temp_db):
        """Should import a basic conversation successfully."""
        conversation_turns = [
            {
                'user': 'How do I add authentication to the dashboard?',
                'assistant': 'I\'ll help you implement authentication using the existing user service.'
            },
            {
                'user': 'What about session management?',
                'assistant': 'We\'ll use JWT tokens for session management.'
            }
        ]
        
        result = temp_db.import_conversation(
            conversation_turns=conversation_turns,
            import_source="CopilotChats-2025-11-13.md",
            workspace_path="/projects/myapp"
        )
        
        assert result['conversation_id'] is not None
        assert result['session_id'] is not None
        assert result['turns_imported'] == 2
        assert result['quality_score'] >= 0
        assert result['quality_level'] in ['EXCELLENT', 'GOOD', 'FAIR', 'LOW']
    
    def test_import_high_quality_conversation(self, temp_db):
        """Should recognize high-quality strategic conversation."""
        conversation_turns = [
            {
                'user': 'Let\'s plan the authentication system',
                'assistant': '''
                🧠 CORTEX Feature Planning
                
                🎯 My Understanding: You want to design an authentication system
                
                ⚠️ Challenge: ✓ Accept - Good approach for security
                
                💬 Response: I recommend a multi-phase implementation:
                
                Phase 1: Core Authentication (login UI, JWT tokens)
                Phase 2: Route Protection (guards, middleware)
                Phase 3: Testing & Validation (unit tests, security audit)
                
                This design provides strong security with incremental delivery.
                
                📝 Your Request: Plan authentication system
                
                🔍 Next Steps:
                   1. Implement Phase 1 components
                   2. Add route guards in Phase 2
                   3. Comprehensive testing in Phase 3
                '''
            }
        ]
        
        result = temp_db.import_conversation(
            conversation_turns=conversation_turns,
            import_source="CopilotChats-planning-2025-11-13.md",
            workspace_path="/projects/myapp"
        )
        
        assert result['quality_level'] in ['EXCELLENT', 'GOOD']
        assert result['quality_score'] >= 6  # GOOD threshold
        assert result['semantic_elements']['multi_phase_planning'] == True
        assert result['semantic_elements']['phase_count'] >= 3
        assert result['semantic_elements']['challenge_accept_flow'] == True
        assert result['semantic_elements']['next_steps_provided'] == True
    
    def test_import_stores_quality_metadata(self, temp_db):
        """Should store quality scores in database."""
        conversation_turns = [
            {
                'user': 'Fix the button color',
                'assistant': 'I\'ll change the button to purple: `styles/button.css`'
            }
        ]
        
        result = temp_db.import_conversation(
            conversation_turns=conversation_turns,
            import_source="quick-fix.md"
        )
        
        # Verify database has quality metadata
        conn = sqlite3.connect(temp_db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT conversation_type, import_source, quality_score, semantic_elements
            FROM conversations 
            WHERE conversation_id = ?
        """, (result['conversation_id'],))
        
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row[0] == 'imported'  # conversation_type
        assert row[1] == 'quick-fix.md'  # import_source
        assert row[2] >= 0  # quality_score
        assert row[3] is not None  # semantic_elements (JSON)
        
        # Verify JSON parses
        semantic_elements = json.loads(row[3])
        assert 'multi_phase_planning' in semantic_elements
        assert 'file_references' in semantic_elements
    
    def test_import_without_workspace(self, temp_db):
        """Should import conversation without workspace context."""
        conversation_turns = [
            {
                'user': 'What is CORTEX?',
                'assistant': 'CORTEX is a cognitive framework for AI...'
            }
        ]
        
        result = temp_db.import_conversation(
            conversation_turns=conversation_turns,
            import_source="general-qa.md"
        )
        
        assert result['conversation_id'] is not None
        assert result['session_id'] is None  # No workspace, no session
        assert result['turns_imported'] == 1
    
    def test_import_links_to_existing_session(self, temp_db):
        """Should link imported conversation to existing active session."""
        workspace_path = "/projects/myapp"
        
        # Create an active session using detect_or_create
        session_1 = temp_db.session_manager.detect_or_create_session(workspace_path)
        session_id_1 = session_1.session_id
        
        # Import conversation - should use existing session
        conversation_turns = [
            {
                'user': 'Continue with authentication',
                'assistant': 'I\'ll continue the authentication implementation.'
            }
        ]
        
        result = temp_db.import_conversation(
            conversation_turns=conversation_turns,
            import_source="continue-work.md",
            workspace_path=workspace_path
        )
        
        assert result['session_id'] == session_id_1
    
    def test_import_preserves_message_order(self, temp_db):
        """Should preserve the order of conversation turns."""
        conversation_turns = [
            {'user': 'First question', 'assistant': 'First answer'},
            {'user': 'Second question', 'assistant': 'Second answer'},
            {'user': 'Third question', 'assistant': 'Third answer'}
        ]
        
        result = temp_db.import_conversation(
            conversation_turns=conversation_turns,
            import_source="ordered-conversation.md"
        )
        
        # Retrieve messages
        messages = temp_db.get_messages(result['conversation_id'])
        
        assert len(messages) == 6  # 3 user + 3 assistant
        assert messages[0]['content'] == 'First question'
        assert messages[1]['content'] == 'First answer'
        assert messages[2]['content'] == 'Second question'
        assert messages[3]['content'] == 'Second answer'
    
    def test_import_detects_file_references(self, temp_db):
        """Should detect and count file references in conversations."""
        conversation_turns = [
            {
                'user': 'Update the authentication files',
                'assistant': 'I\'ll update `src/auth/login.py`, `src/auth/session.py`, and `tests/test_auth.py`'
            }
        ]
        
        result = temp_db.import_conversation(
            conversation_turns=conversation_turns,
            import_source="file-refs.md"
        )
        
        assert result['semantic_elements']['file_references'] == 3
    
    def test_import_empty_conversation(self, temp_db):
        """Should handle empty conversation gracefully."""
        result = temp_db.import_conversation(
            conversation_turns=[],
            import_source="empty.md"
        )
        
        assert result['conversation_id'] is not None
        assert result['turns_imported'] == 0
        assert result['quality_score'] == 0


class TestImportedConversationRetrieval:
    """Test retrieving and querying imported conversations."""
    
    @pytest.fixture
    def temp_db_with_imports(self, tmp_path):
        """Create database with pre-imported conversations."""
        db_path = tmp_path / "test_retrieval.db"
        wm = WorkingMemory(db_path)
        
        # Import several conversations
        result_a = wm.import_conversation(
            conversation_turns=[
                {'user': 'Plan feature A', 'assistant': 'Phase 1, Phase 2, Phase 3'}
            ],
            import_source="plan-a.md",
            workspace_path="/project/A"
        )
        
        result_b = wm.import_conversation(
            conversation_turns=[
                {'user': 'Quick fix button', 'assistant': 'Changed color'}
            ],
            import_source="fix-b.md",
            workspace_path="/project/B"
        )
        
        yield wm
    
    def test_retrieve_imported_conversations(self, temp_db_with_imports):
        """Should retrieve all imported conversations."""
        conn = sqlite3.connect(temp_db_with_imports.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT conversation_id, conversation_type, quality_score
            FROM conversations
            WHERE conversation_type = 'imported'
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        assert len(rows) == 2
        assert all(row[1] == 'imported' for row in rows)
    
    def test_filter_by_quality_level(self, temp_db_with_imports):
        """Should filter conversations by quality score."""
        conn = sqlite3.connect(temp_db_with_imports.db_path)
        cursor = conn.cursor()
        
        # Get high-quality conversations (score >= 6)
        cursor.execute("""
            SELECT conversation_id, quality_score
            FROM conversations
            WHERE conversation_type = 'imported' AND quality_score >= 6
        """)
        
        high_quality = cursor.fetchall()
        conn.close()
        
        # At least one should be high quality (the planning one)
        assert len(high_quality) >= 1
        assert all(row[1] >= 6 for row in high_quality)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
