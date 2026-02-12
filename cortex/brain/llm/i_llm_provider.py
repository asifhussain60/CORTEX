"""
LLM Provider Interface.

AC-ID: AC-LENS-LLM-001
Defines interface for LLM providers (OpenAI, Anthropic, Azure OpenAI).
Compliance: CORE-011 (Type hints), CORE-012 (Docstrings), SOLID (D - Dependency Inversion)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class LLMUsage:
    """Token usage information for LLM call."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    @property
    def cost_estimate_usd(self) -> float:
        """Estimate cost in USD (rough estimate based on GPT-4 pricing)."""
        # GPT-4: ~$0.03/1K prompt tokens, ~$0.06/1K completion tokens
        prompt_cost = (self.prompt_tokens / 1000) * 0.03
        completion_cost = (self.completion_tokens / 1000) * 0.06
        return prompt_cost + completion_cost


@dataclass
class LLMResponse:
    """Response from LLM provider."""
    content: str
    usage: LLMUsage
    model: str
    provider: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize metadata if None."""
        if self.metadata is None:
            self.metadata = {}


class ILLMProvider(ABC):
    """
    Interface for LLM providers.

    SOLID: Dependency Inversion Principle - depend on abstraction, not concrete implementation.
    Allows swapping OpenAI ↔ Anthropic ↔ Azure OpenAI without changing consumer code.

    Example:
        >>> provider = LLMFactory.create_provider("openai", api_key="sk-...")
        >>> response = provider.generate("Explain this code", max_tokens=100)
        >>> print(response.content)
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        timeout: int = 30,
        **kwargs
    ) -> LLMResponse:
        """
        Generate text from prompt.

        Args:
            prompt: Input prompt for LLM
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
            timeout: Timeout in seconds
            **kwargs: Provider-specific parameters

        Returns:
            LLMResponse with content, usage, model, provider

        Raises:
            TimeoutError: If request exceeds timeout
            ValueError: If parameters are invalid
            Exception: Provider-specific errors
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get provider name (openai, anthropic, azure)."""
        pass

    @abstractmethod
    def get_model(self) -> str:
        """Get model name being used."""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate provider configuration.

        Returns:
            True if configuration is valid (API key present, model supported)
        """
        pass
