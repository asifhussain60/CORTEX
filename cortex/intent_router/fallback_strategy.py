"""Fallback Strategy Module - Handles fallback logic for intent routing.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass


class FallbackType(Enum):
    """Types of fallback strategies."""
    DEFAULT = "default"
    CACHED = "cached"
    RETRY = "retry"
    ALTERNATE = "alternate"


@dataclass
class FallbackStrategy:
    """Fallback strategy configuration."""
    
    strategy_type: FallbackType = FallbackType.DEFAULT
    max_retries: int = 3
    cache_enabled: bool = True
    alternate_handlers: List[str] = None
    
    def __post_init__(self):
        """Initialize defaults."""
        if self.alternate_handlers is None:
            self.alternate_handlers = []
    
    def execute(self, context: Dict[str, Any]) -> Any:
        """Execute fallback strategy.
        
        Args:
            context: Execution context
            
        Returns:
            Fallback result
        """
        if self.strategy_type == FallbackType.DEFAULT:
            return {"status": "fallback", "type": "default"}
        elif self.strategy_type == FallbackType.CACHED:
            return context.get("cached_result", {})
        elif self.strategy_type == FallbackType.RETRY:
            return {"status": "retry", "attempts": self.max_retries}
        else:
            return {"status": "alternate", "handlers": self.alternate_handlers}


__all__ = ["FallbackType", "FallbackStrategy"]
