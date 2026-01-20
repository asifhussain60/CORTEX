"""Tests for Turn-by-Turn Response Generation (AC-RESP-001-01)."""
import pytest
from datetime import datetime
from cortex.orchestrators.response.turn_response_generator import (
    ResponseMode,
    ResponseTone,
    ResponseMetadata,
    ResponseSegment,
    TurnResponse,
    ResponseBuilder,
    ResponseFormatter,
    TurnResponseGenerator,
)

class TestResponseModes:
    """Test supported response modes."""
    
    def test_all_response_modes_defined(self):
        """All response modes are defined."""
        modes = [
            ResponseMode.CHAT,
            ResponseMode.COMMAND,
            ResponseMode.VISUALIZATION,
            ResponseMode.JSON_API,
            ResponseMode.MARKDOWN,
            ResponseMode.STREAM,
        ]
        
        assert len(modes) == 6
        assert all(mode.value for mode in modes)
    
    def test_response_mode_values(self):
        """Response mode values are strings."""
        assert ResponseMode.CHAT.value == "chat"
        assert ResponseMode.COMMAND.value == "command"
        assert ResponseMode.VISUALIZATION.value == "visualization"
        assert ResponseMode.JSON_API.value == "json_api"
        assert ResponseMode.MARKDOWN.value == "markdown"
        assert ResponseMode.STREAM.value == "stream"

class TestResponseTones:
    """Test response tone options."""
    
    def test_all_response_tones_defined(self):
        """All response tones are defined."""
        tones = [
            ResponseTone.FORMAL,
            ResponseTone.CASUAL,
            ResponseTone.TECHNICAL,
            ResponseTone.EXECUTIVE,
            ResponseTone.EDUCATIONAL,
        ]
        
        assert len(tones) == 5
    
    def test_response_tone_values(self):
        """Response tone values are strings."""
        assert ResponseTone.FORMAL.value == "formal"
        assert ResponseTone.CASUAL.value == "casual"
        assert ResponseTone.TECHNICAL.value == "technical"
        assert ResponseTone.EXECUTIVE.value == "executive"
        assert ResponseTone.EDUCATIONAL.value == "educational"

class TestResponseMetadata:
    """Test response metadata structure."""
    
    def test_metadata_initialization(self):
        """Metadata initializes with required fields."""
        metadata = ResponseMetadata(
            mode=ResponseMode.CHAT,
            tone=ResponseTone.TECHNICAL,
            turn_number=1,
            operation_id="op_001",
            phase="PHASE-24",
            orchestrator="MasterOrchestrator"
        )
        
        assert metadata.mode == ResponseMode.CHAT
        assert metadata.tone == ResponseTone.TECHNICAL
        assert metadata.turn_number == 1
        assert metadata.operation_id == "op_001"
        assert metadata.phase == "PHASE-24"
        assert metadata.orchestrator == "MasterOrchestrator"
    
    def test_metadata_context_hash_generated(self):
        """Context hash is generated during initialization."""
        metadata = ResponseMetadata(
            mode=ResponseMode.CHAT,
            tone=ResponseTone.TECHNICAL,
            turn_number=1,
            operation_id="op_001",
            phase="PHASE-24",
            orchestrator="MasterOrchestrator"
        )
        
        assert metadata.context_hash
        assert len(metadata.context_hash) == 32  # MD5 hex length
    
    def test_metadata_timestamp_set(self):
        """Timestamp is set automatically."""
        before = datetime.now()
        metadata = ResponseMetadata(
            mode=ResponseMode.CHAT,
            tone=ResponseTone.TECHNICAL,
            turn_number=1,
            operation_id="op_001",
            phase="PHASE-24",
            orchestrator="MasterOrchestrator"
        )
        after = datetime.now()
        
        assert before <= metadata.timestamp <= after
    
    def test_metadata_token_estimate_default(self):
        """Token estimate defaults to 0."""
        metadata = ResponseMetadata(
            mode=ResponseMode.CHAT,
            tone=ResponseTone.TECHNICAL,
            turn_number=1,
            operation_id="op_001",
            phase="PHASE-24",
            orchestrator="MasterOrchestrator"
        )
        
        assert metadata.token_estimate == 0

