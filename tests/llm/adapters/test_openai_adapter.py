"""
Comprehensive unit tests for OpenAIAdapter (GPT integration).

Target Coverage: 85%+ on src/llm/adapters/openai_adapter.py (12 statements)

Test Organization:
- TestOpenAIAdapterInitialization: Constructor and defaults (5 tests)
- TestOpenAIAdapterCapabilities: detect_capabilities() validation (11 tests)
- TestOpenAIAdapterGeneration: generate() method all parameters (11 tests)
- TestOpenAIAdapterTokenUsage: Token counting and scaling (5 tests)
- TestOpenAIAdapterLatency: Response timing metrics (3 tests)
- TestOpenAIAdapterConfidenceState: Confidence state validation (3 tests)
- TestOpenAIAdapterEdgeCases: Empty/long/special prompts (6 tests)
- TestOpenAIAdapterModelVariants: GPT-4, GPT-3.5, custom models (4 tests)
- TestOpenAIAdapterResponseStructure: LLMResponse contract (4 tests)
- TestOpenAIAdapterWithFixtures: Fixture usage patterns (3 tests)

Coverage Strategy:
- All public methods: __init__, detect_capabilities, generate
- All code paths: defaults, custom values, edge cases
- All LLMCaps fields: context tokens, output tokens, tools, streaming, JSON mode
- All LLMResponse fields: text, tool_calls, token_usage, latency_ms, confidence_state
- OpenAI-specific features: 128k context, 4k output, JSON mode, 120.5ms latency, "openai" format
"""

import pytest
from typing import Dict, Optional

from src.llm.adapters.openai_adapter import OpenAIAdapter
from src.llm.types import LLMCaps, LLMGenerationSettings, LLMResponse


# ============================================================================
# Test Class: Initialization (5 tests)
# ============================================================================

class TestOpenAIAdapterInitialization:
    """Test adapter initialization with various configurations."""

    def test_init_with_defaults(self):
        """Should initialize with default model and config."""
        adapter = OpenAIAdapter()
        assert adapter.PROVIDER_NAME == "openai"
        assert adapter.model is None  # No default model specified

    def test_init_with_model(self):
        """Should initialize with custom model name."""
        adapter = OpenAIAdapter(model="gpt-4.1")
        assert adapter.model == "gpt-4.1"

    def test_init_with_config(self):
        """Should initialize with custom config dictionary."""
        config = {"api_key": "sk-test123", "org_id": "org-456"}
        adapter = OpenAIAdapter(config=config)
        assert adapter.config == config
        assert adapter.config["api_key"] == "sk-test123"

    def test_init_with_model_and_config(self):
        """Should initialize with both model and config."""
        config = {"temperature": 0.7}
        adapter = OpenAIAdapter(model="gpt-3.5-turbo", config=config)
        assert adapter.model == "gpt-3.5-turbo"
        assert adapter.config["temperature"] == 0.7

    def test_provider_name_constant(self):
        """Provider name should be 'openai' (lowercase)."""
        adapter = OpenAIAdapter()
        assert adapter.PROVIDER_NAME == "openai"
        assert isinstance(adapter.PROVIDER_NAME, str)


# ============================================================================
# Test Class: Capabilities (11 tests)
# ============================================================================

class TestOpenAIAdapterCapabilities:
    """Test detect_capabilities() returns correct OpenAI specifications."""

    def test_detect_capabilities_returns_correct_type(self):
        """Should return LLMCaps instance."""
        adapter = OpenAIAdapter()
        caps = adapter.detect_capabilities()
        assert isinstance(caps, LLMCaps)

    def test_detect_capabilities_context_tokens(self):
        """OpenAI supports 128k context tokens (GPT-4)."""
        adapter = OpenAIAdapter()
        caps = adapter.detect_capabilities()
        assert caps.max_context_tokens == 128000

    def test_detect_capabilities_output_tokens(self):
        """OpenAI supports 4k output tokens."""
        adapter = OpenAIAdapter()
        caps = adapter.detect_capabilities()
        assert caps.max_output_tokens == 4096

    def test_detect_capabilities_tool_support(self):
        """OpenAI supports structured tool calls."""
        adapter = OpenAIAdapter()
        caps = adapter.detect_capabilities()
        assert caps.tool_call_support == "structured"

    def test_detect_capabilities_function_format(self):
        """OpenAI uses native 'openai' function format."""
        adapter = OpenAIAdapter()
        caps = adapter.detect_capabilities()
        assert caps.function_call_format == "openai"

    def test_detect_capabilities_streaming(self):
        """OpenAI supports streaming responses."""
        adapter = OpenAIAdapter()
        caps = adapter.detect_capabilities()
        assert caps.streaming is True

    def test_detect_capabilities_json_mode(self):
        """OpenAI supports JSON mode (unlike Anthropic)."""
        adapter = OpenAIAdapter()
        caps = adapter.detect_capabilities()
        assert caps.json_mode is True

    def test_detect_capabilities_reasoning(self):
        """OpenAI supports reasoning/chain-of-thought."""
        adapter = OpenAIAdapter()
        caps = adapter.detect_capabilities()
        assert caps.reasoning is True

    def test_detect_capabilities_availability(self):
        """OpenAI has high availability (99.9% uptime)."""
        adapter = OpenAIAdapter()
        caps = adapter.detect_capabilities()
        assert caps.availability == "high"

    def test_capabilities_consistent_across_calls(self):
        """Capabilities should be stable across multiple calls."""
        adapter = OpenAIAdapter()
        caps1 = adapter.detect_capabilities()
        caps2 = adapter.detect_capabilities()
        assert caps1.max_context_tokens == caps2.max_context_tokens
        assert caps1.json_mode == caps2.json_mode


