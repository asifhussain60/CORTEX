from __future__ import annotations

from typing import Dict, Optional
from .base import LLMProviderAdapter
from ..types import LLMCaps, LLMGenerationSettings, LLMResponse


class AnthropicAdapter(LLMProviderAdapter):
    PROVIDER_NAME = "anthropic"

    def detect_capabilities(self) -> LLMCaps:
        return LLMCaps(
            max_context_tokens=200000,
            max_output_tokens=4096,
            tool_call_support="structured",
            function_call_format="openai",  # Similar JSON function spec style mapping
            streaming=True,
            json_mode=False,
            reasoning=True,
            availability="high",
        )

    def generate(
        self,
        prompt_text: str,
        generation: Optional[LLMGenerationSettings] = None,
        tools_schema: Optional[Dict] = None,
        system_text: Optional[str] = None,
    ) -> LLMResponse:
        generation = generation or LLMGenerationSettings()
        text = f"[anthropic:{self.model or 'claude-opus'}] {prompt_text[:200]}"
        return LLMResponse(
            text=text,
            token_usage={"prompt": len(prompt_text.split()), "completion": 37},
            latency_ms={"total": 140.0},
            confidence_state="high",
        )
