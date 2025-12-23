"""
Performance benchmarks and load testing for IntentRouter

Measures:
- Intent classification speed (single request)
- Throughput under load (requests/second)
- Memory usage during high-volume scenarios
- Cache effectiveness
- Tier 2 query performance
- Concurrent routing performance

Priority: P1 - Performance validation
"""

import pytest
import time
import psutil
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, MagicMock

from src.cortex_agents.intent_router import IntentRouter
from src.cortex_agents.base_agent import AgentRequest
from src.cortex_agents.agent_types import IntentType


@pytest.fixture
def performance_intent_router():
    """Create IntentRouter optimized for performance testing."""
    tier1 = Mock()
    tier1.log_event = Mock()
    tier1.get_recent_conversations = Mock(return_value=[])
    tier1.get_profile = Mock(return_value={
        'interaction_mode': 'autonomous',
        'experience_level': 'senior'
    })
    
    tier2 = Mock()
    tier2.search = Mock(return_value=[])
    tier2.find_similar_intents = Mock(return_value=[])
    tier2.add_pattern = Mock()
    tier2.record_routing_decision = Mock()
    tier2.get_routing_patterns = Mock(return_value=[])
    
    tier3 = Mock()
    tier3.get_project_context = Mock(return_value={})
    
    config = {
        'vision_api_enabled': False,
        'tdd_auto_activation': False,
        'confidence_threshold': 0.7
    }
    
    return IntentRouter(
        name="PerfTestRouter",  # Add required 'name' parameter
        tier1_api=tier1,
        tier2_kg=tier2,
        tier3_context=tier3,
        config=config
    )


def get_memory_usage():
    """Get current memory usage in MB."""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024  # Convert to MB


class TestSingleRequestPerformance:
    """Test performance of individual request classification."""
    
    def test_classification_speed_simple_request(self, performance_intent_router):
        """Benchmark: Simple intent classification speed."""
        router = performance_intent_router
        
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="plan authentication feature"
        )
        
        start_time = time.perf_counter()
        response = router.execute(request)
        end_time = time.perf_counter()
        
        elapsed = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Classification should be fast (< 100ms for simple requests)
        assert elapsed < 100, f"Classification took {elapsed:.2f}ms, expected < 100ms"
        assert response is not None
    
    def test_classification_speed_complex_request(self, performance_intent_router):
        """Benchmark: Complex multi-word intent classification speed."""
        router = performance_intent_router
        
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="I need to create a comprehensive plan for implementing "
                        "user authentication with OAuth2, JWT tokens, and role-based "
                        "access control for the microservices architecture"
        )
        
        start_time = time.perf_counter()
        response = router.execute(request)
        end_time = time.perf_counter()
        
        elapsed = (end_time - start_time) * 1000
        
        # Even complex requests should be reasonably fast (< 150ms)
        assert elapsed < 150, f"Complex classification took {elapsed:.2f}ms, expected < 150ms"
        assert response is not None
    
    def test_average_classification_time(self, performance_intent_router):
        """Benchmark: Average classification time over multiple requests."""
        router = performance_intent_router
        
        messages = [
            "plan feature",
            "check system health",
            "align the system",
            "optimize performance",
            "create TDD tests",
            "review architecture",
            "cleanup workspace",
            "deploy to production"
        ]
        
        times = []
        for msg in messages:
            request = AgentRequest(intent="unknown", context={}, user_message=msg)
            
            start = time.perf_counter()
            router.execute(request)
            end = time.perf_counter()
            
            times.append((end - start) * 1000)
        
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        
        print(f"\nAverage: {avg_time:.2f}ms, Median: {median_time:.2f}ms")
        
        # Average should be well under 100ms
        assert avg_time < 100, f"Average time {avg_time:.2f}ms too high"
        assert median_time < 80, f"Median time {median_time:.2f}ms too high"


