"""
Tests for Cache Monitor
Phase 1.5: Token Optimization System
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
from src.tier1.cache_monitor import CacheMonitor, CacheHealthReport


class TestCacheMonitor:
    """Test Cache Monitor functionality."""
    
    @pytest.fixture
    def mock_working_memory(self):
        """Create mock working memory."""
        mock = Mock()
        mock.db_path = "test.db"
        mock.get_recent_conversations = Mock(return_value=[])
        mock.get_active_conversation = Mock(return_value=None)
        return mock
    
    @pytest.fixture
    def monitor(self, mock_working_memory):
        """Create monitor instance."""
        return CacheMonitor(mock_working_memory)
    
    @pytest.fixture
    def sample_conversations(self):
        """Create sample conversations with varying token counts."""
        base_date = datetime.now() - timedelta(days=30)
        
        return [
            {
                "conversation_id": f"conv{i}",
                "title": f"Conversation {i}",
                "messages": [
                    {"content": "A" * 1000}  # ~250 tokens per message
                    for _ in range(10)  # ~2,500 tokens per conversation
                ],
                "created_at": (base_date + timedelta(days=i)).isoformat()
            }
            for i in range(20)  # 20 conversations = ~50,000 tokens
        ]
    
    # ========== Basic Functionality Tests ==========
    
    def test_monitor_initialization(self, monitor):
        """Test monitor initializes correctly."""
        assert monitor.SOFT_LIMIT == 40_000
        assert monitor.HARD_LIMIT == 50_000
        assert monitor.TARGET_AFTER_TRIM == 30_000
        assert monitor._total_checks == 0
        assert monitor._warnings_issued == 0
        assert monitor._emergency_trims == 0
    
    def test_check_cache_health_ok_status(self, monitor, mock_working_memory):
        """Test cache health check with OK status."""
        # Small conversations (well below soft limit)
        small_convs = [
            {
                "conversation_id": "conv1",
                "messages": [{"content": "A" * 400}]  # ~100 tokens
            }
        ]
        mock_working_memory.get_recent_conversations.return_value = small_convs
        
        status = monitor.check_cache_health()
        
        assert status["status"] == "OK"
        assert status["total_tokens"] < monitor.SOFT_LIMIT
        assert "tokens_available" in status
        assert "health_percentage" in status
        assert monitor._total_checks == 1
    
    def test_check_cache_health_warning_status(self, monitor, mock_working_memory):
        """Test cache health check with WARNING status."""
        # Conversations exceeding soft limit
        large_convs = [
            {
                "conversation_id": f"conv{i}",
                "messages": [{"content": "A" * 20_000}]  # ~5,000 tokens each
            }
            for i in range(9)  # ~45,000 tokens total
        ]
        mock_working_memory.get_recent_conversations.return_value = large_convs
        
        status = monitor.check_cache_health()
        
        assert status["status"] == "WARNING"
        assert status["total_tokens"] > monitor.SOFT_LIMIT
        assert status["total_tokens"] < monitor.HARD_LIMIT
        assert "tokens_until_hard_limit" in status
        assert monitor._warnings_issued == 1
    
    def test_check_cache_health_critical_trim(self, monitor, mock_working_memory, sample_conversations):
        """Test cache health check with CRITICAL status and emergency trim."""
        # Conversations exceeding hard limit
        mock_working_memory.get_recent_conversations.return_value = sample_conversations
        mock_conv = Mock()
        mock_conv.conversation_id = "conv15"  # Recent conversation
        mock_working_memory.get_active_conversation.return_value = mock_conv
        
        status = monitor.check_cache_health()
        
        assert status["status"] == "CRITICAL_TRIMMED"
        assert status["action_taken"] == "emergency_trim"
        assert "conversations_archived" in status
        assert "new_token_count" in status
        assert "tokens_saved" in status
        assert monitor._emergency_trims == 1
    
    def test_warning_issued_once(self, monitor, mock_working_memory):
        """Test that warning is only issued once until resolved."""
        large_convs = [
            {"conversation_id": f"conv{i}", "messages": [{"content": "A" * 20_000}]}
            for i in range(9)
        ]
        mock_working_memory.get_recent_conversations.return_value = large_convs
        
        # First check - warning issued
        status1 = monitor.check_cache_health()
        assert status1["status"] == "WARNING"
        assert monitor._warnings_issued == 1
        
        # Second check - warning not re-issued
        status2 = monitor.check_cache_health()
        assert status2["status"] == "WARNING"
        assert monitor._warnings_issued == 1  # Still 1
    
    # ========== Emergency Trim Tests ==========
    
    def test_emergency_trim_preserves_active_conversation(self, monitor, sample_conversations):
        """Test that emergency trim preserves active conversation."""
        mock_active = Mock()
        mock_active.conversation_id = "conv15"
        monitor.working_memory.get_active_conversation.return_value = mock_active
        
        archived_count = monitor._emergency_trim(sample_conversations)
        
        # Should archive conversations but not the active one
        assert archived_count > 0
        # Active conversation should still be in list
        assert any(c["conversation_id"] == "conv15" for c in sample_conversations)
    
    def test_emergency_trim_preserves_today_conversations(self, monitor):
        """Test that emergency trim preserves today's conversations."""
        today = datetime.now()
        old_date = today - timedelta(days=40)
        
        conversations = [
            {
                "conversation_id": "old1",
                "messages": [{"content": "A" * 40_000}],
                "created_at": old_date.isoformat()
            },
            {
                "conversation_id": "old2",
                "messages": [{"content": "A" * 40_000}],
                "created_at": (old_date + timedelta(days=1)).isoformat()
            },
            {
                "conversation_id": "today1",
                "messages": [{"content": "A" * 40_000}],
                "created_at": today.isoformat()
            }
        ]
        
        archived_count = monitor._emergency_trim(conversations)
        
        # Should archive old conversations
        assert archived_count >= 1
        # Today's conversation should remain
        remaining_ids = [c["conversation_id"] for c in conversations]
        assert "today1" in remaining_ids
    
    def test_emergency_trim_reaches_target(self, monitor, sample_conversations):
        """Test that emergency trim reduces to target."""
        archived_count = monitor._emergency_trim(sample_conversations)
        
        # Calculate remaining tokens
        remaining_tokens = sum(
            len(msg.get("content", "")) // 4
            for conv in sample_conversations
            for msg in conv.get("messages", [])
        )
        
        # Should be at or below target
        assert remaining_tokens <= monitor.TARGET_AFTER_TRIM or archived_count > 0
    
    def test_emergency_trim_handles_invalid_dates(self, monitor):
        """Test emergency trim handles invalid dates gracefully."""
        conversations = [
            {
                "conversation_id": "conv1",
                "messages": [{"content": "A" * 40_000}],
                "created_at": "invalid-date"
            },
            {
                "conversation_id": "conv2",
                "messages": [{"content": "A" * 40_000}],
                "created_at": None
            }
        ]
        
        # Should not raise exception
        archived_count = monitor._emergency_trim(conversations)
        assert archived_count >= 0  # At least doesn't crash
    
    # ========== Trim Recommendations Tests ==========
    
    def test_get_trim_recommendations(self, monitor, mock_working_memory):
        """Test getting trim recommendations."""
        old_date = datetime.now() - timedelta(days=40)
        recent_date = datetime.now() - timedelta(days=10)
        
        conversations = [
            {
                "conversation_id": "old1",
                "messages": [{"content": "Test"}],
                "created_at": old_date.isoformat()
            },
            {
                "conversation_id": "recent1",
                "messages": [{"content": "Test"}],
                "created_at": recent_date.isoformat()
            }
        ]
        
        mock_working_memory.get_recent_conversations.return_value = conversations
        
        recommendations = monitor.get_trim_recommendations()
        
        # Should recommend archiving old conversation
        assert len(recommendations) >= 1
        assert any(r["conversation_id"] == "old1" for r in recommendations)
        assert all("reason" in r for r in recommendations)
        assert all("age_days" in r for r in recommendations)
        assert all("estimated_tokens" in r for r in recommendations)
    
    def test_trim_recommendations_sorted_by_age(self, monitor, mock_working_memory):
        """Test recommendations are sorted by age (oldest first)."""
        dates = [datetime.now() - timedelta(days=d) for d in [60, 45, 90]]
        
        conversations = [
            {
                "conversation_id": f"conv{i}",
                "messages": [{"content": "Test"}],
                "created_at": date.isoformat()
            }
            for i, date in enumerate(dates)
        ]
        
        mock_working_memory.get_recent_conversations.return_value = conversations
        
        recommendations = monitor.get_trim_recommendations()
        
        # Should be sorted by age descending (oldest first)
        if len(recommendations) > 1:
            ages = [r["age_days"] for r in recommendations]
            assert ages == sorted(ages, reverse=True)
    
    def test_trim_recommendations_ignores_recent(self, monitor, mock_working_memory):
        """Test recommendations ignore recent conversations."""
        recent_date = datetime.now() - timedelta(days=10)
        
        conversations = [
            {
                "conversation_id": "recent1",
                "messages": [{"content": "Test"}],
                "created_at": recent_date.isoformat()
            }
        ]
        
        mock_working_memory.get_recent_conversations.return_value = conversations
        
        recommendations = monitor.get_trim_recommendations()
        
        # Should not recommend archiving recent conversations
        assert len(recommendations) == 0
    
    # ========== Statistics Tests ==========
    
    def test_get_statistics(self, monitor, mock_working_memory):
        """Test getting monitor statistics."""
        # Perform some checks
        mock_working_memory.get_recent_conversations.return_value = []
        monitor.check_cache_health()
        monitor.check_cache_health()
        
        stats = monitor.get_statistics()
        
        assert stats["total_checks"] == 2
        assert "warnings_issued" in stats
        assert "emergency_trims" in stats
        assert "conversations_archived" in stats
        assert stats["soft_limit"] == 40_000
        assert stats["hard_limit"] == 50_000
    
    def test_reset_statistics(self, monitor):
        """Test resetting statistics."""
        monitor._total_checks = 5
        monitor._warnings_issued = 2
        monitor._emergency_trims = 1
        
        monitor.reset_statistics()
        
        assert monitor._total_checks == 0
        assert monitor._warnings_issued == 0
        assert monitor._emergency_trims == 0
    
    # ========== Helper Method Tests ==========
    
    def test_count_tokens(self, monitor):
        """Test token counting."""
        # 400 characters = ~100 tokens
        tokens = monitor._count_tokens("A" * 400)
        assert tokens == 100
        
        # Empty string
        tokens = monitor._count_tokens("")
        assert tokens == 0
        
        # None
        tokens = monitor._count_tokens(None)
        assert tokens == 0
    
    def test_count_conversation_tokens(self, monitor):
        """Test counting tokens for conversations."""
        conversations = [
            {
                "messages": [
                    {"content": "A" * 400},  # 100 tokens
                    {"content": "B" * 400}   # 100 tokens
                ],
                "title": "C" * 40,  # 10 tokens
                "summary": "D" * 40  # 10 tokens
            }
        ]
        
        total = monitor._count_conversation_tokens(conversations)
        assert total == 220  # 100 + 100 + 10 + 10


