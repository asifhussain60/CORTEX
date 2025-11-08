"""
Unit tests for ConversationSearch module.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from src.tier1.conversations import ConversationManager, ConversationSearch


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def manager(temp_db):
    """Create a ConversationManager for setup."""
    return ConversationManager(temp_db)


@pytest.fixture
def search(temp_db):
    """Create a ConversationSearch instance."""
    return ConversationSearch(temp_db)


class TestSearchByKeyword:
    """Tests for keyword search."""
    
    def test_search_finds_title_match(self, manager, search):
        """Test searching by title."""
        manager.add_conversation("conv-1", "Python Tutorial")
        manager.add_conversation("conv-2", "JavaScript Guide")
        
        results = search.search_by_keyword("Python")
        assert len(results) == 1
        assert results[0].conversation_id == "conv-1"
    
    def test_search_case_insensitive(self, manager, search):
        """Test that search is case-insensitive."""
        manager.add_conversation("conv-1", "Python Tutorial")
        
        results = search.search_by_keyword("python")
        assert len(results) == 1
    
    def test_search_no_matches(self, manager, search):
        """Test search with no results."""
        manager.add_conversation("conv-1", "Python Tutorial")
        
        results = search.search_by_keyword("Ruby")
        assert results == []


class TestSearchByDateRange:
    """Tests for date range search."""
    
    def test_search_within_date_range(self, manager, search):
        """Test filtering by date range."""
        manager.add_conversation("conv-1", "Test")
        
        start = datetime.now() - timedelta(days=1)
        end = datetime.now() + timedelta(days=1)
        
        results = search.search_by_date_range(start, end)
        assert len(results) == 1
    
    def test_search_outside_date_range(self, manager, search):
        """Test that conversations outside range are excluded."""
        manager.add_conversation("conv-1", "Test")
        
        start = datetime.now() + timedelta(days=1)
        end = datetime.now() + timedelta(days=2)
        
        results = search.search_by_date_range(start, end)
        assert results == []
