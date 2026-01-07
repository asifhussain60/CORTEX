"""
CORTEX 6.0 - Trie Router Tests

TDD tests for the Trie-based pattern router.
Phase 4: Pattern Router Implementation

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import time
import threading
from pathlib import Path
from typing import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.orchestrators.routing.trie_router import (
    TrieRouter,
    TrieNode,
    RouteConfig,
    RouteMatch,
    MatchType,
    get_trie_router,
    set_trie_router,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def router() -> Generator[TrieRouter, None, None]:
    """Create a fresh Trie router."""
    router = TrieRouter(enable_logging=False)
    yield router
    router.clear()


@pytest.fixture
def populated_router(router: TrieRouter) -> TrieRouter:
    """Create a router with sample routes."""
    # Exact routes
    router.add_exact_route("plan", "planning_orchestrator")
    router.add_exact_route("help", "help_orchestrator")
    router.add_exact_route("debug", "debug_orchestrator")
    
    # Prefix routes
    router.add_prefix_route("create a plan", "planning_orchestrator")
    router.add_prefix_route("start tdd", "tdd_orchestrator")
    router.add_prefix_route("run tests", "test_orchestrator")
    
    # Keyword routes - use single words that can be matched
    router.add_keyword_route(["investigate", "investigation"], "investigation_orchestrator")
    router.add_keyword_route(["vacuum", "clean"], "vacuum_orchestrator")
    
    # Regex routes
    router.add_regex_route(r"ado\s+(story|feature|bug)", "ado_orchestrator")
    
    return router


# =============================================================================
# TASK 1.4.2: BASIC FUNCTIONALITY TESTS
# =============================================================================

class TestTrieRouterBasics:
    """Test basic Trie router functionality."""
    
    def test_router_initialization(self):
        """Test router can be initialized."""
        router = TrieRouter()
        assert router is not None
        assert router.get_stats()['total_routes'] == 0
    
    def test_add_exact_route(self, router: TrieRouter):
        """Test adding exact match routes."""
        router.add_exact_route("test", "test_orchestrator")
        stats = router.get_stats()
        assert stats['exact_routes'] == 1
    
    def test_add_prefix_route(self, router: TrieRouter):
        """Test adding prefix match routes."""
        router.add_prefix_route("create something", "create_orchestrator")
        stats = router.get_stats()
        assert stats['prefix_routes'] == 1
    
    def test_add_keyword_route(self, router: TrieRouter):
        """Test adding keyword match routes."""
        router.add_keyword_route(["test", "verify"], "test_orchestrator")
        stats = router.get_stats()
        assert stats['keyword_routes'] == 1
    
    def test_add_regex_route(self, router: TrieRouter):
        """Test adding regex match routes."""
        router.add_regex_route(r"test\s+\d+", "test_orchestrator")
        stats = router.get_stats()
        assert stats['regex_routes'] == 1
    
    def test_invalid_confidence_raises(self, router: TrieRouter):
        """Test that invalid confidence raises ValueError."""
        with pytest.raises(ValueError):
            router.add_exact_route("test", "test_orchestrator", confidence=1.5)
    
    def test_invalid_regex_raises(self, router: TrieRouter):
        """Test that invalid regex raises ValueError."""
        with pytest.raises(ValueError):
            router.add_regex_route("[invalid", "test_orchestrator")


# =============================================================================
# TASK 1.4.3: MATCHING TESTS
# =============================================================================

class TestExactMatching:
    """Test exact O(1) matching."""
    
    def test_exact_match(self, populated_router: TrieRouter):
        """Test exact string matching."""
        match = populated_router.match("plan")
        
        assert match.is_matched
        assert match.orchestrator_id == "planning_orchestrator"
        assert match.match_type == MatchType.EXACT
        assert match.confidence == 1.0
    
    def test_exact_match_case_insensitive(self, populated_router: TrieRouter):
        """Test exact matching is case-insensitive."""
        match = populated_router.match("PLAN")
        
        assert match.is_matched
        assert match.orchestrator_id == "planning_orchestrator"
    
    def test_exact_match_with_whitespace(self, populated_router: TrieRouter):
        """Test exact matching trims whitespace."""
        match = populated_router.match("  plan  ")
        
        assert match.is_matched
        assert match.orchestrator_id == "planning_orchestrator"
    
    def test_exact_no_match(self, populated_router: TrieRouter):
        """Test no match returns empty result."""
        match = populated_router.match("nonexistent")
        
        assert not match.is_matched
        assert match.orchestrator_id is None
        assert match.match_type == MatchType.NONE


class TestPrefixMatching:
    """Test Trie-based prefix matching."""
    
    def test_prefix_match(self, populated_router: TrieRouter):
        """Test prefix matching."""
        match = populated_router.match("create a plan for authentication")
        
        assert match.is_matched
        assert match.orchestrator_id == "planning_orchestrator"
        assert match.match_type == MatchType.PREFIX
    
    def test_prefix_exact_match(self, populated_router: TrieRouter):
        """Test prefix matches exact phrase."""
        match = populated_router.match("create a plan")
        
        assert match.is_matched
        assert match.orchestrator_id == "planning_orchestrator"
    
    def test_prefix_partial_no_match(self, populated_router: TrieRouter):
        """Test partial prefix doesn't match."""
        match = populated_router.match("create a")  # Incomplete phrase
        
        # Should NOT match "create a plan" orchestrator
        assert not match.is_matched or match.match_type != MatchType.PREFIX
    
    def test_multiple_prefix_routes(self, router: TrieRouter):
        """Test multiple prefix routes with priority."""
        router.add_prefix_route("create a", "generic_orchestrator", priority=100)
        router.add_prefix_route("create a plan", "planning_orchestrator", priority=50)
        
        # Longer match should still work with higher priority
        match = router.match("create a plan for something")
        
        assert match.is_matched
        assert match.orchestrator_id == "planning_orchestrator"


