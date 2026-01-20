"""CORE-036: Runtime Resilience Configuration"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Any, Dict, List
from enum import Enum

class ResilienceLevel(Enum):
    STRICT = "strict"
    NORMAL = "normal"
    LENIENT = "lenient"

@dataclass
class ResilienceConfig:
    level: ResilienceLevel
    max_retries: int
    timeout_seconds: float
    circuit_breaker_threshold: float

class RuntimeResilienceManager:
    def __init__(self):
        self.config = ResilienceConfig(
            level=ResilienceLevel.NORMAL,
            max_retries=3,
            timeout_seconds=30.0,
            circuit_breaker_threshold=0.5
        )
    
    def set_resilience_level(self, level: ResilienceLevel) -> None:
        self.config.level = level
    
    def get_config(self) -> ResilienceConfig:
        return self.config
