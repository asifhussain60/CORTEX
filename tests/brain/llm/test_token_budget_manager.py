"""
Tests for Token Budget Manager.

AC-ID: AC-LENS-LLM-002
TDD: CORE-008 (Tests created first)
Coverage: TokenBudgetManager, per-request and per-user limits
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from cortex.brain.llm.token_budget_manager import (
    TokenBudgetManager,
    BudgetExceededError,
    ContextTooLargeError,
    TokenUsageRecord
)


class TestTokenBudgetManager:
    """Test token budget management."""
    
    def test_manager_initialization(self):
        """Test manager initializes with default limits."""
        manager = TokenBudgetManager(
            per_request_limit=10000,
            per_user_daily_limit=100000
        )
        
        assert manager.per_request_limit == 10000
        assert manager.per_user_daily_limit == 100000
    
    def test_check_request_budget_within_limit(self):
        """Test request budget check passes when within limit."""
        manager = TokenBudgetManager(per_request_limit=10000)
        
        # Should not raise
        manager.check_request_budget(tokens=5000)
    
    def test_check_request_budget_exceeds_limit(self):
        """Test request budget check fails when exceeding limit."""
        manager = TokenBudgetManager(per_request_limit=10000)
        
        with pytest.raises(BudgetExceededError, match="Request budget exceeded"):
            manager.check_request_budget(tokens=15000)
    
    def test_check_user_budget_within_limit(self):
        """Test user daily budget check passes when within limit."""
        manager = TokenBudgetManager(per_user_daily_limit=100000)
        
        # Record some usage
        manager.record_usage("user1", prompt_tokens=1000, completion_tokens=2000)
        
        # Should not raise (3000 < 100000)
        manager.check_user_budget("user1", tokens=5000)
    
    def test_check_user_budget_exceeds_limit(self):
        """Test user daily budget check fails when exceeding limit."""
        manager = TokenBudgetManager(per_user_daily_limit=10000)
        
        # Record usage near limit
        manager.record_usage("user1", prompt_tokens=5000, completion_tokens=4000)
        
        # Try to exceed limit
        with pytest.raises(BudgetExceededError, match="User daily budget exceeded"):
            manager.check_user_budget("user1", tokens=2000)
    
    def test_record_usage(self):
        """Test usage recording."""
        manager = TokenBudgetManager()
        
        manager.record_usage(
            user_id="user1",
            prompt_tokens=100,
            completion_tokens=200,
            cost_usd=0.05
        )
        
        stats = manager.get_user_stats("user1")
        assert stats["total_tokens"] == 300
        assert stats["total_cost_usd"] == 0.05
        assert stats["request_count"] == 1
    
    def test_get_user_stats(self):
        """Test retrieving user statistics."""
        manager = TokenBudgetManager()
        
        manager.record_usage("user1", prompt_tokens=100, completion_tokens=200)
        manager.record_usage("user1", prompt_tokens=150, completion_tokens=250)
        
        stats = manager.get_user_stats("user1")
        
        assert stats["total_tokens"] == 700  # 300 + 400
        assert stats["request_count"] == 2
        assert stats["remaining_daily_tokens"] > 0
    
    def test_reset_user_budget(self):
        """Test resetting user budget."""
        manager = TokenBudgetManager()
        
        manager.record_usage("user1", prompt_tokens=1000, completion_tokens=2000)
        
        stats_before = manager.get_user_stats("user1")
        assert stats_before["total_tokens"] == 3000
        
        manager.reset_user_budget("user1")
        
        stats_after = manager.get_user_stats("user1")
        assert stats_after["total_tokens"] == 0
    
    def test_daily_budget_resets_automatically(self):
        """Test that daily budgets reset after 24 hours."""
        manager = TokenBudgetManager(per_user_daily_limit=10000)
        
        # Record usage with old timestamp
        old_timestamp = datetime.now() - timedelta(hours=25)
        manager._user_usage["user1"] = [
            TokenUsageRecord(
                timestamp=old_timestamp,
                prompt_tokens=5000,
                completion_tokens=4000,
                cost_usd=0.0
            )
        ]
        
        # Check current usage (should exclude old records)
        stats = manager.get_user_stats("user1")
        assert stats["total_tokens"] == 0  # Old usage excluded
    
    def test_get_global_stats(self):
        """Test retrieving global statistics."""
        manager = TokenBudgetManager()
        
        manager.record_usage("user1", prompt_tokens=100, completion_tokens=200)
        manager.record_usage("user2", prompt_tokens=150, completion_tokens=250)
        
        stats = manager.get_global_stats()
        
        assert stats["total_tokens"] == 700
        assert stats["total_users"] == 2
        assert stats["total_requests"] == 2
    
    def test_cost_tracking(self):
        """Test cost tracking functionality."""
        manager = TokenBudgetManager()
        
        manager.record_usage(
            "user1",
            prompt_tokens=1000,
            completion_tokens=2000,
            cost_usd=0.10
        )
        
        stats = manager.get_user_stats("user1")
        assert stats["total_cost_usd"] == 0.10
        
        global_stats = manager.get_global_stats()
        assert global_stats["total_cost_usd"] == 0.10
    
    def test_context_size_check_within_limit(self):
        """PHASE 1: Test context size check passes when within limit."""
        manager = TokenBudgetManager()
        
        # Small text (under 100k tokens)
        small_text = " ".join(["word"] * 1000)  # ~1k tokens
        
        # Should not raise
        manager.check_context_size(small_text, model="gpt-4")
    
    def test_context_size_check_exceeds_limit(self):
        """PHASE 1: Test context size check fails when exceeding limit."""
        manager = TokenBudgetManager()
        
        # Large text (over 100k tokens)
        large_text = " ".join(["word"] * 150000)  # ~150k tokens
        
        with pytest.raises(ContextTooLargeError, match="Input context too large"):
            manager.check_context_size(large_text, model="gpt-4")
