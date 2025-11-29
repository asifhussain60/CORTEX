"""
Performance benchmarks for Search operations.

Tests search query performance, full-text search, and filtering.
Target: <200ms for semantic search operations
"""

import asyncio
import pytest

from src.application.commands.conversation_commands import CaptureConversationCommand
from src.application.queries.conversation_queries import SearchContextQuery
from src.application.commands.conversation_handlers import CaptureConversationHandler
from src.application.queries.conversation_handlers import SearchContextHandler


class TestSearchPerformance:
    """Benchmark tests for search operations."""
    
    def test_simple_text_search(self, benchmark, perf_unit_of_work, sample_conversations):
        """Benchmark: Simple text keyword search."""
        # Setup: Add 30 conversations
        write_handler = CaptureConversationHandler(perf_unit_of_work)
        for i in range(30):
            conv_data = sample_conversations[i].copy()
            conv_data["conversation_id"] = f"bench_search_simple_{i:03d}"
            command = CaptureConversationCommand(**conv_data)
            asyncio.run(write_handler.handle(command))
        
        search_handler = SearchContextHandler(perf_unit_of_work)
        query = SearchContextQuery(
            search_text="Performance",
            min_relevance=0.0,
            max_results=10
        )
        
        def execute_search():
            return asyncio.run(search_handler.handle(query))
        
        result = benchmark(execute_search)
        
        # Verify search succeeded
        assert result.is_success
        
        # Performance assertion: <200ms for search
        stats = benchmark.stats
        assert stats.stats.mean < 0.200, f"Mean search latency {stats.stats.mean*1000:.2f}ms exceeds 200ms target"
    
    def test_search_with_relevance_filter(self, benchmark, perf_unit_of_work, sample_conversations):
        """Benchmark: Search with relevance score filtering."""
        # Setup: Add 30 conversations
        write_handler = CaptureConversationHandler(perf_unit_of_work)
        for i in range(30):
            conv_data = sample_conversations[i].copy()
            conv_data["conversation_id"] = f"bench_search_relevance_{i:03d}"
            command = CaptureConversationCommand(**conv_data)
            asyncio.run(write_handler.handle(command))
        
        search_handler = SearchContextHandler(perf_unit_of_work)
        query = SearchContextQuery(
            search_text="test",
            min_relevance=0.5,
            max_results=10
        )
        
        def execute_search():
            return asyncio.run(search_handler.handle(query))
        
        result = benchmark(execute_search)
        
        # Verify search succeeded
        assert result.is_success
        
        # Performance assertion: <200ms for filtered search
        stats = benchmark.stats
        assert stats.stats.mean < 0.200, f"Mean filtered search latency {stats.stats.mean*1000:.2f}ms exceeds 200ms target"
    
    def test_search_large_dataset(self, benchmark, perf_unit_of_work, sample_conversations):
        """Benchmark: Search performance with larger dataset (100 conversations)."""
        # Setup: Add all 100 sample conversations
        write_handler = CaptureConversationHandler(perf_unit_of_work)
        for i in range(100):
            conv_data = sample_conversations[i].copy()
            conv_data["conversation_id"] = f"bench_search_large_{i:03d}"
            command = CaptureConversationCommand(**conv_data)
            asyncio.run(write_handler.handle(command))
        
        search_handler = SearchContextHandler(perf_unit_of_work)
        query = SearchContextQuery(
            search_text="benchmarking",
            min_relevance=0.0,
            max_results=20
        )
        
        def execute_search():
            return asyncio.run(search_handler.handle(query))
        
        result = benchmark(execute_search)
        
        # Verify search succeeded
        assert result.is_success
        
        # Performance assertion: <300ms for large dataset search
        stats = benchmark.stats
        assert stats.stats.mean < 0.300, f"Mean large search latency {stats.stats.mean*1000:.2f}ms exceeds 300ms target"
    
    def test_search_no_results(self, benchmark, perf_unit_of_work, sample_conversations):
        """Benchmark: Search with no matching results."""
        # Setup: Add 30 conversations
        write_handler = CaptureConversationHandler(perf_unit_of_work)
        for i in range(30):
            conv_data = sample_conversations[i].copy()
            conv_data["conversation_id"] = f"bench_search_empty_{i:03d}"
            command = CaptureConversationCommand(**conv_data)
            asyncio.run(write_handler.handle(command))
        
        search_handler = SearchContextHandler(perf_unit_of_work)
        query = SearchContextQuery(
            search_text="nonexistent_unique_term_xyz",
            min_relevance=0.0,
            max_results=10
        )
        
        def execute_search():
            return asyncio.run(search_handler.handle(query))
        
        result = benchmark(execute_search)
        
        # Verify search succeeded with no results
        assert result.is_success
        assert len(result.value) == 0
        
        # Performance assertion: <100ms for empty result search
        stats = benchmark.stats
        assert stats.stats.mean < 0.100, f"Mean empty search latency {stats.stats.mean*1000:.2f}ms exceeds 100ms target"
    
    def test_concurrent_search_operations(self, benchmark, perf_unit_of_work, sample_conversations):
        """Benchmark: Concurrent search operations."""
        # Setup: Add 50 conversations
        write_handler = CaptureConversationHandler(perf_unit_of_work)
        for i in range(50):
            conv_data = sample_conversations[i].copy()
            conv_data["conversation_id"] = f"bench_search_concurrent_{i:03d}"
            command = CaptureConversationCommand(**conv_data)
            asyncio.run(write_handler.handle(command))
        
        search_handler = SearchContextHandler(perf_unit_of_work)
        
        async def concurrent_searches():
            """Execute 5 different searches concurrently."""
            queries = [
                SearchContextQuery(search_text="Performance", min_relevance=0.0, max_results=10),
                SearchContextQuery(search_text="Test", min_relevance=0.0, max_results=10),
                SearchContextQuery(search_text="Benchmark", min_relevance=0.0, max_results=10),
                SearchContextQuery(search_text="Conversation", min_relevance=0.0, max_results=10),
                SearchContextQuery(search_text="number", min_relevance=0.0, max_results=10),
            ]
            
            tasks = [search_handler.handle(q) for q in queries]
            results = await asyncio.gather(*tasks)
            return results
        
        def run_concurrent():
            return asyncio.run(concurrent_searches())
        
        results = benchmark(run_concurrent)
        
        # Verify all searches succeeded
        assert all(r.is_success for r in results)
        assert len(results) == 5
        
        # Performance assertion: <500ms for 5 concurrent searches
        stats = benchmark.stats
        assert stats.stats.mean < 0.500, f"Mean concurrent search latency {stats.stats.mean*1000:.2f}ms exceeds 500ms target"
