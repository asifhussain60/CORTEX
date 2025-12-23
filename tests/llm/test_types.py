"""
Comprehensive unit tests for LLM types module.

Target Coverage: 90%+ on src/llm/types.py (~75 statements)

Test Organization:
- TestSafetyLevel: Enum validation (6 tests)
- TestLLMGenerationSettings: Dataclass defaults and validation (12 tests)
- TestLLMCaps: Capability structure validation (13 tests)
- TestToolCall: Tool call dataclass (5 tests)
- TestLLMResponse: Response structure validation (10 tests)
- TestLLMErrorHierarchy: Exception types and inheritance (7 tests)
- TestTypeIntegration: Cross-type interactions (5 tests)

Coverage Strategy:
- All enums: SafetyLevel (STRICT, BALANCED, RAW)
- All dataclasses: LLMGenerationSettings, LLMCaps, ToolCall, LLMResponse
- All exception types: LLMError, RateLimitExceeded, ContextTooLarge, ToolSchemaUnsupported, SafetyBlocked, TransportFailure, GracefulTimeout
- All field defaults and constraints
- Type literals: tool_call_support, function_call_format, availability, confidence_state
"""

import pytest
from dataclasses import fields
from enum import Enum

from src.llm.types import (
    SafetyLevel,
    LLMGenerationSettings,
    LLMCaps,
    ToolCall,
    LLMResponse,
    LLMError,
    RateLimitExceeded,
    ContextTooLarge,
    ToolSchemaUnsupported,
    SafetyBlocked,
    TransportFailure,
    GracefulTimeout,
)


# ============================================================================
# Test Class: SafetyLevel Enum (6 tests)
# ============================================================================

class TestSafetyLevel:
    """Test SafetyLevel enum validation."""

    def test_safety_level_is_enum(self):
        """SafetyLevel should be an Enum subclass."""
        assert issubclass(SafetyLevel, Enum)

    def test_safety_level_has_strict(self):
        """Should have STRICT level."""
        assert SafetyLevel.STRICT.value == "strict"

    def test_safety_level_has_balanced(self):
        """Should have BALANCED level."""
        assert SafetyLevel.BALANCED.value == "balanced"

    def test_safety_level_has_raw(self):
        """Should have RAW level."""
        assert SafetyLevel.RAW.value == "raw"

    def test_safety_level_count(self):
        """Should have exactly 3 safety levels."""
        assert len(list(SafetyLevel)) == 3

    def test_safety_level_string_comparison(self):
        """SafetyLevel should support string comparison."""
        assert SafetyLevel.STRICT == "strict"
        assert SafetyLevel.BALANCED == "balanced"
        assert SafetyLevel.RAW == "raw"


# ============================================================================
# Test Class: LLMGenerationSettings (12 tests)
# ============================================================================

class TestLLMGenerationSettings:
    """Test LLMGenerationSettings dataclass defaults and validation."""

    def test_generation_settings_is_dataclass(self):
        """LLMGenerationSettings should be a dataclass."""
        settings = LLMGenerationSettings()
        assert hasattr(settings, "__dataclass_fields__")

    def test_default_temperature(self):
        """Default temperature should be 0.2."""
        settings = LLMGenerationSettings()
        assert settings.temperature == 0.2

    def test_default_max_tokens(self):
        """Default max_tokens should be None."""
        settings = LLMGenerationSettings()
        assert settings.max_tokens is None

    def test_default_top_p(self):
        """Default top_p should be None."""
        settings = LLMGenerationSettings()
        assert settings.top_p is None

    def test_default_top_k(self):
        """Default top_k should be None."""
        settings = LLMGenerationSettings()
        assert settings.top_k is None

    def test_default_presence_penalty(self):
        """Default presence_penalty should be None."""
        settings = LLMGenerationSettings()
        assert settings.presence_penalty is None

    def test_default_frequency_penalty(self):
        """Default frequency_penalty should be None."""
        settings = LLMGenerationSettings()
        assert settings.frequency_penalty is None

    def test_default_json_mode(self):
        """Default json_mode should be False."""
        settings = LLMGenerationSettings()
        assert settings.json_mode is False

    def test_default_streaming(self):
        """Default streaming should be False."""
        settings = LLMGenerationSettings()
        assert settings.streaming is False

    def test_default_safety(self):
        """Default safety should be BALANCED."""
        settings = LLMGenerationSettings()
        assert settings.safety == SafetyLevel.BALANCED

    def test_custom_values(self):
        """Should accept custom values for all fields."""
        settings = LLMGenerationSettings(
            temperature=0.8,
            max_tokens=2000,
            top_p=0.95,
            top_k=50,
            presence_penalty=0.5,
            frequency_penalty=0.3,
            json_mode=True,
            streaming=True,
            safety=SafetyLevel.STRICT,
        )
        assert settings.temperature == 0.8
        assert settings.max_tokens == 2000
        assert settings.top_p == 0.95
        assert settings.top_k == 50
        assert settings.presence_penalty == 0.5
        assert settings.frequency_penalty == 0.3
        assert settings.json_mode is True
        assert settings.streaming is True
        assert settings.safety == SafetyLevel.STRICT

    def test_field_count(self):
        """Should have exactly 9 fields."""
        settings = LLMGenerationSettings()
        field_names = [f.name for f in fields(settings)]
        assert len(field_names) == 9


