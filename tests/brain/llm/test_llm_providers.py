"""
Tests for LLM Provider Abstraction Layer.

AC-ID: AC-LENS-LLM-001
TDD: CORE-008 (Tests created first)
Coverage: ILLMProvider, OpenAIProvider, AnthropicProvider, LLMFactory
"""

import pytest
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

from cortex.brain.llm.i_llm_provider import ILLMProvider, LLMResponse, LLMUsage
from cortex.brain.llm.openai_provider import OpenAIProvider
from cortex.brain.llm.anthropic_provider import AnthropicProvider
from cortex.brain.llm.llm_factory import LLMFactory


class TestILLMProvider:
    """Test LLM provider interface."""
    
    def test_interface_defines_required_methods(self):
        """Test that interface defines all required methods."""
        required_methods = ['generate', 'get_name', 'get_model', 'validate_config']
        
        for method in required_methods:
            assert hasattr(ILLMProvider, method)
    
    def test_llm_response_structure(self):
        """Test LLMResponse dataclass structure."""
        response = LLMResponse(
            content="Test response",
            usage=LLMUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
            model="gpt-4",
            provider="openai"
        )
        
        assert response.content == "Test response"
        assert response.usage.prompt_tokens == 10
        assert response.usage.total_tokens == 30
        assert response.model == "gpt-4"
        assert response.provider == "openai"


class TestOpenAIProvider:
    """Test OpenAI provider implementation."""
    
    @patch('cortex.brain.llm.openai_provider.OpenAI')
    def test_provider_initialization_with_api_key(self, mock_openai_class):
        """Test provider initializes with API key."""
        provider = OpenAIProvider(api_key="test-key", model="gpt-4")
        
        assert provider.get_name() == "openai"
        assert provider.get_model() == "gpt-4"
        mock_openai_class.assert_called_once()
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'env-key'})
    @patch('cortex.brain.llm.openai_provider.OpenAI')
    def test_provider_initialization_from_env(self, mock_openai_class):
        """Test provider initializes from environment variable."""
        provider = OpenAIProvider(model="gpt-4")
        
        assert provider.get_name() == "openai"
        mock_openai_class.assert_called_once()
    
    def test_provider_fails_without_api_key(self):
        """Test provider raises error without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="API key required"):
                OpenAIProvider()
    
    @patch('cortex.brain.llm.openai_provider.OpenAI')
    def test_generate_success(self, mock_openai_class):
        """Test successful text generation."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Generated text"))]
        mock_response.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
        mock_response.model = "gpt-4"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test
        provider = OpenAIProvider(api_key="test-key")
        response = provider.generate(
            prompt="Test prompt",
            max_tokens=100,
            temperature=0.7
        )
        
        assert response.content == "Generated text"
        assert response.usage.prompt_tokens == 10
        assert response.usage.completion_tokens == 20
        assert response.model == "gpt-4"
        assert response.provider == "openai"
    
    @patch('cortex.brain.llm.openai_provider.OpenAI')
    def test_generate_with_timeout(self, mock_openai_class):
        """Test generation with timeout handling."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Simulate timeout
        import openai
        mock_client.chat.completions.create.side_effect = openai.APITimeoutError("Timeout")
        
        provider = OpenAIProvider(api_key="test-key")
        
        with pytest.raises(TimeoutError):
            provider.generate("Test prompt", timeout=5)
    
    @patch('cortex.brain.llm.openai_provider.OpenAI')
    def test_generate_with_rate_limit(self, mock_openai_class):
        """Test generation with rate limit handling."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Simulate rate limit
        import openai
        mock_client.chat.completions.create.side_effect = openai.RateLimitError("Rate limit")
        
        provider = OpenAIProvider(api_key="test-key")
        
        with pytest.raises(Exception, match="Rate limit"):
            provider.generate("Test prompt")


class TestAnthropicProvider:
    """Test Anthropic provider implementation."""
    
    @patch('cortex.brain.llm.anthropic_provider.Anthropic')
    def test_provider_initialization(self, mock_anthropic_class):
        """Test Anthropic provider initializes correctly."""
        provider = AnthropicProvider(api_key="test-key", model="claude-3-opus-20240229")
        
        assert provider.get_name() == "anthropic"
        assert provider.get_model() == "claude-3-opus-20240229"
        mock_anthropic_class.assert_called_once()
    
    @patch('cortex.brain.llm.anthropic_provider.Anthropic')
    def test_generate_success(self, mock_anthropic_class):
        """Test successful text generation with Anthropic."""
        # Setup mock
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Generated text from Claude")]
        mock_response.usage = MagicMock(
            input_tokens=15,
            output_tokens=25
        )
        mock_response.model = "claude-3-opus-20240229"
        mock_client.messages.create.return_value = mock_response
        
        # Test
        provider = AnthropicProvider(api_key="test-key")
        response = provider.generate(
            prompt="Test prompt",
            max_tokens=100
        )
        
        assert response.content == "Generated text from Claude"
        assert response.usage.prompt_tokens == 15
        assert response.usage.completion_tokens == 25
        assert response.model == "claude-3-opus-20240229"
        assert response.provider == "anthropic"


class TestLLMFactory:
    """Test LLM provider factory."""
    
    @patch('cortex.brain.llm.llm_factory.OpenAIProvider')
    def test_create_openai_provider(self, mock_provider_class):
        """Test factory creates OpenAI provider."""
        mock_provider = Mock()
        mock_provider_class.return_value = mock_provider
        
        provider = LLMFactory.create_provider(
            provider_name="openai",
            api_key="test-key",
            model="gpt-4"
        )
        
        assert provider == mock_provider
        mock_provider_class.assert_called_once_with(
            api_key="test-key",
            model="gpt-4"
        )
    
    @patch('cortex.brain.llm.llm_factory.AnthropicProvider')
    def test_create_anthropic_provider(self, mock_provider_class):
        """Test factory creates Anthropic provider."""
        mock_provider = Mock()
        mock_provider_class.return_value = mock_provider
        
        provider = LLMFactory.create_provider(
            provider_name="anthropic",
            api_key="test-key",
            model="claude-3-opus-20240229"
        )
        
        assert provider == mock_provider
    
    def test_create_invalid_provider(self):
        """Test factory raises error for invalid provider."""
        with pytest.raises(ValueError, match="Unknown provider"):
            LLMFactory.create_provider(
                provider_name="invalid_provider",
                api_key="test-key"
            )
    
    @patch.dict('os.environ', {'DEFAULT_LLM_PROVIDER': 'openai'})
    @patch('cortex.brain.llm.llm_factory.OpenAIProvider')
    def test_create_default_provider(self, mock_provider_class):
        """Test factory creates default provider from environment."""
        mock_provider = Mock()
        mock_provider_class.return_value = mock_provider
        
        provider = LLMFactory.create_default_provider(api_key="test-key")
        
        assert provider == mock_provider
    
    def test_get_available_providers(self):
        """Test factory returns list of available providers."""
        providers = LLMFactory.get_available_providers()
        
        assert "openai" in providers
        assert "anthropic" in providers
        assert len(providers) >= 2
