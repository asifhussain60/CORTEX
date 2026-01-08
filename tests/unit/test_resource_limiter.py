"""
Tests for Resource Limiter middleware.

This module provides comprehensive tests for resource management including:
- Resource quotas
- Concurrent operation limits
- Hard and soft limits
- Resource tracking and enforcement

Author: CORTEX
Feature: feat05-resilience Phase 1
Correlation ID: FEAT05-P1-T1.1
"""

import pytest
import time
import threading

from src.orchestrators.middleware.resource_limiter import (
    ResourceLimiter,
    ResourceQuota,
    ResourceLimitExceeded,
    ResourceType
)


class TestResourceQuota:
    """Tests for ResourceQuota configuration."""
    
    def test_create_quota(self):
        """Test creating a resource quota."""
        quota = ResourceQuota(
            resource_type=ResourceType.MEMORY,
            limit=1024,
            current=0,
            hard_limit=True
        )
        
        assert quota.resource_type == ResourceType.MEMORY
        assert quota.limit == 1024
        assert quota.current == 0
        assert quota.hard_limit is True
        
    def test_soft_limit_quota(self):
        """Test creating a soft limit quota."""
        quota = ResourceQuota(
            resource_type=ResourceType.CPU,
            limit=100,
            hard_limit=False
        )
        
        assert quota.hard_limit is False