class TestResponseSegment:
    """Test response segment structure."""
    
    def test_segment_initialization(self):
        """Segment initializes with required fields."""
        segment = ResponseSegment(
            segment_type="body",
            content="This is test content",
        )
        
        assert segment.segment_type == "body"
        assert segment.content == "This is test content"
        assert segment.length == 20
    
    def test_segment_types(self):
        """Segments support standard types."""
        types = ["header", "body", "alternatives", "footer"]
        
        for seg_type in types:
            segment = ResponseSegment(
                segment_type=seg_type,
                content="Test content",
            )
            assert segment.segment_type == seg_type
    
    def test_segment_length_calculation(self):
        """Segment length is calculated automatically."""
        content = "This is longer content for testing length calculation"
        segment = ResponseSegment(
            segment_type="body",
            content=content,
        )
        
        assert segment.length == len(content)

class TestTurnResponse:
    """Test turn response structure."""
    
    def test_turn_response_initialization(self):
        """Turn response initializes with required fields."""
        metadata = ResponseMetadata(
            mode=ResponseMode.CHAT,
            tone=ResponseTone.TECHNICAL,
            turn_number=1,
            operation_id="op_001",
            phase="PHASE-24",
            orchestrator="MasterOrchestrator"
        )
        
        response = TurnResponse(
            operation_id="op_001",
            turn_number=1,
            metadata=metadata,
        )
        
        assert response.operation_id == "op_001"
        assert response.turn_number == 1
        assert response.metadata == metadata
        assert response.ready_to_send is False
    
    def test_turn_response_segment_property(self):
        """Segment summary property works."""
        metadata = ResponseMetadata(
            mode=ResponseMode.CHAT,
            tone=ResponseTone.TECHNICAL,
            turn_number=1,
            operation_id="op_001",
            phase="PHASE-24",
            orchestrator="MasterOrchestrator"
        )
        
        response = TurnResponse(
            operation_id="op_001",
            turn_number=1,
            metadata=metadata,
            segments=[
                ResponseSegment(segment_type="header", content="Header content"),
                ResponseSegment(segment_type="body", content="Body content here"),
            ]
        )
        
        summary = response.segment_summary
        assert "header" in summary
        assert "body" in summary
        assert summary["header"] == 14
        assert summary["body"] == 17
    
    def test_turn_response_total_length(self):
        """Total length sums all segments."""
        metadata = ResponseMetadata(
            mode=ResponseMode.CHAT,
            tone=ResponseTone.TECHNICAL,
            turn_number=1,
            operation_id="op_001",
            phase="PHASE-24",
            orchestrator="MasterOrchestrator"
        )
        
        response = TurnResponse(
            operation_id="op_001",
            turn_number=1,
            metadata=metadata,
            segments=[
                ResponseSegment(segment_type="header", content="A"),
                ResponseSegment(segment_type="body", content="BC"),
            ]
        )
        
        assert response.total_length == 3

