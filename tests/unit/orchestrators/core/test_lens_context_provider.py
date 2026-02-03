"""
Tests for LENSContextProvider Service.

Authority: Phase 20 Component #1 (AC_LENS_COMPANY_001)
Rule: CORE-008 (TDD First)
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
from pathlib import Path

from cortex.orchestrators.core.lens_context_provider import (
    LENSContextProvider,
    LENSCache,
)


class TestLENSCache:
    """Test LENSCache implementation."""
    
    @pytest.fixture
    def cache(self) -> LENSCache:
        """Create LENSCache instance."""
        return LENSCache(max_size_mb=10)
    
    def test_cache_initializes(self, cache: LENSCache):
        """Test cache initializes with correct defaults."""
        assert cache is not None
        assert cache.max_size_mb == 10
        assert cache.get_size() == 0
    
    def test_cache_set_and_get(self, cache: LENSCache):
        """Test basic cache set/get operations."""
        key = "test_key"
        value = {"data": "test_value"}
        
        cache.set(key, value, ttl=300)
        retrieved = cache.get(key)
        
        assert retrieved == value
    
    def test_cache_ttl_expiration(self, cache: LENSCache):
        """Test cache entry expires after TTL."""
        key = "test_key"
        value = {"data": "test_value"}
        
        cache.set(key, value, ttl=1)  # 1 second TTL
        time.sleep(1.1)  # Wait for expiration
        
        retrieved = cache.get(key)
        assert retrieved is None
    
    def test_cache_invalidate(self, cache: LENSCache):
        """Test cache invalidation."""
        key = "test_key"
        value = {"data": "test_value"}
        
        cache.set(key, value, ttl=300)
        cache.invalidate(key)
        
        retrieved = cache.get(key)
        assert retrieved is None
    
    def test_cache_clear(self, cache: LENSCache):
        """Test cache clear all entries."""
        cache.set("key1", {"data": "value1"}, ttl=300)
        cache.set("key2", {"data": "value2"}, ttl=300)
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_cache_size_limit(self, cache: LENSCache):
        """Test cache enforces size limit."""
        # Create cache with 1MB limit
        small_cache = LENSCache(max_size_mb=1)
        
        # Add entries until limit reached
        for i in range(100):
            key = f"key_{i}"
            # Large value (~100KB)
            value = {"data": "x" * 100000}
            small_cache.set(key, value, ttl=300)
        
        # Cache should enforce size limit
        assert small_cache.get_size() <= 1.5  # Allow 50% overhead


class TestLENSContextProvider:
    """Test LENSContextProvider service."""
    
    @pytest.fixture
    def provider(self) -> LENSContextProvider:
        """Create LENSContextProvider instance."""
        return LENSContextProvider(cache_ttl=300, max_cache_mb=10)
    
    @pytest.fixture
    def mock_lens_orchestrator(self) -> Mock:
        """Mock LENSOrchestrator."""
        mock = Mock()
        mock.analyze_file.return_value = {
            "git_analysis": {"commits": 10},
            "ast_analysis": {"complexity": 5},
            "comment_analysis": {"todos": 2}
        }
        return mock
    
    def test_provider_initializes(self, provider: LENSContextProvider):
        """Test provider initializes correctly."""
        assert provider is not None
        assert provider.cache_ttl == 300
        assert provider.cache is not None
    
    @patch("cortex.orchestrators.core.lens_context_provider.LENSOrchestrator")
    def test_get_context_cache_miss(
        self, 
        mock_lens_class: Mock,
        provider: LENSContextProvider,
        mock_lens_orchestrator: Mock
    ):
        """Test get_context with cache miss."""
        mock_lens_class.return_value = mock_lens_orchestrator
        
        file_path = "/test/file.py"
        company_name = "test-company"
        intent_type = "IMPLEMENT"
        
        context = provider.get_context(file_path, company_name, intent_type)
        
        assert context is not None
        assert "git_analysis" in context
        assert "_metadata" in context
        assert context["_metadata"]["cache_hit"] is False
    
    @patch("cortex.orchestrators.core.lens_context_provider.LENSOrchestrator")
    def test_get_context_cache_hit(
        self,
        mock_lens_class: Mock,
        provider: LENSContextProvider,
        mock_lens_orchestrator: Mock
    ):
        """Test get_context with cache hit."""
        mock_lens_class.return_value = mock_lens_orchestrator
        
        file_path = "/test/file.py"
        company_name = "test-company"
        intent_type = "IMPLEMENT"
        
        # First call - cache miss
        context1 = provider.get_context(file_path, company_name, intent_type)
        
        # Second call - cache hit
        context2 = provider.get_context(file_path, company_name, intent_type)
        
        assert context2["_metadata"]["cache_hit"] is True
        # LENS should only be called once
        assert mock_lens_orchestrator.analyze_file.call_count == 1
    
    def test_should_activate_valid_intents(self, provider: LENSContextProvider):
        """Test intent-based activation for valid intents."""
        valid_intents = ["IMPLEMENT", "FIX", "REFACTOR", "ANALYZE"]
        
        for intent in valid_intents:
            assert provider._should_activate(intent) is True
    
    def test_should_activate_invalid_intents(self, provider: LENSContextProvider):
        """Test intent-based activation rejects invalid intents."""
        invalid_intents = ["HELP", "EXPLAIN", "DOCUMENT", "TEST"]
        
        for intent in invalid_intents:
            assert provider._should_activate(intent) is False
    
    def test_get_context_skips_inactive_intents(self, provider: LENSContextProvider):
        """Test get_context returns None for inactive intents."""
        file_path = "/test/file.py"
        company_name = "test-company"
        intent_type = "HELP"
        
        context = provider.get_context(file_path, company_name, intent_type)
        
        assert context is None
    
    @patch("cortex.orchestrators.core.lens_context_provider.LENSOrchestrator")
    def test_failsafe_fallback(
        self,
        mock_lens_class: Mock,
        provider: LENSContextProvider
    ):
        """Test fail-safe fallback when LENS unavailable."""
        mock_lens_class.side_effect = Exception("LENS unavailable")
        
        file_path = "/test/file.py"
        company_name = "test-company"
        intent_type = "IMPLEMENT"
        
        context = provider.get_context(file_path, company_name, intent_type)
        
        # Should return empty context instead of raising
        assert context is not None
        assert context["_metadata"]["error"] is not None
        assert "LENS unavailable" in context["_metadata"]["error"]
    
    @patch("cortex.orchestrators.core.lens_context_provider.LENSOrchestrator")
    def test_performance_cache_hit(
        self,
        mock_lens_class: Mock,
        provider: LENSContextProvider,
        mock_lens_orchestrator: Mock
    ):
        """Test performance with cache hit (<200ms)."""
        mock_lens_class.return_value = mock_lens_orchestrator
        
        file_path = "/test/file.py"
        company_name = "test-company"
        intent_type = "IMPLEMENT"
        
        # Prime cache
        provider.get_context(file_path, company_name, intent_type)
        
        # Measure cached retrieval
        start_time = time.time()
        provider.get_context(file_path, company_name, intent_type)
        elapsed = (time.time() - start_time) * 1000  # ms
        
        assert elapsed < 200  # <200ms requirement
    
    def test_cache_invalidation_on_file_change(self, provider: LENSContextProvider):
        """Test cache invalidation when file is modified."""
        file_path = "/test/file.py"
        
        provider.invalidate_cache(file_path)
        
        # Verify all entries for this file are invalidated
        cache_key1 = provider._make_cache_key(file_path, "company1")
        cache_key2 = provider._make_cache_key(file_path, "company2")
        
        assert provider.cache.get(cache_key1) is None
        assert provider.cache.get(cache_key2) is None


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
