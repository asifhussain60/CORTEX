"""
Anthropic LLM Provider Implementation.

AC-ID: AC-LENS-LLM-001
Implements ILLMProvider for Anthropic Claude API.
Compliance: CORE-011 (Type hints), CORE-012 (Docstrings), CORE-013 (Specific exceptions)
PHASE 3: Integrated with Prometheus metrics for observability.
"""

import os
import time
from typing import Optional

try:
    from anthropic import Anthropic, APITimeoutError, RateLimitError, APIError
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

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


class AnthropicProvider(ILLMProvider):
    """
    Anthropic Claude LLM provider implementation.
    
    Supports: Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku
    
    Example:
        >>> provider = AnthropicProvider(api_key="sk-ant-...", model="claude-3-opus-20240229")
        >>> response = provider.generate("Analyze this code", max_tokens=500)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022"
    ):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            model: Model to use (default: claude-3-5-sonnet)
        
        Raises:
            ValueError: If API key is missing
            ImportError: If anthropic package not installed
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic package not installed. Install with: pip install anthropic"
            )
        
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.model = model
        self.client = Anthropic(api_key=self.api_key)
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        timeout: int = 30,
        **kwargs
    ) -> LLMResponse:
        """
        Generate text using Anthropic API.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-1.0)
            timeout: Request timeout in seconds
            **kwargs: Additional Anthropic parameters
        
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
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                timeout=timeout,
                **kwargs
            )
            
            content = response.content[0].text
            usage = LLMUsage(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens
            )
            
            # PHASE 3: Record metrics
            latency = time.time() - start_time
            record_llm_call(
                provider="anthropic",
                model=self.model,
                tier="unknown",
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
                provider="anthropic",
                metadata={"stop_reason": response.stop_reason}
            )
            
        except APITimeoutError as e:
            status = "error"
            error_type = "timeout"
            record_llm_error("anthropic", error_type)
            raise TimeoutError(f"Anthropic request timed out after {timeout}s") from e
        except RateLimitError as e:
            status = "error"
            error_type = "rate_limit"
            record_llm_error("anthropic", error_type)
            raise Exception(f"Rate limit exceeded: {str(e)}") from e
        except APIError as e:
            status = "error"
            error_type = "api_error"
            record_llm_error("anthropic", error_type)
            raise Exception(f"Anthropic API error: {str(e)}") from e
        except Exception as e:
            status = "error"
            error_type = "unknown"
            record_llm_error("anthropic", error_type)
            raise Exception(f"Unexpected error calling Anthropic: {str(e)}") from e
    
    def get_name(self) -> str:
        """Get provider name."""
        return "anthropic"
    
    def get_model(self) -> str:
        """Get current model name."""
        return self.model
    
    def validate_config(self) -> bool:
        """
        Validate Anthropic configuration.
        
        Returns:
            True if API key is present and model is supported
        """
        if not self.api_key:
            return False
        
        supported_models = [
            "claude-3-opus", "claude-3-sonnet", "claude-3-haiku",
            "claude-3-5-sonnet", "claude-3-5-haiku"
        ]
        
        # Check if model starts with any supported model name
        return any(self.model.startswith(m) for m in supported_models)
