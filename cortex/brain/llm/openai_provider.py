"""
OpenAI LLM Provider Implementation.

AC-ID: AC-LENS-LLM-001
Implements ILLMProvider for OpenAI API (GPT-4, GPT-4o, GPT-3.5).
Compliance: CORE-011 (Type hints), CORE-012 (Docstrings), CORE-013 (Specific exceptions)
PHASE 3: Integrated with Prometheus metrics for observability.
"""

import os
import time
from typing import Optional, Dict, Any

try:
    from openai import OpenAI
    from openai import APITimeoutError, RateLimitError, APIError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from cortex.brain.llm.i_llm_provider import ILLMProvider, LLMResponse, LLMUsage

# PHASE 3: Import observability metrics
try:
    from cortex.observability.llm_metrics import record_llm_call, record_llm_error
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    def record_llm_call(*args, **kwargs):
        pass
    def record_llm_error(*args, **kwargs):
        pass


class OpenAIProvider(ILLMProvider):
    """
    OpenAI LLM provider implementation.
    
    Supports: GPT-4, GPT-4o, GPT-4-turbo, GPT-3.5-turbo
    
    Example:
        >>> provider = OpenAIProvider(api_key="sk-...", model="gpt-4")
        >>> response = provider.generate("Analyze this code", max_tokens=500)
        >>> print(f"Cost: ${response.usage.cost_estimate_usd:.4f}")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        base_url: Optional[str] = None
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: Model to use (default: gpt-4o-mini for cost efficiency)
            base_url: Optional custom base URL (for Azure OpenAI)
        
        Raises:
            ValueError: If API key is missing
            ImportError: If openai package not installed
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "openai package not installed. Install with: pip install openai"
            )
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.model = model
        self.base_url = base_url
        self.client = OpenAI(api_key=self.api_key, base_url=base_url)
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        timeout: int = 30,
        **kwargs
    ) -> LLMResponse:
        """
        Generate text using OpenAI API.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-2.0)
            timeout: Request timeout in seconds
            **kwargs: Additional OpenAI parameters
        
        Returns:
            LLMResponse with generated text and usage info
        
        Raises:
            TimeoutError: If request times out
            ValueError: If parameters are invalid
            Exception: For other API errors
        """
        start_time = time.time()
        status = "success"
        error_type = None
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
                **kwargs
            )
            
            content = response.choices[0].message.content
            usage = LLMUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )
            
            # PHASE 3: Record metrics
            latency = time.time() - start_time
            record_llm_call(
                provider="openai",
                model=self.model,
                tier="unknown",  # Tier will be set by analyzer
                status=status,
                latency_seconds=latency,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                cost_usd=usage.cost_estimate_usd
            )
            
            return LLMResponse(
                content=content,
                usage=usage,
                model=response.model,
                provider="openai",
                metadata={"finish_reason": response.choices[0].finish_reason}
            )
            
        except APITimeoutError as e:
            status = "error"
            error_type = "timeout"
            record_llm_error("openai", error_type)
            raise TimeoutError(f"OpenAI request timed out after {timeout}s") from e
        except RateLimitError as e:
            status = "error"
            error_type = "rate_limit"
            record_llm_error("openai", error_type)
            raise Exception(f"Rate limit exceeded: {str(e)}") from e
        except APIError as e:
            status = "error"
            error_type = "api_error"
            record_llm_error("openai", error_type)
            raise Exception(f"OpenAI API error: {str(e)}") from e
        except Exception as e:
            status = "error"
            error_type = "unknown"
            record_llm_error("openai", error_type)
            raise Exception(f"Unexpected error calling OpenAI: {str(e)}") from e
    
    def get_name(self) -> str:
        """Get provider name."""
        return "openai"
    
    def get_model(self) -> str:
        """Get current model name."""
        return self.model
    
    def validate_config(self) -> bool:
        """
        Validate OpenAI configuration.
        
        Returns:
            True if API key is present and model is supported
        """
        if not self.api_key:
            return False
        
        supported_models = [
            "gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini",
            "gpt-3.5-turbo", "gpt-3.5-turbo-16k"
        ]
        
        # Check if model starts with any supported model name
        return any(self.model.startswith(m) for m in supported_models)
