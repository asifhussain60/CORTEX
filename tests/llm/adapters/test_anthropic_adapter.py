"""
Tests for Anthropic Adapter
Phase 8 Task 8.2 - Week 1 Sprint
Target: 85%+ coverage on src/llm/adapters/anthropic_adapter.py
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Optional

from src.llm.adapters.anthropic_adapter import AnthropicAdapter
from src.llm.types import (
    LLMCaps,
    LLMGenerationSettings,
    LLMResponse,
    SafetyLevel
)


class TestAnthropicAdapterInitialization:
    """Test AnthropicAdapter initialization."""
    
    def test_init_with_defaults(self):
        """Test adapter initialization with no arguments."""
        adapter = AnthropicAdapter()
        
        assert adapter.model is None
        assert adapter.config == {}
        assert adapter.PROVIDER_NAME == "anthropic"
    
    def test_init_with_model(self):
        """Test adapter initialization with specific model."""
        adapter = AnthropicAdapter(model="claude-opus-3")
        
        assert adapter.model == "claude-opus-3"
        assert adapter.config == {}
    
    def test_init_with_config(self):
        """Test adapter initialization with config."""
        config = {"api_key": "test_key", "timeout": 60}
        adapter = AnthropicAdapter(config=config)
        
        assert adapter.model is None
        assert adapter.config["api_key"] == "test_key"
        assert adapter.config["timeout"] == 60
    
    def test_init_with_model_and_config(self):
        """Test adapter initialization with both model and config."""
        config = {"api_key": "sk-test", "max_retries": 5}
        adapter = AnthropicAdapter(model="claude-sonnet-3.5", config=config)
        
        assert adapter.model == "claude-sonnet-3.5"
        assert adapter.config["api_key"] == "sk-test"
        assert adapter.config["max_retries"] == 5
    
    def test_provider_name_constant(self):
        """Test that PROVIDER_NAME is set correctly."""
        adapter = AnthropicAdapter()
        
        assert hasattr(adapter, "PROVIDER_NAME")
        assert adapter.PROVIDER_NAME == "anthropic"
        assert isinstance(adapter.PROVIDER_NAME, str)


class TestAnthropicAdapterCapabilities:
    """Test capability detection for Anthropic."""
    
    def test_detect_capabilities_returns_correct_type(self):
        """Test that detect_capabilities returns LLMCaps object."""
        adapter = AnthropicAdapter()
        caps = adapter.detect_capabilities()
        
        assert isinstance(caps, LLMCaps)
    
    def test_detect_capabilities_context_tokens(self):
        """Test max context tokens capability."""
        adapter = AnthropicAdapter()
        caps = adapter.detect_capabilities()
        
        assert caps.max_context_tokens == 200000
    
    def test_detect_capabilities_output_tokens(self):
        """Test max output tokens capability."""
        adapter = AnthropicAdapter()
        caps = adapter.detect_capabilities()
        
        assert caps.max_output_tokens == 4096
    
    def test_detect_capabilities_tool_support(self):
        """Test tool call support capability."""
        adapter = AnthropicAdapter()
        caps = adapter.detect_capabilities()
        
        assert caps.tool_call_support == "structured"
    
    def test_detect_capabilities_function_format(self):
        """Test function call format capability."""
        adapter = AnthropicAdapter()
        caps = adapter.detect_capabilities()
        
        assert caps.function_call_format == "openai"
    
    def test_detect_capabilities_streaming(self):
        """Test streaming capability."""
        adapter = AnthropicAdapter()
        caps = adapter.detect_capabilities()
        
        assert caps.streaming is True
    
    def test_detect_capabilities_json_mode(self):
        """Test JSON mode capability."""
        adapter = AnthropicAdapter()
        caps = adapter.detect_capabilities()
        
        assert caps.json_mode is False
    
    def test_detect_capabilities_reasoning(self):
        """Test reasoning capability."""
        adapter = AnthropicAdapter()
        caps = adapter.detect_capabilities()
        
        assert caps.reasoning is True
    
    def test_detect_capabilities_availability(self):
        """Test availability rating."""
        adapter = AnthropicAdapter()
        caps = adapter.detect_capabilities()
        
        assert caps.availability == "high"
    
    def test_capabilities_consistent_across_calls(self):
        """Test that capabilities remain consistent across multiple calls."""
        adapter = AnthropicAdapter()
        caps1 = adapter.detect_capabilities()
        caps2 = adapter.detect_capabilities()
        
        assert caps1.max_context_tokens == caps2.max_context_tokens
        assert caps1.max_output_tokens == caps2.max_output_tokens
        assert caps1.tool_call_support == caps2.tool_call_support


class TestAnthropicAdapterGeneration:
    """Test text generation functionality."""
    
    def test_generate_with_minimal_args(self):
        """Test generation with only prompt text."""
        adapter = AnthropicAdapter()
        response = adapter.generate("Hello, Claude!")
        
        assert isinstance(response, LLMResponse)
        assert response.text is not None
        assert len(response.text) > 0
    
    def test_generate_includes_model_in_response(self):
        """Test that response includes model identifier."""
        adapter = AnthropicAdapter(model="claude-3-opus")
        response = adapter.generate("Test prompt")
        
        assert "claude-3-opus" in response.text or "anthropic" in response.text.lower()
    
    def test_generate_with_default_model(self):
        """Test generation when no model specified uses default."""
        adapter = AnthropicAdapter()
        response = adapter.generate("Default model test")
        
        assert "claude-opus" in response.text
    
    def test_generate_with_custom_model(self):
        """Test generation with custom model name."""
        adapter = AnthropicAdapter(model="claude-custom")
        response = adapter.generate("Custom model test")
        
        assert "claude-custom" in response.text
    
    def test_generate_with_generation_settings(self):
        """Test generation with custom settings."""
        adapter = AnthropicAdapter()
        settings = LLMGenerationSettings(
            temperature=0.8,
            max_tokens=500,
            top_p=0.9
        )
        
        response = adapter.generate("Test with settings", generation=settings)
        
        assert isinstance(response, LLMResponse)
        assert response.text is not None
    
    def test_generate_with_tools_schema(self):
        """Test generation with tools schema."""
        adapter = AnthropicAdapter()
        tools = {
            "functions": [
                {"name": "search", "description": "Search the web"}
            ]
        }
        
        response = adapter.generate("Use search tool", tools_schema=tools)
        
        assert isinstance(response, LLMResponse)
    
    def test_generate_with_system_text(self):
        """Test generation with system prompt."""
        adapter = AnthropicAdapter()
        
        response = adapter.generate(
            "User message",
            system_text="You are a helpful AI assistant."
        )
        
        assert isinstance(response, LLMResponse)
    
    def test_generate_with_all_parameters(self):
        """Test generation with all parameters."""
        adapter = AnthropicAdapter(model="claude-sonnet")
        settings = LLMGenerationSettings(temperature=0.7, max_tokens=1000)
        tools = {"functions": []}
        
        response = adapter.generate(
            prompt_text="Complete request",
            generation=settings,
            tools_schema=tools,
            system_text="Be concise"
        )
        
        assert isinstance(response, LLMResponse)
        assert response.text is not None
    
    def test_generate_truncates_long_prompt_in_response(self):
        """Test that very long prompts are truncated in response."""
        adapter = AnthropicAdapter()
        long_prompt = "x" * 1000
        
        response = adapter.generate(long_prompt)
        
        # Response should contain truncated prompt (first 200 chars)
        assert len(response.text) < len(long_prompt) + 50
    
    def test_generate_handles_none_generation_settings(self):
        """Test that None generation settings creates defaults."""
        adapter = AnthropicAdapter()
        response = adapter.generate("test", generation=None)
        
        assert isinstance(response, LLMResponse)


class TestAnthropicAdapterTokenUsage:
    """Test token usage tracking."""
    
    def test_generate_returns_token_usage(self):
        """Test that generation returns token usage."""
        adapter = AnthropicAdapter()
        response = adapter.generate("Count my tokens")
        
        assert response.token_usage is not None
        assert isinstance(response.token_usage, dict)
    
    def test_token_usage_has_prompt_count(self):
        """Test that token usage includes prompt tokens."""
        adapter = AnthropicAdapter()
        response = adapter.generate("Test prompt")
        
        assert "prompt" in response.token_usage
        assert isinstance(response.token_usage["prompt"], int)
        assert response.token_usage["prompt"] > 0
    
    def test_token_usage_has_completion_count(self):
        """Test that token usage includes completion tokens."""
        adapter = AnthropicAdapter()
        response = adapter.generate("Test prompt")
        
        assert "completion" in response.token_usage
        assert isinstance(response.token_usage["completion"], int)
        assert response.token_usage["completion"] > 0
    
    def test_token_usage_prompt_scales_with_length(self):
        """Test that prompt token count scales with prompt length."""
        adapter = AnthropicAdapter()
        
        short_response = adapter.generate("Hi")
        long_response = adapter.generate("This is a much longer prompt with many more words")
        
        assert short_response.token_usage["prompt"] < long_response.token_usage["prompt"]
    
    def test_token_usage_completion_fixed(self):
        """Test that completion token count is consistent (mock response)."""
        adapter = AnthropicAdapter()
        
        response1 = adapter.generate("Test 1")
        response2 = adapter.generate("Test 2")
        
        assert response1.token_usage["completion"] == response2.token_usage["completion"]


class TestAnthropicAdapterLatency:
    """Test latency tracking."""
    
    def test_generate_returns_latency_info(self):
        """Test that generation returns latency information."""
        adapter = AnthropicAdapter()
        response = adapter.generate("Measure latency")
        
        assert response.latency_ms is not None
        assert isinstance(response.latency_ms, dict)
    
    def test_latency_has_total_time(self):
        """Test that latency includes total time."""
        adapter = AnthropicAdapter()
        response = adapter.generate("Test")
        
        assert "total" in response.latency_ms
        assert isinstance(response.latency_ms["total"], float)
        assert response.latency_ms["total"] > 0
    
    def test_latency_value_reasonable(self):
        """Test that latency value is in reasonable range."""
        adapter = AnthropicAdapter()
        response = adapter.generate("Test")
        
        # Mock latency should be around 140ms
        assert response.latency_ms["total"] == 140.0


class TestAnthropicAdapterConfidenceState:
    """Test confidence state tracking."""
    
    def test_generate_returns_confidence_state(self):
        """Test that generation returns confidence state."""
        adapter = AnthropicAdapter()
        response = adapter.generate("Test confidence")
        
        assert response.confidence_state is not None
    
    def test_confidence_state_is_high_by_default(self):
        """Test that default confidence state is high."""
        adapter = AnthropicAdapter()
        response = adapter.generate("Test")
        
        assert response.confidence_state == "high"
    
    def test_confidence_state_is_valid_literal(self):
        """Test that confidence state is one of valid values."""
        adapter = AnthropicAdapter()
        response = adapter.generate("Test")
        
        valid_states = ["high", "degraded", "minimal", "retrieval-only"]
        assert response.confidence_state in valid_states


class TestAnthropicAdapterEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_prompt(self):
        """Test generation with empty prompt."""
        adapter = AnthropicAdapter()
        response = adapter.generate("")
        
        assert isinstance(response, LLMResponse)
        assert response.text is not None
    
    def test_very_long_prompt(self):
        """Test generation with very long prompt."""
        adapter = AnthropicAdapter()
        long_prompt = "word " * 5000
        
        response = adapter.generate(long_prompt)
        
        assert isinstance(response, LLMResponse)
        # Response should truncate prompt to 200 chars
        assert "word" in response.text
    
    def test_special_characters_in_prompt(self):
        """Test generation with special characters."""
        adapter = AnthropicAdapter()
        special_prompt = "Test with: @#$%^&*()[]{}|\\;:'\"<>?/"
        
        response = adapter.generate(special_prompt)
        
        assert isinstance(response, LLMResponse)
    
    def test_unicode_in_prompt(self):
        """Test generation with unicode characters."""
        adapter = AnthropicAdapter()
        unicode_prompt = "Test with unicode: 你好 мир 🌍"
        
        response = adapter.generate(unicode_prompt)
        
        assert isinstance(response, LLMResponse)
    
    def test_none_values_in_optional_params(self):
        """Test that None values are handled for optional parameters."""
        adapter = AnthropicAdapter()
        
        response = adapter.generate(
            "test",
            generation=None,
            tools_schema=None,
            system_text=None
        )
        
        assert isinstance(response, LLMResponse)
    
    def test_multiple_sequential_generations(self):
        """Test multiple sequential generation calls."""
        adapter = AnthropicAdapter()
        
        response1 = adapter.generate("First call")
        response2 = adapter.generate("Second call")
        response3 = adapter.generate("Third call")
        
        assert response1.text != response2.text
        assert response2.text != response3.text
        assert all(isinstance(r, LLMResponse) for r in [response1, response2, response3])


class TestAnthropicAdapterModelVariants:
    """Test different Claude model variants."""
    
    def test_claude_opus_model(self):
        """Test with Claude Opus model."""
        adapter = AnthropicAdapter(model="claude-3-opus-20240229")
        response = adapter.generate("Test")
        
        assert "claude-3-opus-20240229" in response.text
    
    def test_claude_sonnet_model(self):
        """Test with Claude Sonnet model."""
        adapter = AnthropicAdapter(model="claude-3-sonnet")
        response = adapter.generate("Test")
        
        assert "claude-3-sonnet" in response.text
    
    def test_claude_haiku_model(self):
        """Test with Claude Haiku model."""
        adapter = AnthropicAdapter(model="claude-3-haiku")
        response = adapter.generate("Test")
        
        assert "claude-3-haiku" in response.text
    
    def test_custom_model_name(self):
        """Test with custom model name."""
        adapter = AnthropicAdapter(model="claude-custom-v1")
        response = adapter.generate("Test")
        
        assert "claude-custom-v1" in response.text


class TestAnthropicAdapterResponseStructure:
    """Test response structure and completeness."""
    
    def test_response_has_all_required_fields(self):
        """Test that response contains all required fields."""
        adapter = AnthropicAdapter()
        response = adapter.generate("Test")
        
        assert hasattr(response, "text")
        assert hasattr(response, "tool_calls")
        assert hasattr(response, "safety_flags")
        assert hasattr(response, "token_usage")
        assert hasattr(response, "latency_ms")
        assert hasattr(response, "confidence_state")
    
    def test_response_text_is_string(self):
        """Test that response text is a string."""
        adapter = AnthropicAdapter()
        response = adapter.generate("Test")
        
        assert isinstance(response.text, str)
    
    def test_response_tool_calls_is_list(self):
        """Test that tool_calls is a list."""
        adapter = AnthropicAdapter()
        response = adapter.generate("Test")
        
        assert isinstance(response.tool_calls, list)
    
    def test_response_safety_flags_is_dict(self):
        """Test that safety_flags is a dict."""
        adapter = AnthropicAdapter()
        response = adapter.generate("Test")
        
        assert isinstance(response.safety_flags, dict)


# Pytest fixtures
@pytest.fixture
def basic_anthropic_adapter():
    """Fixture providing a basic Anthropic adapter."""
    return AnthropicAdapter()


@pytest.fixture
def configured_anthropic_adapter():
    """Fixture providing a configured Anthropic adapter."""
    config = {
        "api_key": "test_anthropic_key",
        "timeout": 60,
        "max_retries": 3
    }
    return AnthropicAdapter(model="claude-3-opus", config=config)


@pytest.fixture
def generation_settings_balanced():
    """Fixture providing balanced generation settings."""
    return LLMGenerationSettings(
        temperature=0.7,
        max_tokens=2048,
        top_p=0.9,
        safety=SafetyLevel.BALANCED
    )


class TestAnthropicAdapterWithFixtures:
    """Tests using fixtures."""
    
    def test_basic_adapter_fixture(self, basic_anthropic_adapter):
        """Test using basic adapter fixture."""
        response = basic_anthropic_adapter.generate("Test")
        
        assert isinstance(response, LLMResponse)
    
    def test_configured_adapter_fixture(self, configured_anthropic_adapter):
        """Test using configured adapter fixture."""
        assert configured_anthropic_adapter.model == "claude-3-opus"
        assert configured_anthropic_adapter.config["api_key"] == "test_anthropic_key"
    
    def test_generation_with_fixture_settings(
        self,
        basic_anthropic_adapter,
        generation_settings_balanced
    ):
        """Test generation using fixture settings."""
        response = basic_anthropic_adapter.generate(
            "Test with balanced settings",
            generation=generation_settings_balanced
        )
        
        assert isinstance(response, LLMResponse)
        assert response.confidence_state == "high"
