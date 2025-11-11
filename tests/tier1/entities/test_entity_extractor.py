"""
Unit tests for EntityExtractor module.
"""

import pytest
import tempfile
from pathlib import Path
from src.tier1.entities import EntityExtractor, EntityType


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def extractor(temp_db):
    """Create an EntityExtractor instance with temp database."""
    return EntityExtractor(temp_db)


class TestExtractEntities:
    """Tests for entity extraction."""
    
    def test_extract_file_entities(self, extractor):
        """Test extracting file paths."""
        content = "Check the file `src/main.py` for the implementation."
        entities = extractor.extract_entities("conv-1", content)
        
        file_entities = [e for e in entities if e.entity_type == EntityType.FILE]
        assert len(file_entities) >= 1
        assert any("main.py" in e.entity_name for e in file_entities)
    
    def test_extract_class_entities(self, extractor):
        """Test extracting class names."""
        content = "The `UserManager` class handles authentication."
        entities = extractor.extract_entities("conv-1", content)
        
        class_entities = [e for e in entities if e.entity_type == EntityType.CLASS]
        assert len(class_entities) >= 1
        assert any("UserManager" in e.entity_name for e in class_entities)
    
    def test_extract_method_entities(self, extractor):
        """Test extracting method names."""
        content = "Call the `calculate_total()` method to get the sum."
        entities = extractor.extract_entities("conv-1", content)
        
        method_entities = [e for e in entities if e.entity_type == EntityType.METHOD]
        assert len(method_entities) >= 1
        assert any("calculate_total" in e.entity_name for e in method_entities)
    
    def test_extract_multiple_entity_types(self, extractor):
        """Test extracting mixed entity types."""
        content = """
        In the file `src/models/user.py`, the `UserModel` class 
        has a `validate()` method that checks inputs.
        """
        entities = extractor.extract_entities("conv-1", content)
        
        entity_types = {e.entity_type for e in entities}
        assert EntityType.FILE in entity_types
        assert EntityType.CLASS in entity_types
        assert EntityType.METHOD in entity_types
    
    def test_extract_with_no_entities(self, extractor):
        """Test extraction with plain text (no entities)."""
        content = "This is just plain text with no code references."
        entities = extractor.extract_entities("conv-1", content)
        
        assert len(entities) == 0


class TestGetConversationEntities:
    """Tests for retrieving conversation entities."""
    
    def test_get_entities_after_extraction(self, extractor):
        """Test retrieving entities linked to conversation."""
        content = "The Calculator class has an add() method."
        extractor.extract_entities("conv-1", content)
        
        entities = extractor.get_conversation_entities("conv-1")
        assert len(entities) >= 2  # Calculator + add
    
    def test_get_entities_empty_conversation(self, extractor):
        """Test getting entities from conversation with none."""
        entities = extractor.get_conversation_entities("nonexistent")
        assert entities == []


class TestGetEntityStatistics:
    """Tests for entity statistics."""
    
    def test_get_statistics_includes_access_count(self, extractor):
        """Test that statistics include access counts."""
        # Extract same entities multiple times
        content = "Use the Logger class"
        extractor.extract_entities("conv-1", content)
        extractor.extract_entities("conv-2", content)
        
        stats = extractor.get_entity_statistics()
        
        logger_stats = [s for s in stats if "Logger" in s["entity_name"]]
        assert len(logger_stats) > 0
        assert logger_stats[0]["access_count"] >= 2
    
    def test_get_statistics_empty_database(self, extractor):
        """Test statistics with no entities."""
        stats = extractor.get_entity_statistics()
        assert stats == []