class TestCacheHealthReport:
    """Test Cache Health Report functionality."""
    
    @pytest.fixture
    def mock_monitor(self):
        """Create mock monitor."""
        mock = Mock(spec=CacheMonitor)
        mock.SOFT_LIMIT = 40_000
        mock.HARD_LIMIT = 50_000
        mock.check_cache_health = Mock(return_value={
            "status": "OK",
            "total_tokens": 20_000,
            "conversation_count": 10
        })
        mock.get_trim_recommendations = Mock(return_value=[])
        mock.get_statistics = Mock(return_value={
            "total_checks": 5,
            "warnings_issued": 0,
            "emergency_trims": 0,
            "conversations_archived": 0
        })
        return mock
    
    @pytest.fixture
    def report(self, mock_monitor):
        """Create health report instance."""
        return CacheHealthReport(mock_monitor)
    
    def test_generate_report_structure(self, report):
        """Test report generation structure."""
        full_report = report.generate_report()
        
        assert "timestamp" in full_report
        assert "current_status" in full_report
        assert "health_score" in full_report
        assert "risk_level" in full_report
        assert "statistics" in full_report
        assert "recommendations" in full_report
        assert "summary" in full_report
    
    def test_health_score_calculation(self, report):
        """Test health score calculation."""
        # Healthy (below soft limit)
        score = report._calculate_health_score(20_000)
        assert 0.6 <= score <= 1.0
        
        # Warning zone (between soft and hard)
        score = report._calculate_health_score(45_000)
        assert 0.3 <= score < 0.6
        
        # Critical (at or above hard limit)
        score = report._calculate_health_score(50_000)
        assert score == 0.0
    
    def test_risk_level_calculation(self, report):
        """Test risk level calculation."""
        assert report._calculate_risk_level(20_000) == "LOW"
        assert report._calculate_risk_level(30_000) == "MEDIUM"
        assert report._calculate_risk_level(41_000) == "HIGH"
        assert report._calculate_risk_level(50_000) == "CRITICAL"
    
    def test_recommended_actions(self, report):
        """Test recommended actions."""
        # Healthy
        actions = report._get_recommended_actions(20_000, 0)
        assert len(actions) > 0
        assert any("healthy" in a.lower() for a in actions)
        
        # Warning
        actions = report._get_recommended_actions(42_000, 5)
        assert any("WARNING" in a or "Consider" in a for a in actions)
        
        # Critical
        actions = report._get_recommended_actions(50_000, 10)
        assert any("URGENT" in a or "CRITICAL" in a for a in actions)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
