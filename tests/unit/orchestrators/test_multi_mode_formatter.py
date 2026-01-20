"""Tests for Multi-Mode Response Formatting (AC-RESP-002-01)."""
import pytest
from cortex.orchestrators.response.multi_mode_formatter import (
    FormattingProfile,
    ResponseComponent,
    FormattingOptions,
    FormattedResponseSection,
    ChatResponseFormatter,
    CommandLineResponseFormatter,
    VisualizationResponseFormatter,
    JSONAPIResponseFormatter,
    MarkdownResponseFormatter,
    StreamResponseFormatter,
    ResponseFormattingEngine,
)

class TestFormattingProfile:
    """Test formatting profile options."""
    
    def test_all_profiles_defined(self):
        """All formatting profiles are defined."""
        profiles = [
            FormattingProfile.COMPACT,
            FormattingProfile.STANDARD,
            FormattingProfile.VERBOSE,
            FormattingProfile.MINIMAL,
            FormattingProfile.RICH,
        ]
        
        assert len(profiles) == 5

class TestResponseComponent:
    """Test response component types."""
    
    def test_all_components_defined(self):
        """All response components are defined."""
        components = [
            ResponseComponent.OPERATION_CONTEXT,
            ResponseComponent.BRIEF_SUMMARY,
            ResponseComponent.DETAILED_EXPLANATION,
            ResponseComponent.CODE_EXAMPLE,
            ResponseComponent.ALTERNATIVES,
            ResponseComponent.WARNINGS,
            ResponseComponent.NEXT_STEPS,
            ResponseComponent.METADATA,
        ]
        
        assert len(components) == 8

class TestFormattingOptions:
    """Test formatting options."""
    
    def test_options_initialization(self):
        """FormattingOptions initializes with defaults."""
        options = FormattingOptions()
        
        assert options.profile == FormattingProfile.STANDARD
        assert options.include_metadata is True
        assert options.max_line_length == 80
    
    def test_options_custom_profile(self):
        """Custom formatting profile."""
        options = FormattingOptions(profile=FormattingProfile.COMPACT)
        
        assert options.profile == FormattingProfile.COMPACT

class TestFormattedResponseSection:
    """Test response section structure."""
    
    def test_section_initialization(self):
        """Section initializes correctly."""
        section = FormattedResponseSection(
            section_type=ResponseComponent.BRIEF_SUMMARY,
            title="Summary",
            content="This is a summary",
        )
        
        assert section.section_type == ResponseComponent.BRIEF_SUMMARY
        assert section.title == "Summary"
        assert section.content == "This is a summary"
        assert section.priority == 0

class TestChatResponseFormatter:
    """Test chat response formatting."""
    
    def test_format_basic(self):
        """Format basic content for chat."""
        content = "Hello, this is a test response"
        options = FormattingOptions()
        
        formatted = ChatResponseFormatter.format(content, options)
        
        assert "Hello" in formatted
        assert "test response" in formatted
    
    def test_format_with_newlines(self):
        """Format content with multiple lines."""
        content = "Line 1\nLine 2\nLine 3"
        options = FormattingOptions()
        
        formatted = ChatResponseFormatter.format(content, options)
        
        assert "Line 1" in formatted
        assert "Line 2" in formatted
        assert "Line 3" in formatted
    
    def test_format_compact_profile(self):
        """Format with compact profile."""
        content = "  Indented line  \n  Another line  "
        options = FormattingOptions(profile=FormattingProfile.COMPACT)
        
        formatted = ChatResponseFormatter.format(content, options)
        
        # Compact removes extra whitespace
        assert "Indented line" in formatted
    
    def test_text_wrapping(self):
        """Text wrapping respects max line length."""
        content = "This is a very long line that should be wrapped when the maximum line length is exceeded for better readability"
        options = FormattingOptions(max_line_length=40)
        
        formatted = ChatResponseFormatter.format(content, options)
        
        # Should have line breaks
        lines = formatted.split('\n')
        assert any(len(line) <= 40 or len(line) == 0 for line in lines if line)

class TestCommandLineResponseFormatter:
    """Test CLI response formatting."""
    
    def test_format_basic(self):
        """Format for command line."""
        content = "Operation complete"
        options = FormattingOptions()
        
        formatted = CommandLineResponseFormatter.format(content, options)
        
        assert "RESPONSE" in formatted
        assert "Operation complete" in formatted
        assert "=" in formatted
    
    def test_format_includes_metadata(self):
        """CLI format includes metadata when enabled."""
        content = "Done"
        options = FormattingOptions(include_metadata=True)
        
        formatted = CommandLineResponseFormatter.format(content, options)
        
        assert "✓" in formatted or "complete" in formatted