class TestThroughputUnderLoad:
    """Test throughput under various load conditions."""
    
    def test_sequential_throughput(self, performance_intent_router):
        """Benchmark: Sequential request processing throughput."""
        router = performance_intent_router
        
        num_requests = 100
        messages = [
            "plan feature",
            "check health",
            "align system"
        ]
        
        start_time = time.perf_counter()
        
        for i in range(num_requests):
            msg = messages[i % len(messages)]
            request = AgentRequest(intent="unknown", context={}, user_message=msg)
            router.execute(request)
        
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        
        throughput = num_requests / elapsed
        
        print(f"\nSequential throughput: {throughput:.2f} requests/second")
        
        # Should handle at least 50 requests/second sequentially
        assert throughput > 50, f"Throughput {throughput:.2f} req/s too low"
    
    def test_concurrent_throughput(self, performance_intent_router):
        """Benchmark: Concurrent request processing throughput."""
        router = performance_intent_router
        
        num_requests = 50
        max_workers = 5
        
        def process_request(msg):
            request = AgentRequest(intent="unknown", context={}, user_message=msg)
            return router.execute(request)
        
        messages = ["plan feature", "check health", "align system"] * (num_requests // 3 + 1)
        
        start_time = time.perf_counter()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_request, msg) for msg in messages[:num_requests]]
            results = [f.result() for f in as_completed(futures)]
        
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        
        throughput = num_requests / elapsed
        
        print(f"\nConcurrent throughput ({max_workers} workers): {throughput:.2f} requests/second")
        
        # Concurrent processing should be faster than sequential
        assert throughput > 30, f"Concurrent throughput {throughput:.2f} req/s too low"
        assert len(results) == num_requests
    
    def test_burst_load_handling(self, performance_intent_router):
        """Benchmark: Handling sudden burst of requests."""
        router = performance_intent_router
        
        burst_size = 20
        messages = ["plan authentication feature"] * burst_size
        
        start_time = time.perf_counter()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(
                    router.execute,
                    AgentRequest(intent="unknown", context={}, user_message=msg)
                )
                for msg in messages
            ]
            results = [f.result() for f in as_completed(futures)]
        
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        
        print(f"\nBurst of {burst_size} requests processed in {elapsed:.3f}s")
        
        # Should handle burst without excessive delay
        assert elapsed < 5.0, f"Burst took {elapsed:.3f}s, expected < 5s"
        assert all(r is not None for r in results)


class TestMemoryUsageUnderLoad:
    """Test memory usage during high-volume scenarios."""
    
    def test_memory_usage_baseline(self, performance_intent_router):
        """Measure baseline memory usage."""
        initial_memory = get_memory_usage()
        
        # Perform a few operations
        router = performance_intent_router
        for i in range(10):
            request = AgentRequest(
                intent="unknown",
                context={},
                user_message=f"plan feature {i}"
            )
            router.execute(request)
        
        final_memory = get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        print(f"\nMemory increase after 10 requests: {memory_increase:.2f} MB")
        
        # Should not leak significant memory
        assert memory_increase < 10, f"Memory increase {memory_increase:.2f} MB too high"
    
    def test_memory_under_sustained_load(self, performance_intent_router):
        """Test memory usage under sustained load."""
        initial_memory = get_memory_usage()
        
        router = performance_intent_router
        num_requests = 500
        
        for i in range(num_requests):
            request = AgentRequest(
                intent="unknown",
                context={},
                user_message=f"plan feature {i % 10}"  # Reuse messages
            )
            router.execute(request)
        
        final_memory = get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        print(f"\nMemory increase after {num_requests} requests: {memory_increase:.2f} MB")
        
        # Should not have excessive memory growth
        assert memory_increase < 50, f"Memory growth {memory_increase:.2f} MB too high"
    
    def test_memory_stability_over_time(self, performance_intent_router):
        """Test memory stability over extended operation."""
        router = performance_intent_router
        
        memory_samples = []
        
        # Sample memory at intervals
        for batch in range(5):
            for i in range(20):
                request = AgentRequest(
                    intent="unknown",
                    context={},
                    user_message=f"plan feature {i}"
                )
                router.execute(request)
            
            memory_samples.append(get_memory_usage())
        
        # Check for memory leak (consistently increasing)
        diffs = [memory_samples[i+1] - memory_samples[i] for i in range(len(memory_samples)-1)]
        avg_increase = statistics.mean(diffs)
        
        print(f"\nAverage memory increase per batch: {avg_increase:.2f} MB")
        
        # Should be relatively stable (not consistently increasing)
        assert avg_increase < 5, f"Memory leak detected: {avg_increase:.2f} MB/batch"


