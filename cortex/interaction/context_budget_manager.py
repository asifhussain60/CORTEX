"""
Context Budget Manager - Token allocation and enforcement.

Authority: ENH-046 Phase 2 (Context Synthesis Gateway)
Version: 1.0
Date: 2026-02-06

Enforces 20KB token budget per turn to prevent GitHub Copilot token exhaustion.
Estimates tokens using character-based approximation (±50 token variance acceptable).

CORE Governance:
- CORE-008: TDD (tests before implementation)
- CORE-011: Type hints mandatory
- CORE-012: Google-style docstrings
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Token estimation constants (character-based approximation)
# tiktoken shows ~4 chars per token for English text
CHARS_PER_TOKEN = 4

# Budget thresholds (tokens)
DEFAULT_TOKEN_BUDGET = 5000  # 20KB ≈ 5000 tokens (4 chars/token)
WARNING_THRESHOLD = 0.8  # Warn at 80% usage
CRITICAL_THRESHOLD = 0.95  # Block at 95% usage


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class BudgetStatus:
    """Token budget status for a turn."""
    
    allocated: int  # Total budget
    used: int  # Tokens used so far
    remaining: int  # Tokens remaining
    percentage: float  # Usage percentage (0.0-1.0)
    state: str  # OK, WARNING, CRITICAL, EXCEEDED
    can_proceed: bool  # Whether to allow operation


# =============================================================================
# Context Budget Manager
# =============================================================================

class ContextBudgetManager:
    """
    Manages token budget allocation and enforcement.
    
    Responsibilities:
    - Estimate tokens from content (character-based)
    - Track budget consumption per turn
    - Enforce budget limits (warning/critical thresholds)
    - Prevent overflow (block when budget exceeded)
    
    Token Estimation:
    - Character-based: len(text) / 4 ≈ tokens
    - ±50 token variance acceptable (not mission-critical)
    - Future: tiktoken integration for exact counting
    
    Example:
        >>> manager = ContextBudgetManager(budget=5000)
        >>> tokens = manager.estimate_tokens("Hello world!")
        >>> status = manager.check_budget(tokens)
        >>> if status.can_proceed:
        ...     manager.consume(tokens)
    """
    
    def __init__(self, budget: int = DEFAULT_TOKEN_BUDGET):
        """
        Initialize budget manager.
        
        Args:
            budget: Token budget for this turn (default: 5000)
        """
        self._budget = budget
        self._used = 0
        self._history: list[tuple[str, int]] = []  # (operation, tokens)
    
    def estimate_tokens(
        self,
        content: Union[str, dict, list, Any]
    ) -> int:
        """
        Estimate token count for content.
        
        Uses character-based approximation: len(text) / 4 ≈ tokens
        ±50 token variance is acceptable for non-mission-critical estimation.
        
        Args:
            content: Content to estimate (str, dict, list, or any object)
            
        Returns:
            Estimated token count
            
        Note:
            - For str: Direct character count / 4
            - For dict/list: Convert to string representation first
            - For other types: Convert to string via str()
        """
        # Convert to string if needed
        if isinstance(content, str):
            text = content
        elif isinstance(content, (dict, list)):
            # For dict/list, convert to string representation
            text = str(content)
        else:
            # For other types, use string representation
            text = str(content)
        
        # Estimate tokens (4 chars per token)
        char_count = len(text)
        estimated_tokens = char_count // CHARS_PER_TOKEN
        
        return estimated_tokens
    
    def check_budget(self, tokens_needed: int) -> BudgetStatus:
        """
        Check if token allocation would fit within budget.
        
        Args:
            tokens_needed: Number of tokens needed
            
        Returns:
            BudgetStatus with allocation details
        """
        used_after = self._used + tokens_needed
        remaining = self._budget - used_after
        percentage = used_after / self._budget if self._budget > 0 else 1.0
        
        # Determine state
        if percentage >= 1.0:
            state = "EXCEEDED"
            can_proceed = False
        elif percentage >= CRITICAL_THRESHOLD:
            state = "CRITICAL"
            can_proceed = False
        elif percentage >= WARNING_THRESHOLD:
            state = "WARNING"
            can_proceed = True
        else:
            state = "OK"
            can_proceed = True
        
        return BudgetStatus(
            allocated=self._budget,
            used=used_after,
            remaining=remaining,
            percentage=percentage,
            state=state,
            can_proceed=can_proceed
        )
    
    def consume(
        self,
        tokens: int,
        operation: str = "unknown"
    ) -> BudgetStatus:
        """
        Consume tokens from budget.
        
        Args:
            tokens: Number of tokens to consume
            operation: Operation name for tracking
            
        Returns:
            Updated BudgetStatus
            
        Raises:
            ValueError: If budget exceeded (state=EXCEEDED)
        """
        status = self.check_budget(tokens)
        
        if not status.can_proceed:
            raise ValueError(
                f"Token budget exceeded: {status.used}/{status.allocated} "
                f"({status.percentage:.1%})"
            )
        
        # Update usage
        self._used += tokens
        self._history.append((operation, tokens))
        
        # Log warnings
        if status.state == "WARNING":
            logger.warning(
                f"Token budget WARNING: {status.used}/{status.allocated} "
                f"({status.percentage:.1%}) - consider reducing context"
            )
        
        return status
    
    def reset(self) -> None:
        """Reset budget tracking for new turn."""
        self._used = 0
        self._history.clear()
    
    def get_status(self) -> BudgetStatus:
        """
        Get current budget status.
        
        Returns:
            Current BudgetStatus
        """
        return self.check_budget(0)
    
    def get_history(self) -> list[tuple[str, int]]:
        """
        Get consumption history.
        
        Returns:
            List of (operation, tokens) tuples
        """
        return self._history.copy()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get budget summary for reporting.
        
        Returns:
            Summary dictionary with usage stats
        """
        status = self.get_status()
        
        return {
            "budget": self._budget,
            "used": self._used,
            "remaining": status.remaining,
            "percentage": status.percentage,
            "state": status.state,
            "operations": len(self._history),
            "history": self._history
        }
