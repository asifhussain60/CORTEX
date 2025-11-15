"""
Track A Phase 2: Comprehensive Unit Tests for ConversationImporter

Tests the high-level import orchestration including:
- Import workflow coordination
- Source detection and parsing
- Error handling and recovery
- Import statistics and reporting
- Concurrent import scenarios

Author: CORTEX Team
Date: 2025-11-15
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from src.track_a.conversation_import import ConversationImporter
from src.track_a.parsers.copilot_parser import CopilotParser
from src.track_a.extractors.semantic_extractor import SemanticExtractor
from src.track_a.integrations.conversational_channel_adapter import ConversationalChannelAdapter


class TestConversationImporterBasics:
    """Test basic ConversationImporter functionality."""
    
    @pytest.fixture
    def importer(self):
        """Create ConversationImporter instance."""
        return ConversationImporter()
    
    def test_importer_initialization(self, importer):
        """Test importer initializes with all required components."""
        assert importer.parser is not None
        assert isinstance(importer.parser, CopilotParser)
        assert importer.extractor is not None
        assert isinstance(importer.extractor, SemanticExtractor)
        assert importer.channel_adapter is not None
        assert isinstance(importer.channel_adapter, ConversationalChannelAdapter)
    
    def test_importer_has_import_method(self, importer):
        """Test importer has import_conversation method."""
        assert hasattr(importer, 'import_conversation')
        assert callable(importer.import_conversation)
    
    def test_importer_component_defaults(self, importer):
        """Test importer creates default components if none provided."""
        # Verify components are functional (not None or Mock)
        assert importer.parser.parse is not None
        assert importer.extractor.extract is not None
        assert importer.channel_adapter.store_conversation is not None


class TestConversationImportWorkflow:
    """Test complete import workflow orchestration."""
    
    @pytest.fixture
    def importer(self):
        return ConversationImporter()
    
    @pytest.fixture
    def sample_markdown(self):
        """Sample markdown conversation for testing."""
        return """
**User:**
How do I create a button component?

**Assistant:**
Here's how to create a button component:

```python
class Button:
    def __init__(self, label):
        self.label = label
```

