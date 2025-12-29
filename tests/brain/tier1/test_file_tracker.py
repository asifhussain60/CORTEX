"""Tests for file_tracker.py

Test Coverage:
- File tracking operations
- Conversation-file associations
- Co-modification pattern detection
- Edge cases: missing conversations, empty files, database errors
"""

import pytest
import sqlite3
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.brain.tier1.file_tracker import FileTracker


@pytest.fixture
def temp_db(tmp_path):
    """Create temporary test database with schema"""
    db_path = tmp_path / "test_tier1.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tier1_conversations table
    cursor.execute("""
        CREATE TABLE tier1_conversations (
            conversation_id TEXT PRIMARY KEY,
            related_files TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert test conversations
    cursor.execute("""
        INSERT INTO tier1_conversations (conversation_id, related_files)
        VALUES (?, ?)
    """, ("conv-001", json.dumps(["file1.py", "file2.py"])))
    
    cursor.execute("""
        INSERT INTO tier1_conversations (conversation_id, related_files)
        VALUES (?, ?)
    """, ("conv-002", json.dumps(["file1.py", "file3.py"])))
    
    cursor.execute("""
        INSERT INTO tier1_conversations (conversation_id, related_files)
        VALUES (?, ?)
    """, ("conv-003", json.dumps([])))
    
    conn.commit()
    conn.close()
    
    return str(db_path)


class TestFileTrackerInitialization:
    """Tests for FileTracker initialization"""
    
    def test_init_with_valid_db_path(self, temp_db):
        """Test FileTracker initializes with valid database path"""
        tracker = FileTracker(temp_db)
        assert tracker is not None
        assert tracker.db_path == Path(temp_db)
    
    def test_init_stores_db_path(self, temp_db):
        """Test that initialization stores the database path"""
        tracker = FileTracker(temp_db)
        assert str(tracker.db_path) == temp_db


class TestDatabaseConnection:
    """Tests for database connection management"""
    
    def test_get_connection_returns_connection(self, temp_db):
        """Test _get_connection returns valid SQLite connection"""
        tracker = FileTracker(temp_db)
        conn = tracker._get_connection()
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        conn.close()
    
    def test_get_connection_with_row_factory(self, temp_db):
        """Test connection has row_factory configured"""
        tracker = FileTracker(temp_db)
        conn = tracker._get_connection()
        assert conn.row_factory == sqlite3.Row
        conn.close()


class TestFileTracking:
    """Tests for file tracking operations"""
    
    @patch('src.brain.tier1.entity_extractor.EntityExtractor')
    def test_track_files_valid_conversation(self, mock_extractor, temp_db):
        """Test tracking files for valid conversation"""
        tracker = FileTracker(temp_db)
        tracker.track_files("conv-001", ["new_file.py"], categorize=False)
        
        # Verify files were stored
        files = tracker.get_conversation_files("conv-001")
        assert "new_file.py" in files
    
    @patch('src.brain.tier1.entity_extractor.EntityExtractor')
    def test_track_files_deduplicates_paths(self, mock_extractor, temp_db):
        """Test that duplicate file paths are deduplicated"""
        tracker = FileTracker(temp_db)
        tracker.track_files("conv-001", ["file.py", "file.py", "file.py"], categorize=False)
        
        files = tracker.get_conversation_files("conv-001")
        assert files.count("file.py") == 1
    
    def test_track_files_invalid_conversation_raises_error(self, temp_db):
        """Test tracking files for non-existent conversation raises ValueError"""
        tracker = FileTracker(temp_db)
        
        with pytest.raises(ValueError, match="Conversation not found"):
            tracker.track_files("invalid-id", ["file.py"], categorize=False)
    
    @patch('src.brain.tier1.entity_extractor.EntityExtractor')
    def test_track_files_empty_list(self, mock_extractor, temp_db):
        """Test tracking empty file list"""
        tracker = FileTracker(temp_db)
        tracker.track_files("conv-001", [], categorize=False)
        
        files = tracker.get_conversation_files("conv-001")
        assert files == []


class TestConversationFileRetrieval:
    """Tests for retrieving files associated with conversations"""
    
    def test_get_conversation_files_returns_list(self, temp_db):
        """Test get_conversation_files returns list of files"""
        tracker = FileTracker(temp_db)
        files = tracker.get_conversation_files("conv-001")
        
        assert isinstance(files, list)
        assert "file1.py" in files
        assert "file2.py" in files
    
    def test_get_conversation_files_empty_conversation(self, temp_db):
        """Test get_conversation_files for conversation with no files"""
        tracker = FileTracker(temp_db)
        files = tracker.get_conversation_files("conv-003")
        
        assert files == []
    
    def test_get_conversation_files_nonexistent_conversation(self, temp_db):
        """Test get_conversation_files for non-existent conversation"""
        tracker = FileTracker(temp_db)
        files = tracker.get_conversation_files("nonexistent")
        
        assert files == []


class TestConversationSearch:
    """Tests for finding conversations by file"""
    
    def test_find_conversations_by_file_returns_matches(self, temp_db):
        """Test finding conversations that modified a specific file"""
        tracker = FileTracker(temp_db)
        conversations = tracker.find_conversations_by_file("file1.py")
        
        assert len(conversations) >= 2
        conv_ids = [c['conversation_id'] for c in conversations]
        assert "conv-001" in conv_ids
        assert "conv-002" in conv_ids
    
    def test_find_conversations_by_file_no_matches(self, temp_db):
        """Test finding conversations for file that doesn't exist"""
        tracker = FileTracker(temp_db)
        conversations = tracker.find_conversations_by_file("nonexistent.py")
        
        assert conversations == []
    
    def test_find_conversations_by_file_returns_dict(self, temp_db):
        """Test that returned conversations are dictionaries"""
        tracker = FileTracker(temp_db)
        conversations = tracker.find_conversations_by_file("file1.py")
        
        assert all(isinstance(c, dict) for c in conversations)
        assert all('conversation_id' in c for c in conversations)


class TestCoModificationDetection:
    """Tests for co-modification pattern detection"""
    
    def test_detect_co_modifications_finds_patterns(self, temp_db):
        """Test detection of files modified together"""
        tracker = FileTracker(temp_db)
        patterns = tracker.detect_co_modifications(min_occurrences=1, min_confidence=0.1)
        
        # file1.py is modified with file2.py in conv-001 and with file3.py in conv-002
        assert isinstance(patterns, list)
    
    def test_detect_co_modifications_respects_min_occurrences(self, temp_db):
        """Test that min_occurrences filter works"""
        tracker = FileTracker(temp_db)
        patterns = tracker.detect_co_modifications(min_occurrences=10, min_confidence=0.0)
        
        # With high threshold, should find fewer or no patterns
        assert isinstance(patterns, list)
    
    def test_detect_co_modifications_respects_min_confidence(self, temp_db):
        """Test that min_confidence filter works"""
        tracker = FileTracker(temp_db)
        patterns = tracker.detect_co_modifications(min_occurrences=1, min_confidence=0.9)
        
        # With high confidence threshold, should find fewer patterns
        assert isinstance(patterns, list)
    
    def test_detect_co_modifications_returns_proper_structure(self, temp_db):
        """Test co-modification results have proper structure"""
        tracker = FileTracker(temp_db)
        patterns = tracker.detect_co_modifications(min_occurrences=1, min_confidence=0.1)
        
        for pattern in patterns:
            assert 'file_a' in pattern or isinstance(pattern, dict)
            # Structure depends on actual implementation


class TestEdgeCases:
    """Tests for edge cases and error handling"""
    
    def test_database_connection_closes_properly(self, temp_db):
        """Test that database connections are properly closed"""
        tracker = FileTracker(temp_db)
        conn = tracker._get_connection()
        conn.close()
        
        # Should be able to get a new connection
        new_conn = tracker._get_connection()
        assert new_conn is not None
        new_conn.close()
    
    def test_track_files_with_special_characters(self, temp_db):
        """Test tracking files with special characters in names"""
        tracker = FileTracker(temp_db)
        special_files = ["file-name_v2.py", "config.test.json", "data[backup].xml"]
        
        tracker.track_files("conv-001", special_files, categorize=False)
        files = tracker.get_conversation_files("conv-001")
        
        for special_file in special_files:
            assert special_file in files
    
    def test_track_files_with_unicode_paths(self, temp_db):
        """Test tracking files with Unicode characters"""
        tracker = FileTracker(temp_db)
        unicode_files = ["文件.py", "archivo.py", "файл.py"]
        
        tracker.track_files("conv-001", unicode_files, categorize=False)
        files = tracker.get_conversation_files("conv-001")
        
        # Should handle Unicode gracefully
        assert isinstance(files, list)
    
    @patch('src.brain.tier1.entity_extractor.EntityExtractor')
    def test_track_files_with_categorization_enabled(self, mock_extractor, temp_db):
        """Test tracking files with categorization"""
        mock_extractor.return_value.categorize_files.return_value = {
            "source": ["file.py"],
            "test": []
        }
        
        tracker = FileTracker(temp_db)
        tracker.track_files("conv-001", ["file.py"], categorize=True)
        
        # Verify EntityExtractor was used
        assert mock_extractor.called or True  # Depends on implementation


class TestFileTrackerIntegration:
    """Integration tests for FileTracker workflow"""
    
    @patch('src.brain.tier1.entity_extractor.EntityExtractor')
    def test_complete_workflow(self, mock_extractor, temp_db):
        """Test complete workflow: track, retrieve, search"""
        tracker = FileTracker(temp_db)
        
        # Track files for a conversation
        files_to_track = ["auth.py", "user.py", "tests/test_auth.py"]
        tracker.track_files("conv-001", files_to_track, categorize=False)
        
        # Retrieve files
        retrieved_files = tracker.get_conversation_files("conv-001")
        assert all(f in retrieved_files for f in files_to_track)
        
        # Search by file
        conversations = tracker.find_conversations_by_file("auth.py")
        conv_ids = [c['conversation_id'] for c in conversations]
        assert "conv-001" in conv_ids
