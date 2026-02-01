"""
LLM Provider Factory.

AC-ID: AC-LENS-LLM-001
Factory pattern for creating LLM providers.
Compliance: CORE-011 (Type hints), CORE-012 (Docstrings), SOLID (Factory Pattern)
"""

import os
from typing import Optional, List, Dict, Any

from cortex.brain.llm.i_llm_provider import ILLMProvider
from cortex.brain.llm.openai_provider import OpenAIProvider, OPENAI_AVAILABLE
from cortex.brain.llm.anthropic_provider import AnthropicProvider, ANTHROPIC_AVAILABLE


class LLMFactory:
    """
    Factory for creating LLM providers.
    
    Implements Factory Pattern to abstract provider creation.
    Supports dynamic provider selection based on environment or configuration.
    
    Example:
        >>> provider = LLMFactory.create_provider("openai", api_key="sk-...")
        >>> # Or use environment defaults
        >>> provider = LLMFactory.create_default_provider()
    """
    
    _PROVIDERS: Dict[str, type] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
    }
    
    @classmethod
    def create_provider(
        cls,
        provider_name: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> ILLMProvider:
        """
        Create LLM provider by name.
        
        Args:
            provider_name: Provider name (openai, anthropic, azure)
            api_key: API key (or uses environment variable)
            model: Model name (or uses provider default)
            **kwargs: Provider-specific parameters
        
        Returns:
            ILLMProvider instance
        
        Raises:
            ValueError: If provider name is unknown
            ImportError: If provider package not installed
        """
        provider_name = provider_name.lower()
        
        if provider_name not in cls._PROVIDERS:
            raise ValueError(
                f"Unknown provider: {provider_name}. "
                f"Available: {', '.join(cls._PROVIDERS.keys())}"
            )
        
        provider_class = cls._PROVIDERS[provider_name]
        
        # Build kwargs for provider initialization
        init_kwargs = {}
        if api_key:
            init_kwargs["api_key"] = api_key
        if model:
            init_kwargs["model"] = model
        init_kwargs.update(kwargs)
        
        try:
            return provider_class(**init_kwargs)
        except ImportError as e:
            raise ImportError(
                f"Provider '{provider_name}' requires additional packages. "
                f"Install with: pip install {provider_name}"
            ) from e
    
    @classmethod
    def create_default_provider(
        cls,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> ILLMProvider:
        """
        Create default LLM provider from environment.
        
        Reads DEFAULT_LLM_PROVIDER and DEFAULT_LLM_MODEL from environment.
        Falls back to openai/gpt-4o-mini if not set.
        
        Args:
            api_key: API key (or uses environment variable)
            model: Model name (or uses environment variable)
        
        Returns:
            ILLMProvider instance
        """
        provider_name = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
        model = model or os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")
        
        return cls.create_provider(
            provider_name=provider_name,
            api_key=api_key,
            model=model
        )
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """
        Get list of available LLM providers.
        
        Only returns providers whose packages are installed.
        
        Returns:
            List of provider names
        """
        available = []
        
        if OPENAI_AVAILABLE:
            available.append("openai")
        if ANTHROPIC_AVAILABLE:
            available.append("anthropic")
        
        return available
    
    @classmethod
    def register_provider(
        cls,
        name: str,
        provider_class: type
    ) -> None:
        """
        Register custom LLM provider.
        
        Allows extending factory with custom providers.
        
        Args:
            name: Provider name
            provider_class: Provider class (must implement ILLMProvider)
        
        Raises:
            ValueError: If provider doesn't implement ILLMProvider
        """
        if not issubclass(provider_class, ILLMProvider):
            raise ValueError(
                f"Provider class must implement ILLMProvider interface"
            )
        
        cls._PROVIDERS[name.lower()] = provider_class