class TestKeywordMatching:
    """Test keyword-based matching."""
    
    def test_keyword_match_single(self, populated_router: TrieRouter):
        """Test matching with single keyword."""
        match = populated_router.match("I need to investigate this bug")
        
        assert match.is_matched
        assert match.orchestrator_id == "investigation_orchestrator"
        assert match.match_type == MatchType.KEYWORD
    
    def test_keyword_match_multiple(self, populated_router: TrieRouter):
        """Test matching with multiple keywords from the list."""
        # "investigation" is one of the keywords registered
        match = populated_router.match("start the investigation of the issue")
        
        assert match.is_matched
        assert match.orchestrator_id == "investigation_orchestrator"
    
    def test_keyword_require_all(self, router: TrieRouter):
        """Test keyword matching requiring all keywords."""
        router.add_keyword_route(
            ["build", "deploy"],
            "cicd_orchestrator",
            require_all=True
        )
        
        # Single keyword shouldn't match
        match1 = router.match("build the project")
        assert not match1.is_matched
        
        # Both keywords should match
        match2 = router.match("build and deploy the project")
        assert match2.is_matched
        assert match2.orchestrator_id == "cicd_orchestrator"


class TestRegexMatching:
    """Test regex pattern matching."""
    
    def test_regex_match(self, populated_router: TrieRouter):
        """Test regex pattern matching."""
        match = populated_router.match("ado story for user authentication")
        
        assert match.is_matched
        assert match.orchestrator_id == "ado_orchestrator"
        assert match.match_type == MatchType.REGEX
    
    def test_regex_match_alternative(self, populated_router: TrieRouter):
        """Test regex with alternatives."""
        match1 = populated_router.match("ado feature for login")
        match2 = populated_router.match("ado bug in the system")
        
        assert match1.is_matched
        assert match2.is_matched
        assert match1.orchestrator_id == "ado_orchestrator"
        assert match2.orchestrator_id == "ado_orchestrator"
    
    def test_regex_no_match(self, populated_router: TrieRouter):
        """Test regex doesn't match unrelated input."""
        match = populated_router.match("ado task for something")
        
        # "task" is not in the regex pattern
        assert not match.is_matched or match.match_type != MatchType.REGEX


