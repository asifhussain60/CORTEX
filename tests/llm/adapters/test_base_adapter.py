"""
Tests for LLM Base Adapter
Phase 8 Task 8.2 - Week 1 Sprint
Target: 85%+ coverage on src/llm/adapters/base.py
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Optional

from src.llm.adapters.base import LLMProviderAdapter
from src.llm.types import LLMCaps, LLMGenerationSettings, LLMResponse


# Concrete implementation for testing abstract base
class TestLLMAdapter(LLMProviderAdapter):
    """Concrete test implementation of LLMProviderAdapter."""
    
    def detect_capabilities(self) -> LLMCaps:
        """Test implementation returning mock capabilities."""
        return LLMCaps(
            max_context_tokens=4096,
            max_output_tokens=2048,
            tool_call_support="basic",
            function_call_format="openai",
            streaming=True,
            json_mode=True,
            reasoning=False,
            availability="high"
        )
    
    def generate(
        self,
        prompt_text: str,
        generation: Optional[LLMGenerationSettings] = None,
        tools_schema: Optional[Dict] = None,
        system_text: Optional[str] = None,
    ) -> LLMResponse:
        """Test implementation returning mock response."""
        return LLMResponse(
            text=f"Test response to: {prompt_text[:50]}",
            token_usage={"prompt": 10, "completion": 20},
            latency_ms={"total": 100.0},
            confidence_state="high"
        )


class TestLLMProviderAdapterInitialization:
    """Test LLMProviderAdapter initialization."""
    
    def test_init_with_defaults(self):
        """Test adapter initialization with no arguments."""
        adapter = TestLLMAdapter()
        
        assert adapter.model is None
        assert adapter.config == {}
    
    def test_init_with_model_only(self):
        """Test adapter initialization with model specified."""
        adapter = TestLLMAdapter(model="test-model-v1")
        
        assert adapter.model == "test-model-v1"
        assert adapter.config == {}
    
    def test_init_with_config_only(self):
        """Test adapter initialization with config specified."""
        config = {"api_key": "test_key", "timeout": 30}
        adapter = TestLLMAdapter(config=config)
        
        assert adapter.model is None
        assert adapter.config == {"api_key": "test_key", "timeout": 30}
    
    def test_init_with_both_model_and_config(self):
        """Test adapter initialization with both model and config."""
        config = {"api_key": "test_key", "temperature": 0.7}
        adapter = TestLLMAdapter(model="gpt-4", config=config)
        
        assert adapter.model == "gpt-4"
        assert adapter.config == {"api_key": "test_key", "temperature": 0.7}
    
    def test_init_with_empty_config(self):
        """Test adapter initialization with empty config dict."""
        adapter = TestLLMAdapter(config={})
        
        assert adapter.model is None
        assert adapter.config == {}
    
    def test_init_with_none_config(self):
        """Test adapter initialization with None config (should default to empty dict)."""
        adapter = TestLLMAdapter(model="test-model", config=None)
        
        assert adapter.model == "test-model"
        assert adapter.config == {}


class TestLLMProviderAdapterAbstractMethods:
    """Test abstract method enforcement."""
    
    def test_detect_capabilities_is_abstract(self):
        """Test that detect_capabilities must be implemented."""
        # Create a class that doesn't implement detect_capabilities
        class IncompleteAdapter(LLMProviderAdapter):
            def generate(self, prompt_text, generation=None, tools_schema=None, system_text=None):
                return LLMResponse(text="test")
        
        # Should not be able to instantiate
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteAdapter()
    
    def test_generate_is_abstract(self):
        """Test that generate must be implemented."""
        # Create a class that doesn't implement generate
        class IncompleteAdapter(LLMProviderAdapter):
            def detect_capabilities(self):
                return LLMCaps(
                    max_context_tokens=4096,
                    max_output_tokens=2048
                )
        
        # Should not be able to instantiate
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteAdapter()
    
    def test_both_methods_required(self):
        """Test that both abstract methods must be implemented."""
        class IncompleteAdapter(LLMProviderAdapter):
            pass
        
        # Should not be able to instantiate without implementing both methods
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteAdapter()


class TestLLMProviderAdapterCapabilities:
    """Test capability detection."""
    
    def test_detect_capabilities_returns_correct_type(self):
        """Test that detect_capabilities returns LLMCaps object."""
        adapter = TestLLMAdapter()
        caps = adapter.detect_capabilities()
        
        assert isinstance(caps, LLMCaps)
    
    def test_detect_capabilities_has_required_fields(self):
        """Test that capabilities contain all required fields."""
        adapter = TestLLMAdapter()
        caps = adapter.detect_capabilities()
        
        assert hasattr(caps, "max_context_tokens")
        assert hasattr(caps, "max_output_tokens")
        assert hasattr(caps, "tool_call_support")
        assert hasattr(caps, "streaming")
    
    def test_detect_capabilities_values(self):
        """Test specific capability values."""
        adapter = TestLLMAdapter()
        caps = adapter.detect_capabilities()
        
        assert caps.max_context_tokens == 4096
        assert caps.max_output_tokens == 2048
        assert caps.tool_call_support == "basic"
        assert caps.streaming is True


class TestLLMProviderAdapterGeneration:
    """Test text generation functionality."""
    
    def test_generate_with_minimal_args(self):
        """Test generation with only prompt text."""
        adapter = TestLLMAdapter()
        response = adapter.generate("Hello, world!")
        
        assert isinstance(response, LLMResponse)
        assert "Hello, world!" in response.text
    
    def test_generate_with_generation_settings(self):
        """Test generation with custom settings."""
        adapter = TestLLMAdapter()
        settings = LLMGenerationSettings(temperature=0.8, max_tokens=100)
        
        response = adapter.generate("Test prompt", generation=settings)
        
        assert isinstance(response, LLMResponse)
        assert response.text is not None
    
    def test_generate_with_tools_schema(self):
        """Test generation with tools schema."""
        adapter = TestLLMAdapter()
        tools = {"function": {"name": "test_tool"}}
        
        response = adapter.generate("Use tool", tools_schema=tools)
        
        assert isinstance(response, LLMResponse)
    
    def test_generate_with_system_text(self):
        """Test generation with system prompt."""
        adapter = TestLLMAdapter()
        
        response = adapter.generate(
            "User message",
            system_text="You are a helpful assistant"
        )
        
        assert isinstance(response, LLMResponse)
    
    def test_generate_with_all_parameters(self):
        """Test generation with all parameters specified."""
        adapter = TestLLMAdapter()
        settings = LLMGenerationSettings(temperature=0.7)
        tools = {"functions": []}
        
        response = adapter.generate(
            prompt_text="Complete prompt",
            generation=settings,
            tools_schema=tools,
            system_text="System instructions"
        )
        
        assert isinstance(response, LLMResponse)
        assert response.text is not None
        assert "token_usage" in response.__dict__
    
    def test_generate_returns_token_usage(self):
        """Test that generation returns token usage information."""
        adapter = TestLLMAdapter()
        response = adapter.generate("Count tokens")
        
        assert response.token_usage is not None
        assert "prompt" in response.token_usage
        assert "completion" in response.token_usage
    
    def test_generate_returns_latency_info(self):
        """Test that generation returns latency information."""
        adapter = TestLLMAdapter()
        response = adapter.generate("Measure latency")
        
        assert response.latency_ms is not None
        assert "total" in response.latency_ms


class TestLLMProviderAdapterConfigAccess:
    """Test config and model access patterns."""
    
    def test_config_is_mutable(self):
        """Test that config can be modified after initialization."""
        adapter = TestLLMAdapter()
        adapter.config["new_key"] = "new_value"
        
        assert adapter.config["new_key"] == "new_value"
    
    def test_model_is_mutable(self):
        """Test that model can be changed after initialization."""
        adapter = TestLLMAdapter(model="model-v1")
        adapter.model = "model-v2"
        
        assert adapter.model == "model-v2"
    
    def test_config_persists_across_calls(self):
        """Test that config is maintained across method calls."""
        config = {"api_key": "secret", "retries": 3}
        adapter = TestLLMAdapter(config=config)
        
        # Call generate
        adapter.generate("test")
        
        # Config should still be intact
        assert adapter.config["api_key"] == "secret"
        assert adapter.config["retries"] == 3


class TestLLMProviderAdapterEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_prompt(self):
        """Test generation with empty prompt."""
        adapter = TestLLMAdapter()
        response = adapter.generate("")
        
        assert isinstance(response, LLMResponse)
    
    def test_very_long_prompt(self):
        """Test generation with very long prompt."""
        adapter = TestLLMAdapter()
        long_prompt = "x" * 10000
        
        response = adapter.generate(long_prompt)
        
        assert isinstance(response, LLMResponse)
    
    def test_none_generation_settings(self):
        """Test that None generation settings are handled."""
        adapter = TestLLMAdapter()
        response = adapter.generate("test", generation=None)
        
        assert isinstance(response, LLMResponse)
    
    def test_none_tools_schema(self):
        """Test that None tools schema is handled."""
        adapter = TestLLMAdapter()
        response = adapter.generate("test", tools_schema=None)
        
        assert isinstance(response, LLMResponse)
    
    def test_none_system_text(self):
        """Test that None system text is handled."""
        adapter = TestLLMAdapter()
        response = adapter.generate("test", system_text=None)
        
        assert isinstance(response, LLMResponse)


class TestLLMProviderAdapterInheritance:
    """Test inheritance and polymorphism."""
    
    def test_adapter_is_abc_subclass(self):
        """Test that adapter properly inherits from ABC."""
        from abc import ABC
        
        assert issubclass(LLMProviderAdapter, ABC)
    
    def test_concrete_adapter_is_provider_adapter(self):
        """Test that concrete implementation is instance of base."""
        adapter = TestLLMAdapter()
        
        assert isinstance(adapter, LLMProviderAdapter)
    
    def test_multiple_concrete_adapters_independent(self):
        """Test that multiple adapter instances are independent."""
        adapter1 = TestLLMAdapter(model="model-1")
        adapter2 = TestLLMAdapter(model="model-2")
        
        assert adapter1.model == "model-1"
        assert adapter2.model == "model-2"
        
        adapter1.config["key"] = "value1"
        adapter2.config["key"] = "value2"
        
        assert adapter1.config["key"] == "value1"
        assert adapter2.config["key"] == "value2"


# Pytest fixtures for common test data
@pytest.fixture
def basic_adapter():
    """Fixture providing a basic test adapter."""
    return TestLLMAdapter()


@pytest.fixture
def configured_adapter():
    """Fixture providing a configured test adapter."""
    config = {
        "api_key": "test_api_key",
        "timeout": 30,
        "max_retries": 3
    }
    return TestLLMAdapter(model="test-model-v1", config=config)


@pytest.fixture
def generation_settings():
    """Fixture providing test generation settings."""
    return LLMGenerationSettings(
        temperature=0.7,
        max_tokens=1000,
        top_p=0.9,
        json_mode=True
    )


class TestLLMProviderAdapterWithFixtures:
    """Tests using fixtures."""
    
    def test_basic_adapter_fixture(self, basic_adapter):
        """Test using basic adapter fixture."""
        assert basic_adapter.model is None
        assert basic_adapter.config == {}
    
    def test_configured_adapter_fixture(self, configured_adapter):
        """Test using configured adapter fixture."""
        assert configured_adapter.model == "test-model-v1"
        assert configured_adapter.config["api_key"] == "test_api_key"
    
    def test_generation_with_fixture_settings(self, basic_adapter, generation_settings):
        """Test generation using fixture settings."""
        response = basic_adapter.generate("test", generation=generation_settings)
        
        assert isinstance(response, LLMResponse)
        assert response.text is not None