class TestResponseBuilder:
    """Test response builder functionality."""
    
    def test_builder_initialization(self):
        """Builder initializes correctly."""
        builder = ResponseBuilder("op_001", 1, ResponseMode.CHAT)
        
        assert builder.operation_id == "op_001"
        assert builder.turn_number == 1
        assert builder.mode == ResponseMode.CHAT
        assert len(builder.segments) == 0
    
    def test_builder_add_header(self):
        """Builder can add header segment."""
        builder = ResponseBuilder("op_001", 1)
        builder.add_header("Test header")
        
        assert len(builder.segments) == 1
        assert builder.segments[0].segment_type == "header"
        assert builder.segments[0].content == "Test header"
    
    def test_builder_add_body(self):
        """Builder can add body segment."""
        builder = ResponseBuilder("op_001", 1)
        builder.add_body("Test body content")
        
        assert len(builder.segments) == 1
        assert builder.segments[0].segment_type == "body"
    
    def test_builder_add_alternatives(self):
        """Builder can add alternatives segment."""
        builder = ResponseBuilder("op_001", 1)
        alternatives = [
            {"name": "Alt1", "description": "First alternative"},
            {"name": "Alt2", "description": "Second alternative"},
        ]
        builder.add_alternatives(alternatives)
        
        assert len(builder.segments) == 1
        assert builder.segments[0].segment_type == "alternatives"
        assert len(builder.alternatives) == 2
    
    def test_builder_add_footer(self):
        """Builder can add footer segment."""
        builder = ResponseBuilder("op_001", 1)
        builder.add_footer("Test footer")
        
        assert len(builder.segments) == 1
        assert builder.segments[0].segment_type == "footer"
    
    def test_builder_fluent_interface(self):
        """Builder supports fluent/chained calls."""
        builder = (ResponseBuilder("op_001", 1)
                   .add_header("Header")
                   .add_body("Body")
                   .add_footer("Footer"))
        
        assert len(builder.segments) == 3
    
    def test_builder_build(self):
        """Builder can build response."""
        metadata = ResponseMetadata(
            mode=ResponseMode.CHAT,
            tone=ResponseTone.TECHNICAL,
            turn_number=1,
            operation_id="op_001",
            phase="PHASE-24",
            orchestrator="MasterOrchestrator"
        )
        
        builder = (ResponseBuilder("op_001", 1)
                   .add_header("Header")
                   .add_body("Body"))
        
        response = builder.build(metadata)
        
        assert isinstance(response, TurnResponse)
        assert response.operation_id == "op_001"
        assert response.turn_number == 1
        assert response.ready_to_send is True
        assert len(response.segments) == 2

class TestResponseFormatter:
    """Test response formatting for different modes."""
    
    @pytest.fixture
    def sample_response(self):
        """Create a sample response for formatting tests."""
        metadata = ResponseMetadata(
            mode=ResponseMode.CHAT,
            tone=ResponseTone.TECHNICAL,
            turn_number=1,
            operation_id="op_001",
            phase="PHASE-24",
            orchestrator="MasterOrchestrator"
        )
        
        return TurnResponse(
            operation_id="op_001",
            turn_number=1,
            metadata=metadata,
            formatted_content="Test response content",
            alternatives=[
                {"name": "Alt1", "description": "First option"},
            ],
            confidence_score=0.95,
            ready_to_send=True,
        )
    
    def test_format_chat(self, sample_response):
        """Format response for chat interface."""
        formatted = ResponseFormatter.format_chat(sample_response)
        
        assert formatted["type"] == "chat"
        assert formatted["turn"] == 1
        assert formatted["operation"] == "op_001"
        assert "content" in formatted
        assert formatted["confidence"] == 0.95
    
    def test_format_command(self, sample_response):
        """Format response for command line."""
        formatted = ResponseFormatter.format_command(sample_response)
        
        assert isinstance(formatted, str)
        assert "Turn 1" in formatted
        assert "MasterOrchestrator" in formatted
        assert "op_001" in formatted
    
    def test_format_json_api(self, sample_response):
        """Format response for JSON API."""
        formatted = ResponseFormatter.format_json_api(sample_response)
        
        assert "data" in formatted
        assert formatted["data"]["type"] == "response"
        assert "attributes" in formatted["data"]
        assert formatted["data"]["attributes"]["content"] == "Test response content"
    
    def test_format_markdown(self, sample_response):
        """Format response as markdown."""
        formatted = ResponseFormatter.format_markdown(sample_response)
        
        assert isinstance(formatted, str)
        assert "# Turn 1" in formatted
        assert "MasterOrchestrator" in formatted
        assert "Test response content" in formatted