class TestPriorityRouting:
    """Test priority-based route selection."""
    
    def test_priority_exact_over_prefix(self, router: TrieRouter):
        """Test exact match takes priority over prefix."""
        router.add_exact_route("help", "exact_orchestrator", priority=100)
        router.add_prefix_route("help me", "prefix_orchestrator", priority=50)
        
        # "help" should match exact route
        match = router.match("help")
        assert match.orchestrator_id == "exact_orchestrator"
        
        # "help me with this" should match prefix
        match2 = router.match("help me with this")
        assert match2.orchestrator_id == "prefix_orchestrator"
    
    def test_priority_within_same_type(self, router: TrieRouter):
        """Test priority ordering within same match type."""
        router.add_exact_route("test", "low_priority", priority=100)
        router.add_exact_route("test", "high_priority", priority=10)
        
        match = router.match("test")
        assert match.orchestrator_id == "high_priority"
    
    def test_match_order_performance(self, router: TrieRouter):
        """Test that match order is exact → prefix → keyword → regex."""
        # Add all types with same trigger
        router.add_exact_route("debug", "exact_orch")
        router.add_prefix_route("debug", "prefix_orch")
        router.add_keyword_route(["debug"], "keyword_orch")
        router.add_regex_route(r"debug", "regex_orch")
        
        match = router.match("debug")
        
        # Exact should win
        assert match.match_type == MatchType.EXACT
        assert match.orchestrator_id == "exact_orch"


# =============================================================================
# TASK 1.4.4: PERFORMANCE TESTS
# =============================================================================

class TestPerformanceO1:
    """Test O(1) lookup performance."""
    
    def test_exact_lookup_time(self, router: TrieRouter):
        """Test exact lookup is under 5ms."""
        # Add 100 routes
        for i in range(100):
            router.add_exact_route(f"command{i}", f"orchestrator_{i}")
        
        # Measure lookup time
        start = time.perf_counter()
        for i in range(100):
            router.match(f"command{i}")
        elapsed = (time.perf_counter() - start) * 1000
        
        # Should complete 100 lookups in under 50ms (avg 0.5ms each)
        assert elapsed < 50, f"100 exact lookups took {elapsed:.2f}ms (>50ms SLA)"
    
    def test_prefix_lookup_time(self, router: TrieRouter):
        """Test prefix lookup is performant."""
        # Add deep prefix routes
        for i in range(100):
            router.add_prefix_route(f"create a plan for project {i}", f"orchestrator_{i}")
        
        # Measure lookup time
        start = time.perf_counter()
        for i in range(100):
            router.match(f"create a plan for project {i} with details")
        elapsed = (time.perf_counter() - start) * 1000
        
        # Should complete in under 100ms
        assert elapsed < 100, f"100 prefix lookups took {elapsed:.2f}ms (>100ms SLA)"
    
    def test_100_orchestrator_sla(self, router: TrieRouter):
        """Test <5ms for 100 orchestrators (SLA requirement)."""
        # Add 100 different orchestrator routes
        for i in range(100):
            router.add_exact_route(f"exact_{i}", f"orch_{i}")
            router.add_prefix_route(f"prefix {i}", f"orch_prefix_{i}")
            router.add_keyword_route([f"kw{i}"], f"orch_keyword_{i}")
        
        stats = router.get_stats()
        assert stats['total_routes'] >= 300
        
        # Warm up
        router.match("exact_50")
        
        # Measure single lookup
        times = []
        for _ in range(100):
            start = time.perf_counter()
            router.match("exact_50")
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        p95_time = sorted(times)[95]
        
        assert avg_time < 5, f"Average lookup {avg_time:.3f}ms exceeds 5ms SLA"
        assert p95_time < 10, f"P95 lookup {p95_time:.3f}ms exceeds 10ms"


