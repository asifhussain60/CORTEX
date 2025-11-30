from __future__ import annotations

from typing import Dict, List, Optional, Type

from .types import LLMGenerationSettings, LLMResponse, LLMCaps
from .adapters.base import LLMProviderAdapter
from .adapters.openai_adapter import OpenAIAdapter
from .adapters.anthropic_adapter import AnthropicAdapter
from .adapters.local_adapter import LocalAdapter


ADAPTER_REGISTRY: Dict[str, Type[LLMProviderAdapter]] = {
    OpenAIAdapter.PROVIDER_NAME: OpenAIAdapter,
    AnthropicAdapter.PROVIDER_NAME: AnthropicAdapter,
    LocalAdapter.PROVIDER_NAME: LocalAdapter,
}


class LLMOrchestrator:
    """Selects appropriate adapter and applies fallback strategy."""

    def __init__(self, primary_provider: str, fallback_chain: Optional[List[str]] = None):
        if primary_provider not in ADAPTER_REGISTRY:
            raise ValueError(f"Unknown provider: {primary_provider}")
        self.primary_provider = primary_provider
        self.fallback_chain = fallback_chain or ["local"]
        self._adapters: Dict[str, LLMProviderAdapter] = {}

    def _get_adapter(self, provider: str) -> LLMProviderAdapter:
        if provider not in ADAPTER_REGISTRY:
            raise ValueError(f"Unknown provider: {provider}")
        if provider not in self._adapters:
            adapter_cls = ADAPTER_REGISTRY[provider]
            self._adapters[provider] = adapter_cls()
        return self._adapters[provider]

    def capabilities(self, provider: Optional[str] = None) -> LLMCaps:
        provider = provider or self.primary_provider
        adapter = self._get_adapter(provider)
        return adapter.detect_capabilities()

    def generate(
        self,
        prompt_text: str,
        generation: Optional[LLMGenerationSettings] = None,
        tools_schema: Optional[Dict] = None,
        system_text: Optional[str] = None,
    ) -> LLMResponse:
        providers_to_try = [self.primary_provider] + [p for p in self.fallback_chain if p != self.primary_provider]
        last_error: Optional[Exception] = None

        for provider in providers_to_try:
            adapter = self._get_adapter(provider)
            caps = adapter.detect_capabilities()

            # Basic compatibility guard: tool schema requested but provider cannot handle
            if tools_schema and caps.tool_call_support == "none":
                continue  # try next provider

            try:
                response = adapter.generate(
                    prompt_text=prompt_text,
                    generation=generation,
                    tools_schema=tools_schema,
                    system_text=system_text,
                )
                if provider != self.primary_provider:
                    response.confidence_state = "degraded"
                return response
            except Exception as exc:  # broad catch for stub stage
                last_error = exc
                continue

        raise RuntimeError(f"All providers failed. Last error: {last_error}")