# ============================================================================
# Test Class: Generation (11 tests)
# ============================================================================

class TestOpenAIAdapterGeneration:
    """Test generate() method with all parameter combinations."""

    def test_generate_with_minimal_args(self):
        """Should generate response with only prompt text."""
        adapter = OpenAIAdapter()
        response = adapter.generate(prompt_text="Test prompt")
        assert isinstance(response, LLMResponse)
        assert "Test prompt" in response.text

    def test_generate_includes_model_in_response(self):
        """Response text should include model identifier."""
        adapter = OpenAIAdapter(model="gpt-4.1")
        response = adapter.generate(prompt_text="Hello")
        assert "[openai:gpt-4.1]" in response.text

    def test_generate_with_default_model(self):
        """Should use 'gpt-4.1' when no model specified."""
        adapter = OpenAIAdapter()
        response = adapter.generate(prompt_text="Test")
        # Default fallback in generate() implementation
        assert "[openai:gpt-4.1]" in response.text

    def test_generate_with_custom_model(self):
        """Should use custom model name in response."""
        adapter = OpenAIAdapter(model="gpt-3.5-turbo")
        response = adapter.generate(prompt_text="Query")
        assert "[openai:gpt-3.5-turbo]" in response.text

    def test_generate_with_generation_settings(self):
        """Should accept LLMGenerationSettings parameter."""
        adapter = OpenAIAdapter()
        settings = LLMGenerationSettings(temperature=0.8, top_p=0.9)
        response = adapter.generate(prompt_text="Test", generation=settings)
        assert isinstance(response, LLMResponse)

    def test_generate_with_tools_schema(self):
        """Should accept tools schema dictionary."""
        adapter = OpenAIAdapter()
        tools = [{"name": "search", "parameters": {"query": "string"}}]
        response = adapter.generate(prompt_text="Find X", tools_schema=tools)
        assert isinstance(response, LLMResponse)
        # Tool calls extracted (stub returns empty list)
        assert isinstance(response.tool_calls, list)

    def test_generate_with_system_text(self):
        """Should accept system text parameter."""
        adapter = OpenAIAdapter()
        response = adapter.generate(
            prompt_text="User query",
            system_text="You are a helpful assistant"
        )
        assert isinstance(response, LLMResponse)

    def test_generate_with_all_parameters(self):
        """Should accept all parameters simultaneously."""
        adapter = OpenAIAdapter(model="gpt-4.1")
        settings = LLMGenerationSettings(temperature=0.7)
        tools = [{"name": "tool1"}]
        response = adapter.generate(
            prompt_text="Complex query",
            generation=settings,
            tools_schema=tools,
            system_text="System instructions"
        )
        assert isinstance(response, LLMResponse)
        assert "[openai:gpt-4.1]" in response.text

    def test_generate_truncates_long_prompt_in_response(self):
        """Should truncate prompts longer than 200 characters."""
        adapter = OpenAIAdapter()
        long_prompt = "A" * 300
        response = adapter.generate(prompt_text=long_prompt)
        # Implementation truncates at 200 chars
        assert len(response.text.split("] ")[1]) == 200

    def test_generate_handles_none_generation_settings(self):
        """Should use default settings when generation=None."""
        adapter = OpenAIAdapter()
        response = adapter.generate(prompt_text="Test", generation=None)
        assert isinstance(response, LLMResponse)


# ============================================================================
# Test Class: Token Usage (5 tests)
# ============================================================================