# ============================================================================
# Test Class: LLMCaps (13 tests)
# ============================================================================

class TestLLMCaps:
    """Test LLMCaps capability structure validation."""

    def test_llm_caps_is_dataclass(self):
        """LLMCaps should be a dataclass."""
        caps = LLMCaps(max_context_tokens=8000, max_output_tokens=2000)
        assert hasattr(caps, "__dataclass_fields__")

    def test_required_context_tokens(self):
        """max_context_tokens is required."""
        caps = LLMCaps(max_context_tokens=128000, max_output_tokens=4096)
        assert caps.max_context_tokens == 128000

    def test_required_output_tokens(self):
        """max_output_tokens is required."""
        caps = LLMCaps(max_context_tokens=8000, max_output_tokens=2048)
        assert caps.max_output_tokens == 2048

    def test_default_tool_call_support(self):
        """Default tool_call_support should be 'none'."""
        caps = LLMCaps(max_context_tokens=8000, max_output_tokens=2000)
        assert caps.tool_call_support == "none"

    def test_default_function_call_format(self):
        """Default function_call_format should be 'none'."""
        caps = LLMCaps(max_context_tokens=8000, max_output_tokens=2000)
        assert caps.function_call_format == "none"

    def test_default_streaming(self):
        """Default streaming should be True."""
        caps = LLMCaps(max_context_tokens=8000, max_output_tokens=2000)
        assert caps.streaming is True

    def test_default_json_mode(self):
        """Default json_mode should be False."""
        caps = LLMCaps(max_context_tokens=8000, max_output_tokens=2000)
        assert caps.json_mode is False

    def test_default_reasoning(self):
        """Default reasoning should be False."""
        caps = LLMCaps(max_context_tokens=8000, max_output_tokens=2000)
        assert caps.reasoning is False

    def test_default_availability(self):
        """Default availability should be 'variable'."""
        caps = LLMCaps(max_context_tokens=8000, max_output_tokens=2000)
        assert caps.availability == "variable"

    def test_tool_call_support_literals(self):
        """tool_call_support should accept valid literals."""
        for support in ["none", "basic", "structured"]:
            caps = LLMCaps(
                max_context_tokens=8000,
                max_output_tokens=2000,
                tool_call_support=support,
            )
            assert caps.tool_call_support == support

    def test_function_call_format_literals(self):
        """function_call_format should accept valid literals."""
        for format in ["openai", "json-in-text", "none"]:
            caps = LLMCaps(
                max_context_tokens=8000,
                max_output_tokens=2000,
                function_call_format=format,
            )
            assert caps.function_call_format == format

    def test_availability_literals(self):
        """availability should accept valid literals."""
        for avail in ["high", "variable", "low"]:
            caps = LLMCaps(
                max_context_tokens=8000,
                max_output_tokens=2000,
                availability=avail,
            )
            assert caps.availability == avail

    def test_custom_values(self):
        """Should accept custom values for all fields."""
        caps = LLMCaps(
            max_context_tokens=200000,
            max_output_tokens=4096,
            tool_call_support="structured",
            function_call_format="openai",
            streaming=True,
            json_mode=True,
            reasoning=True,
            availability="high",
        )
        assert caps.max_context_tokens == 200000
        assert caps.max_output_tokens == 4096
        assert caps.tool_call_support == "structured"
        assert caps.function_call_format == "openai"
        assert caps.streaming is True
        assert caps.json_mode is True
        assert caps.reasoning is True
        assert caps.availability == "high"


# ============================================================================
# Test Class: ToolCall (5 tests)
# ============================================================================

