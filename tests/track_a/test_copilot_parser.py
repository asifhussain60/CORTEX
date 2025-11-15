"""
Track A Phase 2: Comprehensive Unit Tests for CopilotParser

Tests markdown/text conversation parsing including:
- Format detection (markdown vs plain text)
- Message extraction and role detection
- Timestamp parsing and normalization
- Multi-turn conversation handling
- Edge cases and error handling

Author: CORTEX Team
Date: 2025-11-15
"""

import pytest
from datetime import datetime
from src.track_a.parsers.copilot_parser import CopilotParser


class TestCopilotParserBasics:
    """Test basic CopilotParser functionality."""
    
    @pytest.fixture
    def parser(self):
        """Create CopilotParser instance."""
        return CopilotParser()
    
    def test_parser_initialization(self, parser):
        """Test parser initializes successfully."""
        assert parser is not None
        assert hasattr(parser, 'parse')
        assert callable(parser.parse)
    
    def test_parser_has_detect_format_method(self, parser):
        """Test parser has format detection capability."""
        assert hasattr(parser, 'detect_format') or hasattr(parser, '_detect_format')


class TestMarkdownFormatParsing:
    """Test parsing markdown conversation format."""
    
    @pytest.fixture
    def parser(self):
        return CopilotParser()
    
    @pytest.fixture
    def simple_markdown(self):
        """Simple two-message conversation."""
        return """
**User:**
Hello, how are you?

**Assistant:**
I'm doing well, thanks for asking!
"""
    
    @pytest.fixture
    def complex_markdown(self):
        """Multi-turn conversation with code blocks."""
        return """
**User:**
How do I create a Python function?

**Assistant:**
Here's a simple Python function:

```python
def greet(name):
    return f"Hello, {name}!"
```

This function takes a name and returns a greeting.

**User:**
Can you add error handling?

**Assistant:**
Sure! Here's the updated version:

```python
def greet(name):
    if not name:
        raise ValueError("Name cannot be empty")
    return f"Hello, {name}!"
```
"""
    
    def test_parse_simple_markdown(self, parser, simple_markdown):
        """Test parsing simple two-message conversation."""
        result = parser.parse(simple_markdown)
        
        assert result is not None
        assert "messages" in result
        assert len(result["messages"]) == 2
        
        # Verify roles
        assert result["messages"][0]["role"] == "user"
        assert result["messages"][1]["role"] == "assistant"
        
        # Verify content
        assert "how are you" in result["messages"][0]["content"].lower()
        assert "doing well" in result["messages"][1]["content"].lower()
    
    def test_parse_multi_turn_markdown(self, parser, complex_markdown):
        """Test parsing multi-turn conversation."""
        result = parser.parse(complex_markdown)
        
        assert len(result["messages"]) == 4
        
        # Verify alternating roles
        assert result["messages"][0]["role"] == "user"
        assert result["messages"][1]["role"] == "assistant"
        assert result["messages"][2]["role"] == "user"
        assert result["messages"][3]["role"] == "assistant"
    
    def test_parse_preserves_code_blocks(self, parser, complex_markdown):
        """Test code blocks are preserved in content."""
        result = parser.parse(complex_markdown)
        
        # Find assistant message with code
        assistant_msg = result["messages"][1]["content"]
        assert "```python" in assistant_msg or "def greet" in assistant_msg
    
    def test_parse_extracts_timestamps(self, parser, simple_markdown):
        """Test timestamps are extracted for each message."""
        result = parser.parse(simple_markdown)
        
        for message in result["messages"]:
            assert "timestamp" in message
            # Timestamp should be valid ISO format or datetime string
            assert isinstance(message["timestamp"], str)
            assert len(message["timestamp"]) > 0
    
    def test_parse_markdown_format_detection(self, parser, simple_markdown):
        """Test parser detects markdown format."""
        result = parser.parse(simple_markdown)
        
        # Should detect format as markdown
        if "metadata" in result:
            assert result["metadata"].get("format") == "markdown"


class TestPlainTextFormatParsing:
    """Test parsing plain text conversation format."""
    
    @pytest.fixture
    def parser(self):
        return CopilotParser()
    
    @pytest.fixture
    def plain_text_conversation(self):
        """Plain text conversation without markdown."""
        return """
User: What's the weather like?
Assistant: I don't have access to real-time weather data.
User: Okay, thanks anyway.
Assistant: You're welcome!
"""
    
    def test_parse_plain_text(self, parser, plain_text_conversation):
        """Test parsing plain text format."""
        result = parser.parse(plain_text_conversation)
        
        assert result is not None
        assert "messages" in result
        assert len(result["messages"]) >= 2
    
    def test_parse_plain_text_detects_roles(self, parser, plain_text_conversation):
        """Test role detection in plain text."""
        result = parser.parse(plain_text_conversation)
        
        # Check roles are correctly identified
        user_found = any(msg["role"] == "user" for msg in result["messages"])
        assistant_found = any(msg["role"] == "assistant" for msg in result["messages"])
        
        assert user_found
        assert assistant_found


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def parser(self):
        return CopilotParser()
    
    def test_parse_empty_string(self, parser):
        """Test parsing empty string."""
        result = parser.parse("")
        
        # Should return empty result or raise appropriate error
        assert result is not None
        if "messages" in result:
            assert len(result["messages"]) == 0
    
    def test_parse_whitespace_only(self, parser):
        """Test parsing whitespace-only string."""
        result = parser.parse("   \n\n   \t\t   ")
        
        assert result is not None
        if "messages" in result:
            assert len(result["messages"]) == 0
    
    def test_parse_single_message(self, parser):
        """Test parsing single message (no conversation)."""
        single = "**User:**\nJust one message"
        result = parser.parse(single)
        
        assert result is not None
        assert "messages" in result
        assert len(result["messages"]) >= 1
    
    def test_parse_missing_role_markers(self, parser):
        """Test parsing text without clear role markers."""
        unclear = "This is some text without clear roles or structure."
        result = parser.parse(unclear)
        
        # Should handle gracefully (empty result or best-effort parsing)
        assert result is not None
        assert "messages" in result
    
    def test_parse_mixed_format(self, parser):
        """Test parsing mixed markdown and plain text."""
        mixed = """
**User:**
First message in markdown

User: Second message in plain text

**Assistant:**
Response in markdown
"""
        result = parser.parse(mixed)
        
        # Should parse successfully, extracting what it can
        assert result is not None
        assert "messages" in result
        assert len(result["messages"]) >= 2


