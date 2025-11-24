from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Literal, Optional


class SafetyLevel(str, Enum):
    STRICT = "strict"
    BALANCED = "balanced"
    RAW = "raw"


@dataclass
class LLMGenerationSettings:
    temperature: float = 0.2
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    json_mode: bool = False
    streaming: bool = False
    safety: SafetyLevel = SafetyLevel.BALANCED


@dataclass
class LLMCaps:
    max_context_tokens: int
    max_output_tokens: int
    tool_call_support: Literal["none", "basic", "structured"] = "none"
    function_call_format: Literal["openai", "json-in-text", "none"] = "none"
    streaming: bool = True
    json_mode: bool = False
    reasoning: bool = False
    availability: Literal["high", "variable", "low"] = "variable"


@dataclass
class ToolCall:
    name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResponse:
    text: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    safety_flags: Dict[str, Any] = field(default_factory=dict)
    token_usage: Dict[str, int] = field(default_factory=dict)
    latency_ms: Dict[str, float] = field(default_factory=dict)
    confidence_state: Literal["high", "degraded", "minimal", "retrieval-only"] = "high"


class LLMError(Exception):
    pass


class RateLimitExceeded(LLMError):
    pass


class ContextTooLarge(LLMError):
    pass


class ToolSchemaUnsupported(LLMError):
    pass


class SafetyBlocked(LLMError):
    pass


class TransportFailure(LLMError):
    pass


class GracefulTimeout(LLMError):
    pass