class TestVisualizationResponseFormatter:
    """Test visualization response formatting."""
    
    def test_format_basic(self):
        """Format for visualization."""
        content = "Graph data"
        
        formatted = VisualizationResponseFormatter.format(content)
        
        assert formatted["type"] == "visualization"
        assert formatted["content"] == "Graph data"
        assert "metadata" in formatted
    
    def test_format_with_data(self):
        """Format with visualization data."""
        content = "Graph"
        data = {"nodes": [1, 2, 3], "edges": [[1, 2], [2, 3]]}
        
        formatted = VisualizationResponseFormatter.format(content, data)
        
        assert formatted["data"] == data

class TestJSONAPIResponseFormatter:
    """Test JSON API response formatting."""
    
    def test_format_basic(self):
        """Format for JSON API."""
        content = "Response content"
        options = FormattingOptions()
        
        formatted = JSONAPIResponseFormatter.format(
            content,
            "op_001",
            1,
            options
        )
        
        assert formatted["jsonapi"]["version"] == "1.0"
        assert formatted["data"]["type"] == "response"
        assert formatted["data"]["attributes"]["content"] == "Response content"

class TestMarkdownResponseFormatter:
    """Test Markdown response formatting."""
    
    def test_format_basic(self):
        """Format as markdown."""
        content = "Response content"
        
        formatted = MarkdownResponseFormatter.format(content)
        
        assert "Response content" in formatted
    
    def test_format_with_title(self):
        """Format markdown with title."""
        content = "Content here"
        title = "My Title"
        
        formatted = MarkdownResponseFormatter.format(content, title)
        
        assert "# My Title" in formatted
        assert "Content here" in formatted
    
    def test_format_with_sections(self):
        """Format markdown with sections."""
        content = "Main content"
        sections = [
            FormattedResponseSection(
                section_type=ResponseComponent.BRIEF_SUMMARY,
                title="Summary",
                content="Brief summary here",
                priority=10,
            ),
            FormattedResponseSection(
                section_type=ResponseComponent.DETAILED_EXPLANATION,
                title="Details",
                content="Detailed info here",
                priority=5,
            ),
        ]
        
        formatted = MarkdownResponseFormatter.format(content, sections=sections)
        
        assert "## Summary" in formatted
        assert "Brief summary here" in formatted
        assert "## Details" in formatted

class TestStreamResponseFormatter:
    """Test streaming response formatting."""
    
    def test_format_chunk(self):
        """Format single chunk."""
        chunk = "Response part 1"
        
        formatted = StreamResponseFormatter.format_chunk(chunk, 1, 3)
        
        assert formatted["type"] == "chunk"
        assert formatted["number"] == 1
        assert formatted["total"] == 3
        assert formatted["content"] == "Response part 1"
        assert formatted["is_final"] is False
    
    def test_format_final_chunk(self):
        """Format final chunk in stream."""
        chunk = "Final part"
        
        formatted = StreamResponseFormatter.format_chunk(chunk, 3, 3)
        
        assert formatted["is_final"] is True
    
    def test_format_stream(self):
        """Format multiple chunks."""
        chunks = ["Part 1", "Part 2", "Part 3"]
        
        formatted = StreamResponseFormatter.format_stream(chunks)
        
        assert len(formatted) == 3
        assert formatted[0]["number"] == 1
        assert formatted[2]["is_final"] is True