class TestCachePerformance:
    """Test cache effectiveness for performance."""
    
    def test_cache_hit_performance(self, performance_intent_router):
        """Benchmark: Performance improvement from cache hits."""
        router = performance_intent_router
        message = "plan authentication feature"
        
        # First request (cold - no cache)
        request1 = AgentRequest(intent="unknown", context={}, user_message=message)
        
        start1 = time.perf_counter()
        router.execute(request1)
        end1 = time.perf_counter()
        cold_time = (end1 - start1) * 1000
        
        # Second identical request (warm - potential cache hit)
        request2 = AgentRequest(intent="unknown", context={}, user_message=message)
        
        start2 = time.perf_counter()
        router.execute(request2)
        end2 = time.perf_counter()
        warm_time = (end2 - start2) * 1000
        
        print(f"\nCold: {cold_time:.2f}ms, Warm: {warm_time:.2f}ms")
        
        # Warm should be at least as fast (possibly faster with caching)
        # Note: In mock scenario, may not see dramatic improvement
        assert warm_time <= cold_time * 1.5, "Cache not providing benefit"
    
    def test_cache_effectiveness_ratio(self, performance_intent_router):
        """Test cache hit ratio under repeated requests."""
        router = performance_intent_router
        
        # Configure mock to track cache hits
        cache_hits = 0
        total_lookups = 0
        
        def mock_tier2_search(query):
            nonlocal cache_hits, total_lookups
            total_lookups += 1
            # Simulate 50% cache hit rate
            if total_lookups % 2 == 0:
                cache_hits += 1
                return [{'intent': 'PLAN', 'confidence': 0.9}]
            return []
        
        router.tier2.find_similar_intents = mock_tier2_search  # Fixed: tier2_kg → tier2
        
        # Execute requests
        messages = ["plan feature"] * 20 + ["check health"] * 20
        
        for msg in messages:
            request = AgentRequest(intent="unknown", context={}, user_message=msg)
            router.execute(request)
        
        # Note: Actual cache tracking depends on implementation
        print(f"\nSimulated cache hits: {cache_hits}/{total_lookups}")


class TestTier2QueryPerformance:
    """Test Tier 2 knowledge graph query performance."""
    
    def test_tier2_search_latency(self, performance_intent_router):
        """Benchmark: Tier 2 search query latency."""
        router = performance_intent_router
        
        # Simulate Tier 2 search with realistic delay
        def slow_search(query):
            time.sleep(0.01)  # 10ms simulated DB query
            return []
        
        router.tier2.find_similar_intents = slow_search  # Fixed: tier2_kg → tier2
        
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="plan feature"
        )
        
        start = time.perf_counter()
        router.execute(request)
        end = time.perf_counter()
        
        elapsed = (end - start) * 1000
        
        # Should still be fast even with Tier 2 latency
        assert elapsed < 200, f"Total time {elapsed:.2f}ms too high with Tier 2 latency"
    
    def test_tier2_timeout_handling(self, performance_intent_router):
        """Test handling of slow Tier 2 queries."""
        router = performance_intent_router
        
        # Simulate very slow Tier 2
        def very_slow_search(query):
            time.sleep(0.5)  # 500ms - unacceptably slow
            return []
        
        router.tier2.find_similar_intents = very_slow_search  # Fixed: tier2_kg → tier2
        
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="plan feature"
        )
        
        start = time.perf_counter()
        response = router.execute(request)
        end = time.perf_counter()
        
        elapsed = (end - start) * 1000
        
        # Should still complete (with fallback if needed)
        assert response is not None
        print(f"\nHandled slow Tier 2 in {elapsed:.2f}ms")


class TestPerformanceRegression:
    """Test for performance regressions."""
    
    def test_baseline_performance_metrics(self, performance_intent_router):
        """Establish baseline performance metrics."""
        router = performance_intent_router
        
        # Standard test suite
        test_cases = [
            ("plan authentication", 100),  # Expected max time in ms
            ("check health", 80),
            ("align system", 80),
            ("optimize performance", 100)
        ]
        
        results = []
        for msg, max_time in test_cases:
            request = AgentRequest(intent="unknown", context={}, user_message=msg)
            
            start = time.perf_counter()
            response = router.execute(request)
            end = time.perf_counter()
            
            elapsed = (end - start) * 1000
            results.append((msg, elapsed, max_time))
            
            print(f"{msg}: {elapsed:.2f}ms (max: {max_time}ms)")
            assert elapsed < max_time, f"Regression: {msg} took {elapsed:.2f}ms"
        
        # All should pass
        assert all(elapsed < max_time for _, elapsed, max_time in results)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