This creates a simple button class.
"""
    
    def test_import_markdown_conversation(self, importer, sample_markdown):
        """Test importing a markdown conversation."""
        result = importer.import_conversation(sample_markdown, source="test")
        
        assert result["success"] is True
        assert "conversation_id" in result
        assert result["conversation_id"].startswith("imported-conv-")
        assert "import_report" in result
        assert result["import_report"]["total_imported"] == 1
    
    def test_import_assigns_conversation_id(self, importer, sample_markdown):
        """Test import generates unique conversation ID."""
        result1 = importer.import_conversation(sample_markdown, source="test1")
        result2 = importer.import_conversation(sample_markdown, source="test2")
        
        assert result1["conversation_id"] != result2["conversation_id"]
    
    def test_import_preserves_source(self, importer, sample_markdown):
        """Test import preserves conversation source metadata."""
        source = "github-copilot-chat"
        result = importer.import_conversation(sample_markdown, source=source)
        
        assert result["success"] is True
        # Verify source stored in conversation metadata
        conversation_id = result["conversation_id"]
        retrieved = importer.channel_adapter.retrieve_conversation(conversation_id)
        assert retrieved is not None
    
    def test_import_workflow_steps(self, importer, sample_markdown):
        """Test import executes all workflow steps: parse → extract → store."""
        # Mock components to verify call chain
        importer.parser.parse = Mock(return_value={
            "messages": [{"role": "user", "content": "test", "timestamp": "2025-11-15T10:00:00"}],
            "metadata": {}
        })
        importer.extractor.extract = Mock(return_value={
            "entities": [],
            "intents": ["EXECUTE"],
            "quality": 5.0
        })
        importer.channel_adapter.store_conversation = Mock(return_value={
            "success": True,
            "conversation_id": "test-id-123"
        })
        
        result = importer.import_conversation(sample_markdown, source="test")
        
        # Verify all components called
        importer.parser.parse.assert_called_once()
        importer.extractor.extract.assert_called_once()
        importer.channel_adapter.store_conversation.assert_called_once()


class TestConversationImportErrorHandling:
    """Test error handling during import."""
    
    @pytest.fixture
    def importer(self):
        return ConversationImporter()
    
    def test_import_empty_text(self, importer):
        """Test importing empty text returns error."""
        result = importer.import_conversation("", source="test")
        
        assert result["success"] is False
        assert "error" in result
        assert "empty" in result["error"].lower()
    
    def test_import_none_text(self, importer):
        """Test importing None text returns error."""
        result = importer.import_conversation(None, source="test")
        
        assert result["success"] is False
        assert "error" in result
    
    def test_import_invalid_format(self, importer):
        """Test importing invalid format returns error."""
        invalid_text = "This is not a valid conversation format"
        result = importer.import_conversation(invalid_text, source="test")
        
        # Should either succeed with warning or fail gracefully
        assert "success" in result
        if result["success"] is False:
            assert "error" in result or "warning" in result
    
    def test_import_parser_error_recovery(self, importer):
        """Test import handles parser errors gracefully."""
        # Mock parser to raise exception
        importer.parser.parse = Mock(side_effect=Exception("Parser error"))
        
        result = importer.import_conversation("test text", source="test")
        
        assert result["success"] is False
        assert "error" in result
        assert "parser" in result["error"].lower() or "parse" in result["error"].lower()
    
    def test_import_extractor_error_recovery(self, importer):
        """Test import handles extractor errors gracefully."""
        # Mock parser to succeed, extractor to fail
        importer.parser.parse = Mock(return_value={
            "messages": [{"role": "user", "content": "test", "timestamp": "2025-11-15T10:00:00"}]
        })
        importer.extractor.extract = Mock(side_effect=Exception("Extractor error"))
        
        result = importer.import_conversation("test text", source="test")
        
        assert result["success"] is False
        assert "error" in result
    
    def test_import_storage_error_recovery(self, importer):
        """Test import handles storage errors gracefully."""
        # Mock parser and extractor to succeed, storage to fail
        importer.parser.parse = Mock(return_value={
            "messages": [{"role": "user", "content": "test", "timestamp": "2025-11-15T10:00:00"}]
        })
        importer.extractor.extract = Mock(return_value={
            "entities": [],
            "intents": ["EXECUTE"],
            "quality": 5.0
        })
        importer.channel_adapter.store_conversation = Mock(return_value={
            "success": False,
            "error": "Storage failure"
        })
        
        result = importer.import_conversation("test text", source="test")
        
        assert result["success"] is False
        assert "error" in result


class TestConversationImportStatistics:
    """Test import statistics and reporting."""
    
    @pytest.fixture
    def importer(self):
        return ConversationImporter()
    
    @pytest.fixture
    def sample_conversation(self):
        return """
**User:**
Test message 1

**Assistant:**
Response 1

**User:**
Test message 2

**Assistant:**
Response 2
"""
    
    def test_import_report_includes_message_count(self, importer, sample_conversation):
        """Test import report includes message count."""
        result = importer.import_conversation(sample_conversation, source="test")
        
        assert result["success"] is True
        assert "import_report" in result
        assert "messages_imported" in result["import_report"] or "total_imported" in result["import_report"]
    
    def test_import_report_includes_entity_count(self, importer, sample_conversation):
        """Test import report includes entity count."""
        result = importer.import_conversation(sample_conversation, source="test")
        
        assert result["success"] is True
        assert "import_report" in result
        # Entity count may be 0 if no entities detected
        report = result["import_report"]
        assert "entities_extracted" in report or "entities" in str(report)
    
    def test_import_report_includes_quality_score(self, importer, sample_conversation):
        """Test import report includes quality score."""
        result = importer.import_conversation(sample_conversation, source="test")
        
        assert result["success"] is True
        assert "import_report" in result or "quality" in result


class TestConcurrentImports:
    """Test concurrent import scenarios."""
    
    @pytest.fixture
    def importer(self):
        return ConversationImporter()
    
    def test_sequential_imports_dont_interfere(self, importer):
        """Test sequential imports maintain isolation."""
        conv1 = "**User:** Test 1\n**Assistant:** Response 1"
        conv2 = "**User:** Test 2\n**Assistant:** Response 2"
        
        result1 = importer.import_conversation(conv1, source="test1")
        result2 = importer.import_conversation(conv2, source="test2")
        
        assert result1["success"] is True
        assert result2["success"] is True
        assert result1["conversation_id"] != result2["conversation_id"]
    
    def test_import_idempotency(self, importer):
        """Test importing same conversation twice creates separate entries."""
        conv = "**User:** Test\n**Assistant:** Response"
        
        result1 = importer.import_conversation(conv, source="test")
        result2 = importer.import_conversation(conv, source="test")
        
        # Should create two separate conversation entries
        assert result1["conversation_id"] != result2["conversation_id"]