class TestToolCall:
    """Test ToolCall dataclass."""

    def test_tool_call_is_dataclass(self):
        """ToolCall should be a dataclass."""
        tool = ToolCall(name="search", arguments={"query": "test"})
        assert hasattr(tool, "__dataclass_fields__")

    def test_tool_call_name(self):
        """Should store tool name."""
        tool = ToolCall(name="calculate", arguments={})
        assert tool.name == "calculate"

    def test_tool_call_arguments(self):
        """Should store tool arguments as dict."""
        args = {"x": 10, "y": 20, "operation": "add"}
        tool = ToolCall(name="math", arguments=args)
        assert tool.arguments == args
        assert tool.arguments["x"] == 10

    def test_tool_call_empty_arguments(self):
        """Should support empty arguments dict."""
        tool = ToolCall(name="ping", arguments={})
        assert tool.arguments == {}
        assert isinstance(tool.arguments, dict)

    def test_tool_call_nested_arguments(self):
        """Should support nested argument structures."""
        args = {
            "filters": {"status": "active", "type": "user"},
            "sort": {"field": "created_at", "order": "desc"},
            "limit": 100,
        }
        tool = ToolCall(name="query_db", arguments=args)
        assert tool.arguments["filters"]["status"] == "active"
        assert tool.arguments["sort"]["order"] == "desc"


# ============================================================================
# Test Class: LLMResponse (10 tests)
# ============================================================================

class TestLLMResponse:
    """Test LLMResponse structure validation."""

    def test_llm_response_is_dataclass(self):
        """LLMResponse should be a dataclass."""
        response = LLMResponse()
        assert hasattr(response, "__dataclass_fields__")

    def test_default_text(self):
        """Default text should be empty string."""
        response = LLMResponse()
        assert response.text == ""

    def test_default_tool_calls(self):
        """Default tool_calls should be empty list."""
        response = LLMResponse()
        assert response.tool_calls == []
        assert isinstance(response.tool_calls, list)

    def test_default_safety_flags(self):
        """Default safety_flags should be empty dict."""
        response = LLMResponse()
        assert response.safety_flags == {}
        assert isinstance(response.safety_flags, dict)

    def test_default_token_usage(self):
        """Default token_usage should be empty dict."""
        response = LLMResponse()
        assert response.token_usage == {}

    def test_default_latency_ms(self):
        """Default latency_ms should be empty dict."""
        response = LLMResponse()
        assert response.latency_ms == {}

    def test_default_confidence_state(self):
        """Default confidence_state should be 'high'."""
        response = LLMResponse()
        assert response.confidence_state == "high"

    def test_confidence_state_literals(self):
        """confidence_state should accept valid literals."""
        for state in ["high", "degraded", "minimal", "retrieval-only"]:
            response = LLMResponse(confidence_state=state)
            assert response.confidence_state == state

    def test_custom_values(self):
        """Should accept custom values for all fields."""
        tool = ToolCall(name="search", arguments={"q": "test"})
        response = LLMResponse(
            text="Generated response",
            tool_calls=[tool],
            safety_flags={"flagged": False},
            token_usage={"prompt": 10, "completion": 42},
            latency_ms={"total": 150.5},
            confidence_state="degraded",
        )
        assert response.text == "Generated response"
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].name == "search"
        assert response.safety_flags["flagged"] is False
        assert response.token_usage["prompt"] == 10
        assert response.latency_ms["total"] == 150.5
        assert response.confidence_state == "degraded"

    def test_multiple_tool_calls(self):
        """Should support multiple tool calls."""
        tools = [
            ToolCall(name="search", arguments={"q": "A"}),
            ToolCall(name="calculate", arguments={"x": 5}),
            ToolCall(name="store", arguments={"key": "result"}),
        ]
        response = LLMResponse(tool_calls=tools)
        assert len(response.tool_calls) == 3
        assert response.tool_calls[1].name == "calculate"


# ============================================================================
# Test Class: Exception Hierarchy (7 tests)
# ============================================================================

class TestLLMErrorHierarchy:
    """Test LLM exception types and inheritance."""

    def test_llm_error_is_exception(self):
        """LLMError should inherit from Exception."""
        assert issubclass(LLMError, Exception)

    def test_rate_limit_exceeded_inheritance(self):
        """RateLimitExceeded should inherit from LLMError."""
        assert issubclass(RateLimitExceeded, LLMError)
        error = RateLimitExceeded("Rate limit hit")
        assert isinstance(error, LLMError)
        assert isinstance(error, Exception)

    def test_context_too_large_inheritance(self):
        """ContextTooLarge should inherit from LLMError."""
        assert issubclass(ContextTooLarge, LLMError)
        error = ContextTooLarge("Context exceeds 128k")
        assert isinstance(error, LLMError)

    def test_tool_schema_unsupported_inheritance(self):
        """ToolSchemaUnsupported should inherit from LLMError."""
        assert issubclass(ToolSchemaUnsupported, LLMError)
        error = ToolSchemaUnsupported("Tool schema invalid")
        assert isinstance(error, LLMError)

    def test_safety_blocked_inheritance(self):
        """SafetyBlocked should inherit from LLMError."""
        assert issubclass(SafetyBlocked, LLMError)
        error = SafetyBlocked("Content flagged")
        assert isinstance(error, LLMError)

    def test_transport_failure_inheritance(self):
        """TransportFailure should inherit from LLMError."""
        assert issubclass(TransportFailure, LLMError)
        error = TransportFailure("Network error")
        assert isinstance(error, LLMError)

    def test_graceful_timeout_inheritance(self):
        """GracefulTimeout should inherit from LLMError."""
        assert issubclass(GracefulTimeout, LLMError)
        error = GracefulTimeout("Request timeout")
        assert isinstance(error, LLMError)