class TestResourceLimiter:
    """Tests for ResourceLimiter middleware."""
    
    @pytest.fixture
    def limiter(self):
        """Create resource limiter for testing."""
        return ResourceLimiter()
        
    def test_initialization(self, limiter):
        """Test limiter initialization."""
        assert limiter is not None
        assert hasattr(limiter, '_quotas')
        assert hasattr(limiter, '_lock')
        
    def test_set_quota(self, limiter):
        """Test setting a resource quota."""
        limiter.set_quota(ResourceType.MEMORY, limit=512, hard_limit=True)
        
        usage = limiter.get_usage(ResourceType.MEMORY)
        assert usage['limit'] == 512
        assert usage['current'] == 0
        assert usage['available'] == 512
        
    def test_acquire_resource_within_limit(self, limiter):
        """Test acquiring resource within limit."""
        limiter.set_quota(ResourceType.CONCURRENT_OPERATIONS, limit=5)
        
        # Acquire within limit
        result = limiter.acquire_resource(ResourceType.CONCURRENT_OPERATIONS, amount=3)
        assert result is True
        
        usage = limiter.get_usage(ResourceType.CONCURRENT_OPERATIONS)
        assert usage['current'] == 3
        assert usage['available'] == 2
        
    def test_acquire_resource_at_limit(self, limiter):
        """Test acquiring resource at exact limit."""
        limiter.set_quota(ResourceType.CONCURRENT_OPERATIONS, limit=5)
        
        result = limiter.acquire_resource(ResourceType.CONCURRENT_OPERATIONS, amount=5)
        assert result is True
        
        usage = limiter.get_usage(ResourceType.CONCURRENT_OPERATIONS)
        assert usage['current'] == 5
        assert usage['available'] == 0
        
    def test_acquire_resource_exceeds_hard_limit(self, limiter):
        """Test acquiring resource that exceeds hard limit."""
        limiter.set_quota(ResourceType.CONCURRENT_OPERATIONS, limit=5, hard_limit=True)
        
        # Use up to limit
        limiter.acquire_resource(ResourceType.CONCURRENT_OPERATIONS, amount=5)
        
        # Try to exceed - should fail
        result = limiter.acquire_resource(ResourceType.CONCURRENT_OPERATIONS, amount=1)
        assert result is False
        
        usage = limiter.get_usage(ResourceType.CONCURRENT_OPERATIONS)
        assert usage['current'] == 5  # Should not have increased
        
    def test_acquire_resource_exceeds_soft_limit(self, limiter):
        """Test acquiring resource that exceeds soft limit."""
        limiter.set_quota(ResourceType.CPU, limit=80, hard_limit=False)
        
        # Exceed soft limit - should succeed with warning
        result = limiter.acquire_resource(ResourceType.CPU, amount=100)
        assert result is True
        
        usage = limiter.get_usage(ResourceType.CPU)
        assert usage['current'] == 100  # Should have increased despite limit
        
    def test_release_resource(self, limiter):
        """Test releasing a resource."""
        limiter.set_quota(ResourceType.MEMORY, limit=1024)
        
        # Acquire then release
        limiter.acquire_resource(ResourceType.MEMORY, amount=512)
        usage = limiter.get_usage(ResourceType.MEMORY)
        assert usage['current'] == 512
        
        limiter.release_resource(ResourceType.MEMORY, amount=256)
        usage = limiter.get_usage(ResourceType.MEMORY)
        assert usage['current'] == 256
        assert usage['available'] == 768
        
    def test_release_resource_below_zero(self, limiter):
        """Test that releasing doesn't go below zero."""
        limiter.set_quota(ResourceType.MEMORY, limit=1024)
        
        limiter.acquire_resource(ResourceType.MEMORY, amount=100)
        limiter.release_resource(ResourceType.MEMORY, amount=200)
        
        usage = limiter.get_usage(ResourceType.MEMORY)
        assert usage['current'] == 0  # Should not go negative
        
    def test_resource_scope_success(self, limiter):
        """Test resource_scope context manager."""
        limiter.set_quota(ResourceType.FILE_HANDLES, limit=10)
        
        with limiter.resource_scope(ResourceType.FILE_HANDLES, amount=3):
            usage = limiter.get_usage(ResourceType.FILE_HANDLES)
            assert usage['current'] == 3
            
        # After context, should be released
        usage = limiter.get_usage(ResourceType.FILE_HANDLES)
        assert usage['current'] == 0
        
    def test_resource_scope_exceeds_limit(self, limiter):
        """Test resource_scope when limit exceeded."""
        limiter.set_quota(ResourceType.CONCURRENT_OPERATIONS, limit=5, hard_limit=True)
        
        # Use up all quota
        limiter.acquire_resource(ResourceType.CONCURRENT_OPERATIONS, amount=5)
        
        # Try to use more - should raise exception
        with pytest.raises(ResourceLimitExceeded):
            with limiter.resource_scope(ResourceType.CONCURRENT_OPERATIONS, amount=1):
                pass
                
        # Quota should not have changed
        usage = limiter.get_usage(ResourceType.CONCURRENT_OPERATIONS)
        assert usage['current'] == 5
        
    def test_resource_scope_exception_cleanup(self, limiter):
        """Test resource_scope cleans up on exception."""
        limiter.set_quota(ResourceType.MEMORY, limit=1024)
        
        with pytest.raises(ValueError):
            with limiter.resource_scope(ResourceType.MEMORY, amount=512):
                usage = limiter.get_usage(ResourceType.MEMORY)
                assert usage['current'] == 512
                raise ValueError("Test error")
                
        # Should have cleaned up despite exception
        usage = limiter.get_usage(ResourceType.MEMORY)
        assert usage['current'] == 0
        
    def test_reset_quota(self, limiter):
        """Test resetting a quota."""
        limiter.set_quota(ResourceType.CPU, limit=100)
        limiter.acquire_resource(ResourceType.CPU, amount=75)
        
        usage = limiter.get_usage(ResourceType.CPU)
        assert usage['current'] == 75
        
        limiter.reset_quota(ResourceType.CPU)
        
        usage = limiter.get_usage(ResourceType.CPU)
        assert usage['current'] == 0
        assert usage['limit'] == 100  # Limit unchanged
        
    def test_get_usage_no_quota(self, limiter):
        """Test getting usage when no quota set."""
        usage = limiter.get_usage(ResourceType.MEMORY)
        
        assert usage['current'] == 0
        assert usage['limit'] == 0
        assert usage['available'] == 0
        
    def test_acquire_without_quota(self, limiter):
        """Test acquiring resource when no quota set."""
        # Should succeed - no quota means no limit
        result = limiter.acquire_resource(ResourceType.MEMORY, amount=9999)
        assert result is True