class TestConcurrentAccess:
    """Test thread safety."""
    
    def test_concurrent_reads(self, populated_router: TrieRouter):
        """Test concurrent read access is safe."""
        results = []
        errors = []
        
        def read_worker(thread_id: int):
            try:
                for _ in range(100):
                    match = populated_router.match("plan")
                    if match.orchestrator_id != "planning_orchestrator":
                        errors.append(f"Thread {thread_id}: Wrong result")
                results.append(thread_id)
            except Exception as e:
                errors.append(f"Thread {thread_id}: {e}")
        
        threads = []
        for i in range(10):
            t = threading.Thread(target=read_worker, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Concurrent read errors: {errors}"
        assert len(results) == 10
    
    def test_concurrent_read_write(self, router: TrieRouter):
        """Test concurrent read and write operations."""
        errors = []
        write_count = [0]
        read_count = [0]
        
        def writer():
            try:
                for i in range(50):
                    router.add_exact_route(f"dynamic_{i}", f"orch_{i}")
                    write_count[0] += 1
            except Exception as e:
                errors.append(f"Writer: {e}")
        
        def reader():
            try:
                for _ in range(100):
                    router.match("dynamic_25")
                    read_count[0] += 1
            except Exception as e:
                errors.append(f"Reader: {e}")
        
        writer_thread = threading.Thread(target=writer)
        reader_threads = [threading.Thread(target=reader) for _ in range(5)]
        
        writer_thread.start()
        for t in reader_threads:
            t.start()
        
        writer_thread.join()
        for t in reader_threads:
            t.join()
        
        assert len(errors) == 0, f"Concurrent R/W errors: {errors}"
        assert write_count[0] == 50
        assert read_count[0] == 500


# =============================================================================
# EDGE CASES AND ERROR HANDLING
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_input(self, populated_router: TrieRouter):
        """Test empty input returns no match."""
        match = populated_router.match("")
        assert not match.is_matched
    
    def test_whitespace_only_input(self, populated_router: TrieRouter):
        """Test whitespace-only input returns no match."""
        match = populated_router.match("   ")
        assert not match.is_matched
    
    def test_none_input(self, populated_router: TrieRouter):
        """Test None-like input is handled."""
        match = populated_router.match(None)  # type: ignore
        assert not match.is_matched
    
    def test_unicode_input(self, router: TrieRouter):
        """Test Unicode input is handled."""
        router.add_exact_route("créer un plan", "french_orchestrator")
        
        match = router.match("créer un plan")
        assert match.is_matched
        assert match.orchestrator_id == "french_orchestrator"
    
    def test_special_characters(self, router: TrieRouter):
        """Test input with special characters."""
        router.add_exact_route("test (special)", "special_orchestrator")
        
        match = router.match("test (special)")
        assert match.is_matched
    
    def test_very_long_input(self, populated_router: TrieRouter):
        """Test very long input is handled."""
        long_input = "plan " + "word " * 1000
        match = populated_router.match(long_input)
        # Should not crash, may or may not match
        assert isinstance(match, RouteMatch)
    
    def test_clear_router(self, populated_router: TrieRouter):
        """Test clearing all routes."""
        populated_router.clear()
        
        stats = populated_router.get_stats()
        assert stats['total_routes'] == 0
        
        match = populated_router.match("plan")
        assert not match.is_matched


class TestStatistics:
    """Test router statistics and debugging."""
    
    def test_stats_tracking(self, populated_router: TrieRouter):
        """Test statistics are tracked correctly."""
        # Do some lookups
        populated_router.match("plan")
        populated_router.match("help")
        populated_router.match("nonexistent")
        
        stats = populated_router.get_stats()
        assert stats['total_lookups'] == 3
        assert stats['cache_hits'] >= 2  # At least 2 exact matches
    
    def test_export_routes(self, populated_router: TrieRouter):
        """Test route export for debugging."""
        export = populated_router.export_routes()
        
        assert 'exact' in export
        assert 'stats' in export
        assert len(export['exact']) > 0


# =============================================================================
# INTEGRATION WITH EXISTING ROUTER
# =============================================================================

class TestBackwardsCompatibility:
    """Test integration with existing pattern_router.py."""
    
    def test_match_result_compatibility(self, router: TrieRouter):
        """Test RouteMatch has compatible interface."""
        router.add_exact_route("test", "test_orchestrator", confidence=0.95)
        match = router.match("test")
        
        # Check interface matches OrchestratorMatch from pattern_router.py
        assert hasattr(match, 'orchestrator_id')
        assert hasattr(match, 'confidence')
        assert hasattr(match, 'match_type')
        assert hasattr(match, 'matched_pattern')
        assert hasattr(match, 'metadata')
        assert hasattr(match, 'is_matched')
        assert hasattr(match, 'is_high_confidence')
    
    def test_global_instance(self):
        """Test global instance getter/setter."""
        router1 = get_trie_router()
        router2 = get_trie_router()
        
        assert router1 is router2
        
        new_router = TrieRouter()
        set_trie_router(new_router)
        
        assert get_trie_router() is new_router


# =============================================================================
# TEST SUMMARY
# =============================================================================
#
# Total tests: ~40
# 
# Coverage:
# - Basic functionality: add routes, match types
# - Exact O(1) matching
# - Trie prefix matching
# - Keyword matching (single, multiple, require_all)
# - Regex pattern matching
# - Priority routing
# - Performance: <5ms SLA for 100 orchestrators
# - Thread safety: concurrent reads, concurrent R/W
# - Edge cases: empty, unicode, special chars, long input
# - Statistics and debugging
# - Backwards compatibility
# =============================================================================
