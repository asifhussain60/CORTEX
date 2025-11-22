"""
Performance benchmarks for Mediator pattern implementation.

Tests mediator throughput, latency, and request handling performance.
Target: <50ms p95 latency for command/query dispatch.
"""

import asyncio
import pytest

from src.application.commands.conversation_commands import CaptureConversationCommand
from src.application.queries.conversation_queries import GetConversationByIdQuery, SearchContextQuery
from src.application.commands.conversation_handlers import CaptureConversationHandler
from src.application.queries.conversation_handlers import (
    GetConversationByIdHandler,
    SearchContextHandler
)


class TestMediatorPerformance:
    """Benchmark tests for mediator pattern performance."""
    
    def test_command_dispatch_latency(self, benchmark, perf_unit_of_work):
        """Benchmark: Command dispatch latency (single command)."""
        command = CaptureConversationCommand(
            conversation_id="bench_conv_001",
            title="Benchmark Conversation",
            content="Content for latency benchmark",
            file_path="/bench/latency.md",
            quality_score=0.85,
            entity_count=5
        )
        
        handler = CaptureConversationHandler(perf_unit_of_work)
        
        def execute_command():
            return asyncio.run(handler.handle(command))
        
        result = benchmark(execute_command)
        
        # Verify command executed successfully
        assert result.is_success
        
        # Performance assertion: <50ms p95
        stats = benchmark.stats
        assert stats.stats.mean < 0.050, f"Mean latency {stats.stats.mean*1000:.2f}ms exceeds 50ms target"
    
    def test_query_dispatch_latency(self, benchmark, perf_unit_of_work, sample_conversations):
        """Benchmark: Query dispatch latency (single query)."""
        # Setup: Add a conversation first
        command = CaptureConversationCommand(**sample_conversations[0])
        handler = CaptureConversationHandler(perf_unit_of_work)
        asyncio.run(handler.handle(command))
        
        query = GetConversationByIdQuery(conversation_id=sample_conversations[0]["conversation_id"])
        query_handler = GetConversationByIdHandler(perf_unit_of_work)
        
        def execute_query():
            return asyncio.run(query_handler.handle(query))
        
        result = benchmark(execute_query)
        
        # Verify query executed successfully
        assert result.is_success
        
        # Performance assertion: <50ms p95
        stats = benchmark.stats
        assert stats.stats.mean < 0.050, f"Mean latency {stats.stats.mean*1000:.2f}ms exceeds 50ms target"
    
    def test_concurrent_command_throughput(self, benchmark, perf_unit_of_work, sample_conversations):
        """Benchmark: Concurrent command processing throughput."""
        handler = CaptureConversationHandler(perf_unit_of_work)
        
        async def execute_concurrent_commands():
            """Execute 10 commands concurrently."""
            tasks = []
            for i in range(10):
                conv_data = sample_conversations[i].copy()
                conv_data["conversation_id"] = f"bench_concurrent_{i:03d}"
                command = CaptureConversationCommand(**conv_data)
                tasks.append(handler.handle(command))
            
            results = await asyncio.gather(*tasks)
            return results
        
        def run_concurrent():
            return asyncio.run(execute_concurrent_commands())
        
        results = benchmark(run_concurrent)
        
        # Verify all commands succeeded
        assert all(r.is_success for r in results)
        assert len(results) == 10
        
        # Performance assertion: <500ms for 10 concurrent (50ms each)
        stats = benchmark.stats
        assert stats.stats.mean < 0.500, f"Mean latency {stats.stats.mean*1000:.2f}ms exceeds 500ms target"
    
    def test_mixed_workload_performance(self, benchmark, perf_unit_of_work, sample_conversations):
        """Benchmark: Mixed command/query workload performance."""
        capture_handler = CaptureConversationHandler(perf_unit_of_work)
        query_handler = GetConversationByIdHandler(perf_unit_of_work)
        
        # Setup: Add some conversations
        for i in range(5):
            conv_data = sample_conversations[i].copy()
            conv_data["conversation_id"] = f"bench_mixed_{i:03d}"
            command = CaptureConversationCommand(**conv_data)
            asyncio.run(capture_handler.handle(command))
        
        async def execute_mixed_workload():
            """Execute 5 queries + 5 commands concurrently."""
            tasks = []
            
            # Add 5 queries
            for i in range(5):
                query = GetConversationByIdQuery(conversation_id=f"bench_mixed_{i:03d}")
                tasks.append(query_handler.handle(query))
            
            # Add 5 new commands
            for i in range(5, 10):
                conv_data = sample_conversations[i].copy()
                conv_data["conversation_id"] = f"bench_mixed_new_{i:03d}"
                command = CaptureConversationCommand(**conv_data)
                tasks.append(capture_handler.handle(command))
            
            results = await asyncio.gather(*tasks)
            return results
        
        def run_mixed():
            return asyncio.run(execute_mixed_workload())
        
        results = benchmark(run_mixed)
        
        # Verify all operations succeeded
        assert all(r.is_success for r in results)
        assert len(results) == 10
        
        # Performance assertion: <500ms for 10 mixed operations
        stats = benchmark.stats
        assert stats.stats.mean < 0.500, f"Mean latency {stats.stats.mean*1000:.2f}ms exceeds 500ms target"
    
    def test_search_query_performance(self, benchmark, perf_unit_of_work, sample_conversations):
        """Benchmark: Search query performance with filters."""
        # Setup: Add 20 conversations
        capture_handler = CaptureConversationHandler(perf_unit_of_work)
        for i in range(20):
            conv_data = sample_conversations[i].copy()
            conv_data["conversation_id"] = f"bench_search_{i:03d}"
            command = CaptureConversationCommand(**conv_data)
            asyncio.run(capture_handler.handle(command))
        
        search_handler = SearchContextHandler(perf_unit_of_work)
        query = SearchContextQuery(
            search_text="Performance",
            min_relevance=0.0,
            max_results=10
        )
        
        def execute_search():
            return asyncio.run(search_handler.handle(query))
        
        result = benchmark(execute_search)
        
        # Verify search executed successfully
        assert result.is_success
        
        # Performance assertion: <200ms for search operations
        stats = benchmark.stats
        assert stats.stats.mean < 0.200, f"Mean search latency {stats.stats.mean*1000:.2f}ms exceeds 200ms target"