class TestOpenAIAdapterTokenUsage:
    """Test token counting in LLMResponse.token_usage."""

    def test_generate_returns_token_usage(self):
        """Response should include token usage dictionary."""
        adapter = OpenAIAdapter()
        response = adapter.generate(prompt_text="Test prompt")
        assert "token_usage" in dir(response)
        assert isinstance(response.token_usage, dict)

    def test_token_usage_has_prompt_count(self):
        """Token usage should include prompt token count."""
        adapter = OpenAIAdapter()
        response = adapter.generate(prompt_text="Test prompt")
        assert "prompt" in response.token_usage
        assert isinstance(response.token_usage["prompt"], int)

    def test_token_usage_has_completion_count(self):
        """Token usage should include completion token count."""
        adapter = OpenAIAdapter()
        response = adapter.generate(prompt_text="Test")
        assert "completion" in response.token_usage
        assert response.token_usage["completion"] == 42  # Stub value

    def test_token_usage_prompt_scales_with_length(self):
        """Prompt tokens should scale with word count."""
        adapter = OpenAIAdapter()
        short = adapter.generate(prompt_text="Hi")
        long = adapter.generate(prompt_text="This is a longer prompt")
        assert long.token_usage["prompt"] > short.token_usage["prompt"]

    def test_token_usage_completion_fixed(self):
        """Completion tokens should be fixed (stub implementation)."""
        adapter = OpenAIAdapter()
        r1 = adapter.generate(prompt_text="A")
        r2 = adapter.generate(prompt_text="B" * 100)
        assert r1.token_usage["completion"] == r2.token_usage["completion"] == 42


# ============================================================================
# Test Class: Latency (3 tests)
# ============================================================================

class TestOpenAIAdapterLatency:
    """Test response timing metrics in LLMResponse.latency_ms."""

    def test_generate_returns_latency_info(self):
        """Response should include latency information."""
        adapter = OpenAIAdapter()
        response = adapter.generate(prompt_text="Test")
        assert hasattr(response, "latency_ms")
        assert isinstance(response.latency_ms, dict)

    def test_latency_has_total_time(self):
        """Latency should include 'total' key."""
        adapter = OpenAIAdapter()
        response = adapter.generate(prompt_text="Test")
        assert "total" in response.latency_ms

    def test_latency_value_reasonable(self):
        """OpenAI latency should be ~120.5ms (stub value)."""
        adapter = OpenAIAdapter()
        response = adapter.generate(prompt_text="Test")
        assert response.latency_ms["total"] == 120.5


# ============================================================================
# Test Class: Confidence State (3 tests)
# ============================================================================

class TestOpenAIAdapterConfidenceState:
    """Test confidence state in LLMResponse."""

    def test_generate_returns_confidence_state(self):
        """Response should include confidence state."""
        adapter = OpenAIAdapter()
        response = adapter.generate(prompt_text="Test")
        assert hasattr(response, "confidence_state")

    def test_confidence_state_is_high_by_default(self):
        """Confidence state should be 'high' for OpenAI."""
        adapter = OpenAIAdapter()
        response = adapter.generate(prompt_text="Test")
        assert response.confidence_state == "high"

    def test_confidence_state_is_valid_literal(self):
        """Confidence state should be a valid string literal."""
        adapter = OpenAIAdapter()
        response = adapter.generate(prompt_text="Test")
        assert response.confidence_state in ["high", "medium", "low", "unknown"]


# ============================================================================
# Test Class: Edge Cases (6 tests)
# ============================================================================

class TestOpenAIAdapterEdgeCases:
    """Test adapter behavior with unusual inputs."""

    def test_empty_prompt(self):
        """Should handle empty prompt string."""
        adapter = OpenAIAdapter()
        response = adapter.generate(prompt_text="")
        assert isinstance(response, LLMResponse)
        assert response.token_usage["prompt"] == 0  # len("".split()) = 1 word, but empty

    def test_very_long_prompt(self):
        """Should handle prompts approaching context limit."""
        adapter = OpenAIAdapter()
        # 100k characters (~25k tokens)
        long_prompt = "word " * 20000
        response = adapter.generate(prompt_text=long_prompt)
        assert isinstance(response, LLMResponse)
        assert response.token_usage["prompt"] > 10000

    def test_special_characters_in_prompt(self):
        """Should handle special characters without errors."""
        adapter = OpenAIAdapter()
        special = "Test with @#$% & *(){}[]|\\:;\"'<>?/"
        response = adapter.generate(prompt_text=special)
        assert isinstance(response, LLMResponse)

    def test_unicode_in_prompt(self):
        """Should handle Unicode characters (emoji, CJK)."""
        adapter = OpenAIAdapter()
        unicode_text = "Hello 世界 🌍 émojis"
        response = adapter.generate(prompt_text=unicode_text)
        assert isinstance(response, LLMResponse)

    def test_none_values_in_optional_params(self):
        """Should handle explicit None for optional parameters."""
        adapter = OpenAIAdapter()
        response = adapter.generate(
            prompt_text="Test",
            generation=None,
            tools_schema=None,
            system_text=None
        )
        assert isinstance(response, LLMResponse)

    def test_empty_config_dictionary(self):
        """Should handle empty config during initialization."""
        adapter = OpenAIAdapter(config={})
        assert adapter.config == {}
        response = adapter.generate(prompt_text="Test")
        assert isinstance(response, LLMResponse)