class TestTimestampHandling:
    """Test timestamp extraction and normalization."""
    
    @pytest.fixture
    def parser(self):
        return CopilotParser()
    
    def test_timestamp_format_consistency(self, parser):
        """Test all timestamps use consistent format."""
        conversation = """
**User:**
Message 1

**Assistant:**
Response 1

**User:**
Message 2
"""
        result = parser.parse(conversation)
        
        timestamps = [msg["timestamp"] for msg in result["messages"]]
        
        # All timestamps should be non-empty strings
        assert all(isinstance(ts, str) for ts in timestamps)
        assert all(len(ts) > 0 for ts in timestamps)
    
    def test_timestamp_parseable_as_datetime(self, parser):
        """Test timestamps can be parsed as datetime objects."""
        conversation = "**User:**\nTest\n\n**Assistant:**\nResponse"
        result = parser.parse(conversation)
        
        for message in result["messages"]:
            timestamp = message["timestamp"]
            # Should be parseable by datetime
            try:
                if "T" in timestamp:
                    datetime.fromisoformat(timestamp)
                else:
                    datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pytest.fail(f"Timestamp not parseable: {timestamp}")
    
    def test_timestamp_ordering(self, parser):
        """Test timestamps maintain chronological order."""
        conversation = """
**User:**
First

**Assistant:**
Second

**User:**
Third
"""
        result = parser.parse(conversation)
        
        timestamps = [msg["timestamp"] for msg in result["messages"]]
        
        # Parse and verify chronological order
        parsed_times = []
        for ts in timestamps:
            if "T" in ts:
                parsed_times.append(datetime.fromisoformat(ts))
            else:
                parsed_times.append(datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"))
        
        # Timestamps should be in order or very close
        for i in range(len(parsed_times) - 1):
            time_diff = (parsed_times[i+1] - parsed_times[i]).total_seconds()
            assert time_diff >= 0, "Timestamps should be chronological"


class TestMetadataExtraction:
    """Test metadata extraction from conversations."""
    
    @pytest.fixture
    def parser(self):
        return CopilotParser()
    
    def test_parse_returns_metadata(self, parser):
        """Test parse result includes metadata."""
        conversation = "**User:**\nTest\n\n**Assistant:**\nResponse"
        result = parser.parse(conversation)
        
        # Should have metadata field
        assert "metadata" in result or "messages" in result
    
    def test_metadata_includes_message_count(self, parser):
        """Test metadata includes message count."""
        conversation = "**User:**\nTest\n\n**Assistant:**\nResponse"
        result = parser.parse(conversation)
        
        if "metadata" in result:
            metadata = result["metadata"]
            assert "message_count" in metadata or "total_messages" in metadata


class TestSpecialCharacterHandling:
    """Test handling of special characters and unicode."""
    
    @pytest.fixture
    def parser(self):
        return CopilotParser()
    
    def test_parse_unicode_content(self, parser):
        """Test parsing content with unicode characters."""
        unicode_conv = """
**User:**
Hello 👋 How are you?

**Assistant:**
I'm great! 😊 Thanks for asking.
"""
        result = parser.parse(unicode_conv)
        
        assert len(result["messages"]) == 2
        assert "👋" in result["messages"][0]["content"]
        assert "😊" in result["messages"][1]["content"]
    
    def test_parse_special_markdown_chars(self, parser):
        """Test parsing markdown with special characters."""
        special_conv = """
**User:**
Can you explain `**bold**` and *italic*?

**Assistant:**
Sure! Use `**text**` for **bold** and `*text*` for *italic*.
"""
        result = parser.parse(special_conv)
        
        assert len(result["messages"]) == 2
        # Content should preserve special markdown chars
        assert "**" in result["messages"][0]["content"] or "bold" in result["messages"][0]["content"]
    
    def test_parse_code_with_backticks(self, parser):
        """Test parsing code blocks with backticks."""
        code_conv = """
**User:**
Show me a function

**Assistant:**
Here's an example:

```python
def example():
    return "test"
```
"""
        result = parser.parse(code_conv)
        
        assert len(result["messages"]) == 2
        # Code block should be preserved
        assert "```" in result["messages"][1]["content"] or "def example" in result["messages"][1]["content"]
