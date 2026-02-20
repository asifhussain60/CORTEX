"""
Token Budget Manager.

AC-ID: AC-LENS-LLM-002
Manages token budgets per-request and per-user to prevent cost overruns.
Compliance: CORE-011 (Type hints), CORE-012 (Docstrings), CORE-013 (Specific exceptions)
"""

import os
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class BudgetExceededError(Exception):
    """Raised when token budget is exceeded."""
    pass


class ContextTooLargeError(Exception):
    """Raised when input context exceeds maximum size (PHASE 1)."""
    pass


@dataclass
class TokenUsageRecord:
    """Record of token usage for a single request."""
    timestamp: datetime
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float = 0.0

    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self.prompt_tokens + self.completion_tokens


class TokenBudgetManager:
    """
    Manages token budgets for LLM API calls.

    Features:
    - Per-request token limits (prevent single large request)
    - Per-user daily limits (prevent abuse)
    - Cost tracking (monitor spending)
    - Automatic daily reset (24h sliding window)

    Example:
        >>> manager = TokenBudgetManager(per_request_limit=10000)
        >>> manager.check_request_budget(tokens=5000)  # OK
        >>> manager.check_request_budget(tokens=15000)  # Raises BudgetExceededError
        >>>
        >>> manager.record_usage("user1", prompt_tokens=100, completion_tokens=200)
        >>> stats = manager.get_user_stats("user1")
        >>> print(f"Used: {stats['total_tokens']} tokens")
    """

    def __init__(
        self,
        per_request_limit: Optional[int] = None,
        per_user_daily_limit: Optional[int] = None,
        global_daily_limit: Optional[int] = None
    ):
        """
        Initialize token budget manager.

        Args:
            per_request_limit: Maximum tokens per single request (default from env)
            per_user_daily_limit: Maximum tokens per user per day (default from env)
            global_daily_limit: Maximum tokens globally per day (default from env)
        """
        self.per_request_limit = per_request_limit or int(
            os.getenv("LLM_TOKEN_BUDGET_PER_REQUEST", "10000")
        )
        self.per_user_daily_limit = per_user_daily_limit or int(
            os.getenv("LLM_TOKEN_BUDGET_PER_USER_DAILY", "100000")
        )
        self.global_daily_limit = global_daily_limit or int(
            os.getenv("LLM_TOKEN_BUDGET_GLOBAL_DAILY", "1000000")
        )

        # User usage tracking (user_id -> list of records)
        self._user_usage: Dict[str, List[TokenUsageRecord]] = defaultdict(list)

        # Global usage tracking
        self._global_usage: List[TokenUsageRecord] = []

    def check_request_budget(self, tokens: int) -> None:
        """
        Check if request is within per-request budget.

        Args:
            tokens: Number of tokens requested

        Raises:
            BudgetExceededError: If tokens exceed per-request limit
        """
        if tokens > self.per_request_limit:
            raise BudgetExceededError(
                f"Request budget exceeded: {tokens} tokens requested, "
                f"limit is {self.per_request_limit}"
            )

    def check_context_size(self, text: str, model: str) -> None:
        """
        PHASE 1: Check if input context exceeds maximum size.

        Prevents context window DoS attacks by limiting input size.

        Args:
            text: Input text to check
            model: Model name (for context window lookup)

        Raises:
            ContextTooLargeError: If estimated tokens exceed limit
        """
        # Maximum context tokens (conservative limit to prevent DoS)
        MAX_CONTEXT_TOKENS = int(os.getenv("LLM_MAX_CONTEXT_TOKENS", "100000"))

        # Rough token estimation (1 token ≈ 0.75 words for English)
        # Conservative estimate: 1 token per word
        estimated_tokens = len(text.split())

        if estimated_tokens > MAX_CONTEXT_TOKENS:
            raise ContextTooLargeError(
                f"Input context too large: ~{estimated_tokens} tokens estimated, "
                f"maximum is {MAX_CONTEXT_TOKENS}. "
                f"Consider using smart context selection or summarization."
            )

    def check_user_budget(self, user_id: str, tokens: int) -> None:
        """
        Check if user is within daily budget.

        Args:
            user_id: User identifier
            tokens: Number of tokens for new request

        Raises:
            BudgetExceededError: If tokens would exceed user daily limit
        """
        current_usage = self._get_user_daily_usage(user_id)

        if current_usage + tokens > self.per_user_daily_limit:
            raise BudgetExceededError(
                f"User daily budget exceeded: {current_usage} tokens used today, "
                f"{tokens} requested, limit is {self.per_user_daily_limit}"
            )

    def check_global_budget(self, tokens: int) -> None:
        """
        Check if request is within global daily budget.

        Args:
            tokens: Number of tokens for new request

        Raises:
            BudgetExceededError: If tokens would exceed global daily limit
        """
        current_usage = self._get_global_daily_usage()

        if current_usage + tokens > self.global_daily_limit:
            raise BudgetExceededError(
                f"Global daily budget exceeded: {current_usage} tokens used today, "
                f"{tokens} requested, limit is {self.global_daily_limit}"
            )

    def record_usage(
        self,
        user_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float = 0.0
    ) -> None:
        """
        Record token usage for a user.

        Args:
            user_id: User identifier
            prompt_tokens: Tokens used in prompt
            completion_tokens: Tokens used in completion
            cost_usd: Estimated cost in USD
        """
        record = TokenUsageRecord(
            timestamp=datetime.now(),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=cost_usd
        )

        self._user_usage[user_id].append(record)
        self._global_usage.append(record)

        # Cleanup old records (keep only last 30 days)
        self._cleanup_old_records()

    def get_user_stats(self, user_id: str) -> Dict[str, any]:
        """
        Get usage statistics for a user.

        Args:
            user_id: User identifier

        Returns:
            Dict with total_tokens, total_cost_usd, request_count, remaining_daily_tokens
        """
        records = self._get_user_daily_records(user_id)

        total_tokens = sum(r.total_tokens for r in records)
        total_cost = sum(r.cost_usd for r in records)

        return {
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost,
            "request_count": len(records),
            "remaining_daily_tokens": max(0, self.per_user_daily_limit - total_tokens),
            "daily_limit": self.per_user_daily_limit
        }

    def get_global_stats(self) -> Dict[str, any]:
        """
        Get global usage statistics.

        Returns:
            Dict with total_tokens, total_cost_usd, total_users, total_requests
        """
        records = self._get_global_daily_records()

        total_tokens = sum(r.total_tokens for r in records)
        total_cost = sum(r.cost_usd for r in records)
        unique_users = len(self._user_usage)

        return {
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost,
            "total_users": unique_users,
            "total_requests": len(records),
            "remaining_daily_tokens": max(0, self.global_daily_limit - total_tokens),
            "daily_limit": self.global_daily_limit
        }

    def reset_user_budget(self, user_id: str) -> None:
        """
        Reset user budget (for testing or admin override).

        Args:
            user_id: User identifier
        """
        if user_id in self._user_usage:
            del self._user_usage[user_id]

    def _get_user_daily_usage(self, user_id: str) -> int:
        """Get total tokens used by user in last 24 hours."""
        records = self._get_user_daily_records(user_id)
        return sum(r.total_tokens for r in records)

    def _get_global_daily_usage(self) -> int:
        """Get total tokens used globally in last 24 hours."""
        records = self._get_global_daily_records()
        return sum(r.total_tokens for r in records)

    def _get_user_daily_records(self, user_id: str) -> List[TokenUsageRecord]:
        """Get user records from last 24 hours."""
        cutoff = datetime.now() - timedelta(hours=24)
        return [
            r for r in self._user_usage.get(user_id, [])
            if r.timestamp > cutoff
        ]

    def _get_global_daily_records(self) -> List[TokenUsageRecord]:
        """Get global records from last 24 hours."""
        cutoff = datetime.now() - timedelta(hours=24)
        return [r for r in self._global_usage if r.timestamp > cutoff]

    def _cleanup_old_records(self) -> None:
        """Remove records older than 30 days to prevent memory bloat."""
        cutoff = datetime.now() - timedelta(days=30)

        # Cleanup user records
        for user_id in list(self._user_usage.keys()):
            self._user_usage[user_id] = [
                r for r in self._user_usage[user_id]
                if r.timestamp > cutoff
            ]
            # Remove empty user entries
            if not self._user_usage[user_id]:
                del self._user_usage[user_id]

        # Cleanup global records
        self._global_usage = [
            r for r in self._global_usage
            if r.timestamp > cutoff
        ]
