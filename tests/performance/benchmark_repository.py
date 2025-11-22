"""
Performance benchmarks for Repository operations.

Tests repository read/write performance and data access patterns.
Targets:
- Read operations: <10ms average
- Write operations: <20ms average
- Batch operations: Linear scaling
"""

import asyncio
import pytest

from src.application.commands.conversation_commands import (
    CaptureConversationCommand,
    DeleteConversationCommand,
    LearnPatternCommand
)
from src.application.queries.conversation_queries import (
    GetConversationByIdQuery,
    GetRecentConversationsQuery,
    GetPatternByIdQuery
)
from src.application.commands.conversation_handlers import (
    CaptureConversationHandler,
    DeleteConversationHandler,
    LearnPatternHandler
)
from src.application.queries.conversation_handlers import (
    GetConversationByIdHandler,
    GetRecentConversationsHandler,
    GetPatternByIdHandler
)


class TestRepositoryPerformance:
    """Benchmark tests for repository operations."""
    
    def test_single_conversation_write(self, benchmark, perf_unit_of_work, sample_conversations):
        """Benchmark: Single conversation write operation."""
        handler = CaptureConversationHandler(perf_unit_of_work)
        conv_data = sample_conversations[0].copy()
        conv_data["conversation_id"] = "bench_write_single"
        command = CaptureConversationCommand(**conv_data)
        
        def write_conversation():
            return asyncio.run(handler.handle(command))
        
        result = benchmark(write_conversation)
        
        # Verify write succeeded
        assert result.is_success
        
        # Performance assertion: <20ms for single write
        stats = benchmark.stats
        assert stats.stats.mean < 0.020, f"Mean write latency {stats.stats.mean*1000:.2f}ms exceeds 20ms target"
    
    def test_single_conversation_read(self, benchmark, perf_unit_of_work, sample_conversations):
        """Benchmark: Single conversation read operation."""
        # Setup: Add conversation first
        handler = CaptureConversationHandler(perf_unit_of_work)
        conv_data = sample_conversations[0].copy()
        conv_data["conversation_id"] = "bench_read_single"
        command = CaptureConversationCommand(**conv_data)
        asyncio.run(handler.handle(command))
        
        query_handler = GetConversationByIdHandler(perf_unit_of_work)
        query = GetConversationByIdQuery(conversation_id="bench_read_single")
        
        def read_conversation():
            return asyncio.run(query_handler.handle(query))
        
        result = benchmark(read_conversation)
        
        # Verify read succeeded
        assert result.is_success
        assert result.value is not None
        
        # Performance assertion: <10ms for single read
        stats = benchmark.stats
        assert stats.stats.mean < 0.010, f"Mean read latency {stats.stats.mean*1000:.2f}ms exceeds 10ms target"
    
    def test_batch_conversation_write(self, benchmark, perf_unit_of_work, sample_conversations):
        """Benchmark: Batch write operations (10 conversations)."""
        handler = CaptureConversationHandler(perf_unit_of_work)
        
        async def batch_write():
            """Write 10 conversations sequentially."""
            results = []
            for i in range(10):
                conv_data = sample_conversations[i].copy()
                conv_data["conversation_id"] = f"bench_batch_write_{i:03d}"
                command = CaptureConversationCommand(**conv_data)
                result = await handler.handle(command)
                results.append(result)
            return results
        
        def run_batch_write():
            return asyncio.run(batch_write())
        
        results = benchmark(run_batch_write)
        
        # Verify all writes succeeded
        assert all(r.is_success for r in results)
        assert len(results) == 10
        
        # Performance assertion: <200ms for 10 writes (20ms each)
        stats = benchmark.stats
        assert stats.stats.mean < 0.200, f"Mean batch write latency {stats.stats.mean*1000:.2f}ms exceeds 200ms target"
    
    def test_batch_conversation_read(self, benchmark, perf_unit_of_work, sample_conversations):
        """Benchmark: Batch read operations (10 conversations)."""
        # Setup: Add 10 conversations
        write_handler = CaptureConversationHandler(perf_unit_of_work)
        for i in range(10):
            conv_data = sample_conversations[i].copy()
            conv_data["conversation_id"] = f"bench_batch_read_{i:03d}"
            command = CaptureConversationCommand(**conv_data)
            asyncio.run(write_handler.handle(command))
        
        read_handler = GetConversationByIdHandler(perf_unit_of_work)
        
        async def batch_read():
            """Read 10 conversations sequentially."""
            results = []
            for i in range(10):
                query = GetConversationByIdQuery(conversation_id=f"bench_batch_read_{i:03d}")
                result = await read_handler.handle(query)
                results.append(result)
            return results
        
        def run_batch_read():
            return asyncio.run(batch_read())
        
        results = benchmark(run_batch_read)
        
        # Verify all reads succeeded
        assert all(r.is_success and r.value is not None for r in results)
        assert len(results) == 10
        
        # Performance assertion: <100ms for 10 reads (10ms each)
        stats = benchmark.stats
        assert stats.stats.mean < 0.100, f"Mean batch read latency {stats.stats.mean*1000:.2f}ms exceeds 100ms target"
    
    def test_recent_conversations_query(self, benchmark, perf_unit_of_work, sample_conversations):
        """Benchmark: Recent conversations query with limit."""
        # Setup: Add 50 conversations
        write_handler = CaptureConversationHandler(perf_unit_of_work)
        for i in range(50):
            conv_data = sample_conversations[i].copy()
            conv_data["conversation_id"] = f"bench_recent_{i:03d}"
            command = CaptureConversationCommand(**conv_data)
            asyncio.run(write_handler.handle(command))
        
        query_handler = GetRecentConversationsHandler(perf_unit_of_work)
        query = GetRecentConversationsQuery(max_results=20)
        
        def query_recent():
            return asyncio.run(query_handler.handle(query))
        
        result = benchmark(query_recent)
        
        # Verify query succeeded
        assert result.is_success
        assert len(result.value) <= 20
        
        # Performance assertion: <50ms for recent query
        stats = benchmark.stats
        assert stats.stats.mean < 0.050, f"Mean recent query latency {stats.stats.mean*1000:.2f}ms exceeds 50ms target"
    
    def test_pattern_write_performance(self, benchmark, perf_unit_of_work, sample_patterns):
        """Benchmark: Pattern write operations."""
        handler = LearnPatternHandler(perf_unit_of_work)
        pattern_data = sample_patterns[0].copy()
        pattern_data["pattern_id"] = "bench_pattern_write"
        command = LearnPatternCommand(**pattern_data)
        
        def write_pattern():
            return asyncio.run(handler.handle(command))
        
        result = benchmark(write_pattern)
        
        # Verify write succeeded
        assert result.is_success
        
        # Performance assertion: <20ms for pattern write
        stats = benchmark.stats
        assert stats.stats.mean < 0.020, f"Mean pattern write latency {stats.stats.mean*1000:.2f}ms exceeds 20ms target"
    
    def test_pattern_read_performance(self, benchmark, perf_unit_of_work, sample_patterns):
        """Benchmark: Pattern read operations."""
        # Setup: Add pattern first
        write_handler = LearnPatternHandler(perf_unit_of_work)
        pattern_data = sample_patterns[0].copy()
        pattern_data["pattern_id"] = "bench_pattern_read"
        command = LearnPatternCommand(**pattern_data)
        asyncio.run(write_handler.handle(command))
        
        query_handler = GetPatternByIdHandler(perf_unit_of_work)
        query = GetPatternByIdQuery(pattern_id="bench_pattern_read")
        
        def read_pattern():
            return asyncio.run(query_handler.handle(query))
        
        result = benchmark(read_pattern)
        
        # Verify read succeeded
        assert result.is_success
        assert result.value is not None
        
        # Performance assertion: <10ms for pattern read
        stats = benchmark.stats
        assert stats.stats.mean < 0.010, f"Mean pattern read latency {stats.stats.mean*1000:.2f}ms exceeds 10ms target"
    
    def test_conversation_delete_performance(self, benchmark, perf_unit_of_work, sample_conversations):
        """Benchmark: Conversation delete operations."""
        # Setup: Add conversations to delete
        write_handler = CaptureConversationHandler(perf_unit_of_work)
        conv_data = sample_conversations[0].copy()
        
        # Pre-populate some conversations for deletion
        for i in range(10):
            conv_data_copy = conv_data.copy()
            conv_data_copy["conversation_id"] = f"bench_delete_{i:03d}"
            command = CaptureConversationCommand(**conv_data_copy)
            asyncio.run(write_handler.handle(command))
        
        delete_handler = DeleteConversationHandler(perf_unit_of_work)
        
        counter = [0]  # Mutable counter for benchmark iterations
        
        def delete_conversation():
            """Delete conversation (creates new one each time for fair benchmark)."""
            # Add a fresh conversation to delete
            idx = counter[0]
            conv_new = conv_data.copy()
            conv_new["conversation_id"] = f"bench_delete_temp_{idx:06d}"
            add_cmd = CaptureConversationCommand(**conv_new)
            asyncio.run(write_handler.handle(add_cmd))
            
            # Delete it
            command = DeleteConversationCommand(conversation_id=conv_new["conversation_id"])
            result = asyncio.run(delete_handler.handle(command))
            counter[0] += 1
            return result
        
        result = benchmark(delete_conversation)
        
        # Verify delete succeeded
        assert result.is_success
        
        # Performance assertion: <30ms for delete (includes re-add)
        stats = benchmark.stats
        assert stats.stats.mean < 0.030, f"Mean delete latency {stats.stats.mean*1000:.2f}ms exceeds 30ms target"
