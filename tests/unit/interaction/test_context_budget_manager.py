"""
Tests for ContextBudgetManager.

Authority: ENH-046 Phase 2 (Context Synthesis Gateway)
Test Coverage: Token estimation, budget enforcement, overflow prevention
"""

import pytest
from cortex.interaction.context_budget_manager import (
    ContextBudgetManager,
    BudgetStatus,
    DEFAULT_TOKEN_BUDGET,
    WARNING_THRESHOLD,
    CRITICAL_THRESHOLD,
)


class TestContextBudgetManager:
    """Test suite for ContextBudgetManager."""
    
    def test_initialization(self):
        """Test manager initializes with default budget."""
        manager = ContextBudgetManager()
        
        status = manager.get_status()
        assert status.allocated == DEFAULT_TOKEN_BUDGET
        assert status.used == 0
        assert status.remaining == DEFAULT_TOKEN_BUDGET
        assert status.state == "OK"
    
    def test_custom_budget(self):
        """Test manager accepts custom budget."""
        manager = ContextBudgetManager(budget=10000)
        
        status = manager.get_status()
        assert status.allocated == 10000
    
    def test_estimate_tokens_string(self):
        """Test token estimation for strings."""
        manager = ContextBudgetManager()
        
        # ~4 characters per token
        text = "Hello world! This is a test."  # 28 chars = ~7 tokens
        tokens = manager.estimate_tokens(text)
        
        # Allow ±50 token variance
        assert tokens == 7  # 28 / 4 = 7
    
    def test_estimate_tokens_dict(self):
        """Test token estimation for dict inputs."""
        manager = ContextBudgetManager()
        
        data = {"key": "value", "number": 123}
        tokens = manager.estimate_tokens(data)
        
        # Should convert to string and estimate
        assert tokens > 0  # Exact value depends on string representation
        assert isinstance(tokens, int)
    
    def test_estimate_tokens_list(self):
        """Test token estimation for list inputs."""
        manager = ContextBudgetManager()
        
        data = ["item1", "item2", "item3"]
        tokens = manager.estimate_tokens(data)
        
        assert tokens > 0
        assert isinstance(tokens, int)
    
    def test_check_budget_ok_state(self):
        """Test budget check in OK state."""
        manager = ContextBudgetManager(budget=5000)
        
        status = manager.check_budget(1000)
        
        assert status.state == "OK"
        assert status.can_proceed is True
        assert status.used == 1000
        assert status.remaining == 4000
        assert status.percentage < WARNING_THRESHOLD
    
    def test_check_budget_warning_state(self):
        """Test budget check in WARNING state."""
        manager = ContextBudgetManager(budget=5000)
        
        # Use 80%+ of budget
        status = manager.check_budget(4100)
        
        assert status.state == "WARNING"
        assert status.can_proceed is True
        assert status.percentage >= WARNING_THRESHOLD
        assert status.percentage < CRITICAL_THRESHOLD
    
    def test_check_budget_critical_state(self):
        """Test budget check in CRITICAL state."""
        manager = ContextBudgetManager(budget=5000)
        
        # Use 95%+ of budget
        status = manager.check_budget(4800)
        
        assert status.state == "CRITICAL"
        assert status.can_proceed is False
        assert status.percentage >= CRITICAL_THRESHOLD
    
    def test_check_budget_exceeded_state(self):
        """Test budget check when exceeded."""
        manager = ContextBudgetManager(budget=5000)
        
        status = manager.check_budget(6000)
        
        assert status.state == "EXCEEDED"
        assert status.can_proceed is False
        assert status.percentage >= 1.0
    
    def test_consume_success(self):
        """Test successful token consumption."""
        manager = ContextBudgetManager(budget=5000)
        
        status = manager.consume(1000, operation="load_agent")
        
        assert status.state == "OK"
        assert manager.get_status().used == 1000
    
    def test_consume_raises_on_exceeded(self):
        """Test consume raises ValueError when budget exceeded."""
        manager = ContextBudgetManager(budget=5000)
        
        with pytest.raises(ValueError, match="Token budget exceeded"):
            manager.consume(6000)
    
    def test_consume_tracks_history(self):
        """Test consumption history tracking."""
        manager = ContextBudgetManager(budget=5000)
        
        manager.consume(1000, operation="op1")
        manager.consume(500, operation="op2")
        
        history = manager.get_history()
        assert len(history) == 2
        assert history[0] == ("op1", 1000)
        assert history[1] == ("op2", 500)
    
    def test_reset(self):
        """Test budget reset."""
        manager = ContextBudgetManager(budget=5000)
        
        manager.consume(1000)
        manager.reset()
        
        status = manager.get_status()
        assert status.used == 0
        assert len(manager.get_history()) == 0
    
    def test_get_summary(self):
        """Test summary generation."""
        manager = ContextBudgetManager(budget=5000)
        
        manager.consume(1000, operation="op1")
        manager.consume(500, operation="op2")
        
        summary = manager.get_summary()
        
        assert summary["budget"] == 5000
        assert summary["used"] == 1500
        assert summary["remaining"] == 3500
        assert summary["state"] == "OK"
        assert summary["operations"] == 2
        assert len(summary["history"]) == 2
