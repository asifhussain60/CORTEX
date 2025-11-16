from __future__ import annotations

from typing import Dict, Optional
from .base import LLMProviderAdapter
from ..types import LLMCaps, LLMGenerationSettings, LLMResponse


class LocalAdapter(LLMProviderAdapter):
    PROVIDER_NAME = "local"

    def detect_capabilities(self) -> LLMCaps:
        return LLMCaps(
            max_context_tokens=32768,
            max_output_tokens=2048,
            tool_call_support="none",
            function_call_format="none",
            streaming=False,
            json_mode=False,
            reasoning=False,
            availability="variable",
        )

    def generate(
        self,
        prompt_text: str,
        generation: Optional[LLMGenerationSettings] = None,
        tools_schema: Optional[Dict] = None,
        system_text: Optional[str] = None,
    ) -> LLMResponse:
        generation = generation or LLMGenerationSettings()
        # Local inference placeholder (e.g., llama.cpp call)
        text = f"[local:{self.model or 'llama-3-8b'}] {prompt_text[:200]}"
        return LLMResponse(
            text=text,
            token_usage={"prompt": len(prompt_text.split()), "completion": 20},
            latency_ms={"total": 85.0},
            confidence_state="degraded",
        )
