from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Optional

from ..types import LLMCaps, LLMGenerationSettings, LLMResponse


class LLMProviderAdapter(ABC):
    """Abstract base for provider-specific LLM adapters."""

    def __init__(self, model: Optional[str] = None, config: Optional[Dict] = None):
        self.model = model
        self.config = config or {}

    @abstractmethod
    def detect_capabilities(self) -> LLMCaps:
        """Return the static/detected capabilities for this provider/model."""
        raise NotImplementedError

    @abstractmethod
    def generate(
        self,
        prompt_text: str,
        generation: Optional[LLMGenerationSettings] = None,
        tools_schema: Optional[Dict] = None,
        system_text: Optional[str] = None,
    ) -> LLMResponse:
        """Generate a response for the given prompt and settings."""
        raise NotImplementedError