class TestTurnResponseGenerator:
    """Test response generation engine."""
    
    def test_generator_initialization(self):
        """Generator initializes correctly."""
        generator = TurnResponseGenerator()
        
        assert generator.default_mode == ResponseMode.CHAT
        assert generator.default_tone == ResponseTone.TECHNICAL
        assert len(generator.response_cache) == 0
        assert generator.generation_count == 0
    
    def test_generate_response_basic(self):
        """Generate basic response."""
        generator = TurnResponseGenerator()
        
        response = generator.generate_response(
            operation_id="op_001",
            turn_number=1,
            content="Test content",
        )
        
        assert response.operation_id == "op_001"
        assert response.turn_number == 1
        assert response.ready_to_send is True
        assert generator.generation_count == 1
    
    def test_generate_response_with_mode_and_tone(self):
        """Generate response with specific mode and tone."""
        generator = TurnResponseGenerator()
        
        response = generator.generate_response(
            operation_id="op_001",
            turn_number=1,
            content="Test",
            mode=ResponseMode.MARKDOWN,
            tone=ResponseTone.EXECUTIVE,
        )
        
        assert response.metadata.mode == ResponseMode.MARKDOWN
        assert response.metadata.tone == ResponseTone.EXECUTIVE
    
    def test_generate_response_with_alternatives(self):
        """Generate response with alternatives."""
        generator = TurnResponseGenerator()
        
        alternatives = [
            {"name": "Alt1", "description": "Option 1"},
            {"name": "Alt2", "description": "Option 2"},
        ]
        
        response = generator.generate_response(
            operation_id="op_001",
            turn_number=1,
            content="Test",
            alternatives=alternatives,
        )
        
        assert len(response.alternatives) == 2
    
    def test_response_caching(self):
        """Responses are cached."""
        generator = TurnResponseGenerator()
        
        response1 = generator.generate_response(
            operation_id="op_001",
            turn_number=1,
            content="Test",
        )
        
        cached = generator.get_cached_response("op_001", 1)
        
        assert cached is not None
        assert cached.operation_id == "op_001"
    
    def test_format_response_chat(self):
        """Format response for chat."""
        generator = TurnResponseGenerator()
        response = generator.generate_response(
            operation_id="op_001",
            turn_number=1,
            content="Test",
        )
        
        formatted = generator.format_response(response, "chat")
        
        assert isinstance(formatted, dict)
        assert formatted["type"] == "chat"
    
    def test_format_response_command(self):
        """Format response for command."""
        generator = TurnResponseGenerator()
        response = generator.generate_response(
            operation_id="op_001",
            turn_number=1,
            content="Test",
        )
        
        formatted = generator.format_response(response, "command")
        
        assert isinstance(formatted, str)
        assert "Turn 1" in formatted
    
    def test_format_response_json(self):
        """Format response for JSON API."""
        generator = TurnResponseGenerator()
        response = generator.generate_response(
            operation_id="op_001",
            turn_number=1,
            content="Test",
        )
        
        formatted = generator.format_response(response, "json")
        
        assert isinstance(formatted, dict)
        assert "data" in formatted
    
    def test_format_response_markdown(self):
        """Format response as markdown."""
        generator = TurnResponseGenerator()
        response = generator.generate_response(
            operation_id="op_001",
            turn_number=1,
            content="Test",
        )
        
        formatted = generator.format_response(response, "markdown")
        
        assert isinstance(formatted, str)
        assert "# Turn 1" in formatted
    
    def test_clear_cache_all(self):
        """Clear all cached responses."""
        generator = TurnResponseGenerator()
        
        generator.generate_response("op_001", 1, "Test 1")
        generator.generate_response("op_001", 2, "Test 2")
        
        assert len(generator.response_cache) == 2
        
        generator.clear_cache()
        
        assert len(generator.response_cache) == 0
    
    def test_clear_cache_operation(self):
        """Clear cached responses for specific operation."""
        generator = TurnResponseGenerator()
        
        generator.generate_response("op_001", 1, "Test 1")
        generator.generate_response("op_002", 1, "Test 2")
        
        assert len(generator.response_cache) == 2
        
        generator.clear_cache("op_001")
        
        assert len(generator.response_cache) == 1
        assert generator.get_cached_response("op_002", 1) is not None
    
    def test_statistics(self):
        """Get generator statistics."""
        generator = TurnResponseGenerator()
        
        generator.generate_response("op_001", 1, "Test content")
        generator.generate_response("op_001", 2, "More content")
        
        stats = generator.get_statistics()
        
        assert stats["total_generations"] == 2
        assert stats["cached_responses"] == 2
        assert stats["cache_size_bytes"] > 0