# ============================================================================
# Test Class: Type Integration (5 tests)
# ============================================================================

class TestTypeIntegration:
    """Test cross-type interactions and usage patterns."""

    def test_generation_settings_with_safety_level(self):
        """LLMGenerationSettings should integrate SafetyLevel enum."""
        settings = LLMGenerationSettings(safety=SafetyLevel.STRICT)
        assert settings.safety == SafetyLevel.STRICT
        assert settings.safety.value == "strict"

    def test_response_with_tool_calls(self):
        """LLMResponse should integrate ToolCall dataclass."""
        tool1 = ToolCall(name="search", arguments={"q": "test"})
        tool2 = ToolCall(name="calculate", arguments={"x": 5})
        response = LLMResponse(tool_calls=[tool1, tool2])
        assert len(response.tool_calls) == 2
        assert all(isinstance(t, ToolCall) for t in response.tool_calls)

    def test_caps_with_all_features(self):
        """LLMCaps should represent full-featured provider."""
        caps = LLMCaps(
            max_context_tokens=200000,
            max_output_tokens=4096,
            tool_call_support="structured",
            function_call_format="openai",
            streaming=True,
            json_mode=True,
            reasoning=True,
            availability="high",
        )
        # Verify all premium features enabled
        assert caps.max_context_tokens > 100000
        assert caps.tool_call_support != "none"
        assert caps.streaming is True
        assert caps.json_mode is True
        assert caps.reasoning is True

    def test_exception_catching_hierarchy(self):
        """Should catch specific errors with base LLMError."""
        try:
            raise RateLimitExceeded("Test error")
        except LLMError as e:
            assert isinstance(e, RateLimitExceeded)
            assert "Test error" in str(e)

    def test_response_complete_structure(self):
        """LLMResponse should represent complete generation result."""
        response = LLMResponse(
            text="Generated text",
            tool_calls=[ToolCall(name="action", arguments={})],
            safety_flags={"inappropriate": False},
            token_usage={"prompt": 100, "completion": 50},
            latency_ms={"total": 200.0, "first_token": 50.0},
            confidence_state="high",
        )
        # Verify all fields populated
        assert response.text != ""
        assert len(response.tool_calls) > 0
        assert "inappropriate" in response.safety_flags
        assert "prompt" in response.token_usage
        assert "total" in response.latency_ms
        assert response.confidence_state in ["high", "degraded", "minimal", "retrieval-only"]


# ============================================================================
# Fixtures (3 test fixtures)
# ============================================================================

@pytest.fixture
def basic_generation_settings():
    """Basic generation settings with defaults."""
    return LLMGenerationSettings()


@pytest.fixture
def full_featured_caps():
    """Full-featured LLM capabilities."""
    return LLMCaps(
        max_context_tokens=200000,
        max_output_tokens=4096,
        tool_call_support="structured",
        function_call_format="openai",
        streaming=True,
        json_mode=True,
        reasoning=True,
        availability="high",
    )


@pytest.fixture
def sample_response():
    """Sample LLMResponse with all fields populated."""
    tool = ToolCall(name="search", arguments={"query": "test"})
    return LLMResponse(
        text="Sample response",
        tool_calls=[tool],
        safety_flags={},
        token_usage={"prompt": 10, "completion": 20},
        latency_ms={"total": 150.0},
        confidence_state="high",
    )


# ============================================================================
# Test Class: Fixture Usage (3 tests)
# ============================================================================

class TestTypeFixtures:
    """Test types using pytest fixtures."""

    def test_basic_generation_settings_fixture(self, basic_generation_settings):
        """Should use basic generation settings fixture."""
        assert basic_generation_settings.temperature == 0.2
        assert basic_generation_settings.safety == SafetyLevel.BALANCED

    def test_full_featured_caps_fixture(self, full_featured_caps):
        """Should use full-featured caps fixture."""
        assert full_featured_caps.max_context_tokens == 200000
        assert full_featured_caps.tool_call_support == "structured"
        assert full_featured_caps.json_mode is True

    def test_sample_response_fixture(self, sample_response):
        """Should use sample response fixture."""
        assert sample_response.text == "Sample response"
        assert len(sample_response.tool_calls) == 1
        assert sample_response.confidence_state == "high"