class TestResponseFormattingEngine:
    """Test main formatting engine."""
    
    def test_engine_initialization(self):
        """Engine initializes correctly."""
        engine = ResponseFormattingEngine()
        
        assert len(engine.formatters) == 6
        assert engine.formatting_stats['total_formatted'] == 0
    
    def test_format_chat_mode(self):
        """Format in chat mode."""
        engine = ResponseFormattingEngine()
        content = "Test response"
        
        formatted = engine.format_response(content, mode='chat')
        
        assert isinstance(formatted, str)
        assert "Test response" in formatted
    
    def test_format_command_mode(self):
        """Format in command mode."""
        engine = ResponseFormattingEngine()
        content = "Done"
        
        formatted = engine.format_response(content, mode='command')
        
        assert isinstance(formatted, str)
        assert "Done" in formatted
    
    def test_format_json_mode(self):
        """Format in JSON API mode."""
        engine = ResponseFormattingEngine()
        content = "JSON response"
        
        formatted = engine.format_response(
            content,
            mode='json',
            operation_id='op_001',
            turn_number=1,
        )
        
        assert isinstance(formatted, dict)
        assert "data" in formatted
    
    def test_format_markdown_mode(self):
        """Format in markdown mode."""
        engine = ResponseFormattingEngine()
        content = "Markdown content"
        
        formatted = engine.format_response(content, mode='markdown')
        
        assert isinstance(formatted, str)
    
    def test_format_stream_mode(self):
        """Format in stream mode."""
        engine = ResponseFormattingEngine()
        
        formatted = engine.format_response(
            "ignored",
            mode='stream',
            chunks=['Chunk 1', 'Chunk 2'],
        )
        
        assert isinstance(formatted, list)
        assert len(formatted) == 2
    
    def test_statistics_tracking(self):
        """Engine tracks formatting statistics."""
        engine = ResponseFormattingEngine()
        
        engine.format_response("Test", mode='chat')
        engine.format_response("Test", mode='chat')
        engine.format_response("Test", mode='json', operation_id='op_001', turn_number=1)
        
        stats = engine.get_formatting_statistics()
        
        assert stats['total_formatted'] == 3
        assert stats['by_mode']['chat'] == 2
        assert stats['by_mode']['json'] == 1
    
    def test_batch_format(self):
        """Batch format multiple responses."""
        engine = ResponseFormattingEngine()
        contents = ["Content 1", "Content 2", "Content 3"]
        
        formatted = engine.batch_format(contents, mode='chat')
        
        assert len(formatted) == 3
        assert engine.formatting_stats['total_formatted'] == 3
    
    def test_profile_statistics(self):
        """Profile usage tracked in statistics."""
        engine = ResponseFormattingEngine()
        
        options_compact = FormattingOptions(profile=FormattingProfile.COMPACT)
        options_verbose = FormattingOptions(profile=FormattingProfile.VERBOSE)
        
        engine.format_response("Test", mode='chat', options=options_compact)
        engine.format_response("Test", mode='chat', options=options_verbose)
        engine.format_response("Test", mode='chat', options=options_compact)
        
        stats = engine.get_formatting_statistics()
        
        assert stats['by_profile']['compact'] == 2
        assert stats['by_profile']['verbose'] == 1
    
    def test_reset_statistics(self):
        """Statistics can be reset."""
        engine = ResponseFormattingEngine()
        
        engine.format_response("Test", mode='chat')
        assert engine.formatting_stats['total_formatted'] == 1
        
        engine.reset_statistics()
        
        assert engine.formatting_stats['total_formatted'] == 0
        assert len(engine.formatting_stats['by_mode']) == 0
    
    def test_format_conversion(self):
        """Convert between formats."""
        engine = ResponseFormattingEngine()
        
        # Format as chat first
        chat_response = engine.format_response("Test content", mode='chat')
        
        # Convert to markdown
        markdown = engine.convert_format(chat_response, 'chat', 'markdown')
        
        assert isinstance(markdown, str)
        assert "Test content" in markdown
    
    def test_default_mode_fallback(self):
        """Unknown mode defaults to chat."""
        engine = ResponseFormattingEngine()
        content = "Default"
        
        formatted = engine.format_response(content, mode='unknown')
        
        assert isinstance(formatted, str)
        assert "Default" in formatted
    
    def test_formatting_options_default(self):
        """Default formatting options applied."""
        engine = ResponseFormattingEngine()
        content = "Test"
        
        # No options provided, should use defaults
        formatted = engine.format_response(content, mode='chat')
        
        assert formatted is not None
        assert "Test" in formatted
    
    def test_custom_formatting_options(self):
        """Custom formatting options respected."""
        engine = ResponseFormattingEngine()
        options = FormattingOptions(profile=FormattingProfile.MINIMAL)
        content = "Test content here"
        
        formatted = engine.format_response(content, mode='chat', options=options)
        
        assert "Test content here" in formatted

class TestFormattingIntegration:
    """Integration tests for response formatting."""
    
    def test_full_workflow_single_format(self):
        """Full workflow: generate and format response."""
        engine = ResponseFormattingEngine()
        
        # Generate response
        response = "Operation successful. All tests passed."
        
        # Format for different modes
        chat = engine.format_response(response, mode='chat')
        json_fmt = engine.format_response(response, mode='json', operation_id='op_001', turn_number=1)
        markdown = engine.format_response(response, mode='markdown')
        
        # All should succeed
        assert chat is not None
        assert json_fmt is not None
        assert markdown is not None
    
    def test_batch_processing_performance(self):
        """Batch processing of multiple responses."""
        engine = ResponseFormattingEngine()
        
        contents = [f"Response {i}" for i in range(100)]
        formatted = engine.batch_format(contents, mode='chat')
        
        assert len(formatted) == 100
        assert engine.formatting_stats['total_formatted'] == 100