# ============================================================================
# Test Class: Model Variants (4 tests)
# ============================================================================

class TestOpenAIAdapterModelVariants:
    """Test different OpenAI model configurations."""

    def test_gpt4_model_variant(self):
        """Should support GPT-4.1 model explicitly."""
        adapter = OpenAIAdapter(model="gpt-4.1")
        response = adapter.generate(prompt_text="Test")
        assert "[openai:gpt-4.1]" in response.text

    def test_gpt35_model_variant(self):
        """Should support GPT-3.5-turbo model."""
        adapter = OpenAIAdapter(model="gpt-3.5-turbo")
        response = adapter.generate(prompt_text="Test")
        assert "[openai:gpt-3.5-turbo]" in response.text

    def test_gpt4_turbo_model_variant(self):
        """Should support GPT-4-turbo model."""
        adapter = OpenAIAdapter(model="gpt-4-turbo")
        response = adapter.generate(prompt_text="Test")
        assert "[openai:gpt-4-turbo]" in response.text

    def test_custom_model_name(self):
        """Should support arbitrary model names (future-proof)."""
        adapter = OpenAIAdapter(model="gpt-5-preview")
        response = adapter.generate(prompt_text="Test")
        assert "[openai:gpt-5-preview]" in response.text


# ============================================================================
# Test Class: Response Structure (4 tests)
# ============================================================================

class TestOpenAIAdapterResponseStructure:
    """Test LLMResponse structure and field validation."""

    def test_response_has_all_required_fields(self):
        """LLMResponse should have text, tool_calls, token_usage, latency_ms, confidence_state."""
        adapter = OpenAIAdapter()
        response = adapter.generate(prompt_text="Test")
        assert hasattr(response, "text")
        assert hasattr(response, "tool_calls")
        assert hasattr(response, "token_usage")
        assert hasattr(response, "latency_ms")
        assert hasattr(response, "confidence_state")

    def test_response_text_is_string(self):
        """Response text field should be a string."""
        adapter = OpenAIAdapter()
        response = adapter.generate(prompt_text="Test")
        assert isinstance(response.text, str)
        assert len(response.text) > 0

    def test_response_tool_calls_is_list(self):
        """Tool calls field should be a list (even if empty)."""
        adapter = OpenAIAdapter()
        response = adapter.generate(prompt_text="Test")
        assert isinstance(response.tool_calls, list)

    def test_response_safety_flags_is_dict(self):
        """Response should have safety_flags as dict (if present)."""
        adapter = OpenAIAdapter()
        response = adapter.generate(prompt_text="Test")
        # Check if safety_flags exists and is dict-like if present
        if hasattr(response, "safety_flags"):
            assert isinstance(response.safety_flags, (dict, type(None)))


# ============================================================================
# Fixtures (3 test fixtures)
# ============================================================================

@pytest.fixture
def basic_openai_adapter():
    """Basic OpenAI adapter with defaults."""
    return OpenAIAdapter()


@pytest.fixture
def configured_openai_adapter():
    """OpenAI adapter with custom configuration."""
    config = {"api_key": "sk-test-key", "timeout": 30}
    return OpenAIAdapter(model="gpt-4.1", config=config)


@pytest.fixture
def generation_settings_balanced():
    """Balanced generation settings for testing."""
    return LLMGenerationSettings(
        temperature=0.7,
        top_p=0.9,
        max_tokens=500,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )


# ============================================================================
# Test Class: Fixture Usage (3 tests)
# ============================================================================

class TestOpenAIAdapterWithFixtures:
    """Test adapter using pytest fixtures for reusability."""

    def test_basic_adapter_fixture(self, basic_openai_adapter):
        """Should use basic adapter fixture correctly."""
        response = basic_openai_adapter.generate(prompt_text="Test")
        assert isinstance(response, LLMResponse)

    def test_configured_adapter_fixture(self, configured_openai_adapter):
        """Should use configured adapter with custom settings."""
        assert configured_openai_adapter.model == "gpt-4.1"
        assert configured_openai_adapter.config["api_key"] == "sk-test-key"

    def test_generation_with_fixture_settings(
        self, basic_openai_adapter, generation_settings_balanced
    ):
        """Should combine adapter and settings fixtures."""
        response = basic_openai_adapter.generate(
            prompt_text="Test",
            generation=generation_settings_balanced
        )
        assert isinstance(response, LLMResponse)