class TestConcurrentAccess:
    """Tests for concurrent access to resource limiter."""
    
    def test_concurrent_acquire(self):
        """Test concurrent resource acquisition."""
        limiter = ResourceLimiter()
        limiter.set_quota(ResourceType.CONCURRENT_OPERATIONS, limit=100)
        
        results = []
        
        def worker(worker_id: int):
            result = limiter.acquire_resource(ResourceType.CONCURRENT_OPERATIONS, amount=1)
            results.append((worker_id, result))
            
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(50)]
        
        for t in threads:
            t.start()
            
        for t in threads:
            t.join()
            
        # All should succeed
        assert len(results) == 50
        assert all(result for _, result in results)
        
        usage = limiter.get_usage(ResourceType.CONCURRENT_OPERATIONS)
        assert usage['current'] == 50
        
    def test_concurrent_resource_scope(self):
        """Test concurrent resource_scope usage."""
        limiter = ResourceLimiter()
        limiter.set_quota(ResourceType.CONCURRENT_OPERATIONS, limit=20)
        
        active_count = []
        
        def worker(worker_id: int):
            with limiter.resource_scope(ResourceType.CONCURRENT_OPERATIONS, amount=1):
                usage = limiter.get_usage(ResourceType.CONCURRENT_OPERATIONS)
                active_count.append(usage['current'])
                time.sleep(0.01)
                
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        
        for t in threads:
            t.start()
            
        for t in threads:
            t.join()
            
        # Should have seen concurrent operations
        assert max(active_count) >= 2
        
        # Should be back to zero
        usage = limiter.get_usage(ResourceType.CONCURRENT_OPERATIONS)
        assert usage['current'] == 0


class TestIntegration:
    """Integration tests for resource limiter."""
    
    def test_multiple_resource_types(self):
        """Test managing multiple resource types."""
        limiter = ResourceLimiter()
        
        limiter.set_quota(ResourceType.MEMORY, limit=1024)
        limiter.set_quota(ResourceType.CPU, limit=100)
        limiter.set_quota(ResourceType.CONCURRENT_OPERATIONS, limit=10)
        
        limiter.acquire_resource(ResourceType.MEMORY, amount=512)
        limiter.acquire_resource(ResourceType.CPU, amount=75)
        limiter.acquire_resource(ResourceType.CONCURRENT_OPERATIONS, amount=5)
        
        mem_usage = limiter.get_usage(ResourceType.MEMORY)
        cpu_usage = limiter.get_usage(ResourceType.CPU)
        ops_usage = limiter.get_usage(ResourceType.CONCURRENT_OPERATIONS)
        
        assert mem_usage['current'] == 512
        assert cpu_usage['current'] == 75
        assert ops_usage['current'] == 5
        
    def test_full_lifecycle(self):
        """Test full resource lifecycle."""
        limiter = ResourceLimiter()
        limiter.set_quota(ResourceType.FILE_HANDLES, limit=5, hard_limit=True)
        
        # Acquire resources
        for i in range(5):
            result = limiter.acquire_resource(ResourceType.FILE_HANDLES, amount=1)
            assert result is True
            
        # At limit
        usage = limiter.get_usage(ResourceType.FILE_HANDLES)
        assert usage['current'] == 5
        assert usage['available'] == 0
        
        # Cannot acquire more
        result = limiter.acquire_resource(ResourceType.FILE_HANDLES, amount=1)
        assert result is False
        
        # Release some
        limiter.release_resource(ResourceType.FILE_HANDLES, amount=2)
        
        # Can acquire again
        result = limiter.acquire_resource(ResourceType.FILE_HANDLES, amount=1)
        assert result is True
        
        usage = limiter.get_usage(ResourceType.FILE_HANDLES)
        assert usage['current'] == 4
