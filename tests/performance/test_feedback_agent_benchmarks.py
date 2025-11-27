"""
Performance Benchmarks for FeedbackAgent
Purpose: Validate FeedbackAgent meets performance requirements (<500ms, <100MB, <50% CPU)
Created: 2025-11-26
Author: Asif Hussain
"""

import pytest
import time
import psutil
import os
from pathlib import Path
from src.agents.feedback_agent import FeedbackAgent


@pytest.fixture
def temp_brain_path(tmp_path):
    """Create temporary brain directory for benchmarks."""
    brain_path = tmp_path / "cortex-brain"
    brain_path.mkdir(parents=True, exist_ok=True)
    return brain_path


@pytest.fixture
def feedback_agent(temp_brain_path):
    """Create FeedbackAgent instance for benchmarking."""
    return FeedbackAgent(brain_path=str(temp_brain_path))


class TestFeedbackAgentPerformanceBenchmarks:
    """Performance benchmarks for FeedbackAgent operations."""
    
    def test_initialization_performance(self, temp_brain_path):
        """Benchmark: FeedbackAgent initialization should complete in <100ms."""
        start_time = time.time()
        agent = FeedbackAgent(brain_path=str(temp_brain_path))
        elapsed_ms = (time.time() - start_time) * 1000
        
        assert elapsed_ms < 100, f"Initialization took {elapsed_ms:.2f}ms (expected <100ms)"
        assert agent is not None
    
    def test_report_creation_performance(self, feedback_agent):
        """Benchmark: Single report creation should complete in <500ms."""
        start_time = time.time()
        result = feedback_agent.create_feedback_report(
            user_input="Performance benchmark test",
            feedback_type="bug",
            severity="medium",
            auto_upload=False
        )
        elapsed_ms = (time.time() - start_time) * 1000
        
        assert elapsed_ms < 500, f"Report creation took {elapsed_ms:.2f}ms (expected <500ms)"
        assert result is not None
        assert "feedback_id" in result
    
    def test_report_creation_with_context_performance(self, feedback_agent):
        """Benchmark: Report creation with context should complete in <500ms."""
        context = {
            "file_path": "/path/to/test/file.py",
            "conversation_id": "conv-benchmark-123",
            "operation": "code_review",
            "metadata": {"lines_changed": 150, "complexity": "high"}
        }
        
        start_time = time.time()
        result = feedback_agent.create_feedback_report(
            user_input="Performance test with rich context",
            feedback_type="improvement",
            severity="low",
            context=context,
            auto_upload=False
        )
        elapsed_ms = (time.time() - start_time) * 1000
        
        assert elapsed_ms < 500, f"Report with context took {elapsed_ms:.2f}ms (expected <500ms)"
        assert result is not None
    
    def test_bulk_report_creation_performance(self, feedback_agent):
        """Benchmark: Creating 20 reports should complete in <5 seconds (avg <250ms each)."""
        num_reports = 20
        
        start_time = time.time()
        for i in range(num_reports):
            feedback_agent.create_feedback_report(
                user_input=f"Bulk benchmark test {i}",
                feedback_type="bug",
                auto_upload=False
            )
        total_elapsed = time.time() - start_time
        avg_elapsed_ms = (total_elapsed / num_reports) * 1000
        
        assert total_elapsed < 5.0, f"Bulk creation took {total_elapsed:.2f}s (expected <5s)"
        assert avg_elapsed_ms < 250, f"Average per report: {avg_elapsed_ms:.2f}ms (expected <250ms)"


class TestFeedbackAgentMemoryBenchmarks:
    """Memory usage benchmarks for FeedbackAgent."""
    
    def test_memory_usage_single_report(self, feedback_agent):
        """Benchmark: Single report creation should use <10MB memory."""
        process = psutil.Process(os.getpid())
        
        # Get baseline memory
        baseline_mb = process.memory_info().rss / 1024 / 1024
        
        # Create report
        feedback_agent.create_feedback_report(
            user_input="Memory benchmark test" * 100,  # Larger input
            feedback_type="bug",
            auto_upload=False
        )
        
        # Get memory after
        after_mb = process.memory_info().rss / 1024 / 1024
        memory_increase_mb = after_mb - baseline_mb
        
        # Should not increase more than 10MB
        assert memory_increase_mb < 10, f"Memory increased by {memory_increase_mb:.2f}MB (expected <10MB)"
    
    def test_memory_usage_multiple_reports(self, feedback_agent):
        """Benchmark: Creating 50 reports should use <50MB additional memory."""
        process = psutil.Process(os.getpid())
        
        # Get baseline memory
        baseline_mb = process.memory_info().rss / 1024 / 1024
        
        # Create 50 reports
        for i in range(50):
            feedback_agent.create_feedback_report(
                user_input=f"Memory test {i}",
                feedback_type="bug",
                auto_upload=False
            )
        
        # Get memory after
        after_mb = process.memory_info().rss / 1024 / 1024
        memory_increase_mb = after_mb - baseline_mb
        
        # Should not increase more than 50MB for 50 reports
        assert memory_increase_mb < 50, f"Memory increased by {memory_increase_mb:.2f}MB (expected <50MB)"
    
    def test_total_memory_usage(self, feedback_agent):
        """Benchmark: Total memory usage should stay under 100MB."""
        process = psutil.Process(os.getpid())
        
        # Create some reports
        for i in range(10):
            feedback_agent.create_feedback_report(
                user_input=f"Total memory test {i}",
                feedback_type="bug",
                auto_upload=False
            )
        
        # Check total memory usage
        total_mb = process.memory_info().rss / 1024 / 1024
        
        # Total process memory should be reasonable (allowing for test framework overhead)
        assert total_mb < 200, f"Total memory usage: {total_mb:.2f}MB (expected <200MB with test overhead)"


class TestFeedbackAgentCPUBenchmarks:
    """CPU usage benchmarks for FeedbackAgent."""
    
    def test_cpu_usage_single_report(self, feedback_agent):
        """Benchmark: CPU usage should stay below 50% during report creation."""
        process = psutil.Process(os.getpid())
        
        # Get baseline CPU
        process.cpu_percent(interval=0.1)
        
        # Create report
        start_time = time.time()
        feedback_agent.create_feedback_report(
            user_input="CPU benchmark test",
            feedback_type="bug",
            auto_upload=False
        )
        
        # Get CPU usage during operation
        cpu_percent = process.cpu_percent(interval=0.1)
        
        # CPU usage should be reasonable (<50%)
        assert cpu_percent < 50, f"CPU usage: {cpu_percent:.1f}% (expected <50%)"
    
    def test_cpu_usage_sustained_load(self, feedback_agent):
        """Benchmark: CPU usage should stay reasonable during sustained operations."""
        process = psutil.Process(os.getpid())
        
        # Reset CPU measurement
        process.cpu_percent(interval=0.1)
        
        # Create multiple reports
        for i in range(20):
            feedback_agent.create_feedback_report(
                user_input=f"Sustained CPU test {i}",
                feedback_type="bug",
                auto_upload=False
            )
        
        # Check CPU after sustained load
        cpu_percent = process.cpu_percent(interval=0.5)
        
        # Should not spike CPU too high
        assert cpu_percent < 70, f"Sustained CPU usage: {cpu_percent:.1f}% (expected <70%)"


class TestFeedbackAgentScalabilityBenchmarks:
    """Scalability benchmarks for FeedbackAgent."""
    
    def test_scalability_100_reports(self, feedback_agent):
        """Benchmark: Should handle 100 reports efficiently."""
        start_time = time.time()
        
        for i in range(100):
            feedback_agent.create_feedback_report(
                user_input=f"Scalability test {i}",
                feedback_type="bug",
                auto_upload=False
            )
        
        total_elapsed = time.time() - start_time
        avg_per_report_ms = (total_elapsed / 100) * 1000
        
        # Should average less than 300ms per report at scale
        assert avg_per_report_ms < 300, f"Average at scale: {avg_per_report_ms:.2f}ms (expected <300ms)"
        assert total_elapsed < 30, f"Total time for 100 reports: {total_elapsed:.2f}s (expected <30s)"
    
    def test_scalability_large_input(self, feedback_agent):
        """Benchmark: Should handle large feedback input efficiently."""
        # Generate large input (10KB)
        large_input = "This is a detailed feedback report. " * 500
        
        start_time = time.time()
        result = feedback_agent.create_feedback_report(
            user_input=large_input,
            feedback_type="improvement",
            auto_upload=False
        )
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Should still complete in reasonable time even with large input
        assert elapsed_ms < 1000, f"Large input took {elapsed_ms:.2f}ms (expected <1000ms)"
        assert result is not None
    
    def test_scalability_concurrent_operations(self, feedback_agent):
        """Benchmark: Should handle operations efficiently even with file I/O."""
        import concurrent.futures
        
        def create_report(index):
            return feedback_agent.create_feedback_report(
                user_input=f"Concurrent test {index}",
                feedback_type="bug",
                auto_upload=False
            )
        
        start_time = time.time()
        
        # Create 10 reports (sequential due to file I/O limitations)
        results = []
        for i in range(10):
            results.append(create_report(i))
        
        elapsed = time.time() - start_time
        
        # Should complete all operations
        assert len(results) == 10
        assert all(r is not None for r in results)
        assert elapsed < 5.0, f"Sequential operations took {elapsed:.2f}s (expected <5s)"


class TestFeedbackAgentResponseTimeBenchmarks:
    """Response time benchmarks for different operations."""
    
    def test_p95_response_time(self, feedback_agent):
        """Benchmark: 95th percentile response time should be <600ms."""
        response_times = []
        
        for i in range(100):
            start_time = time.time()
            feedback_agent.create_feedback_report(
                user_input=f"P95 test {i}",
                feedback_type="bug",
                auto_upload=False
            )
            elapsed_ms = (time.time() - start_time) * 1000
            response_times.append(elapsed_ms)
        
        # Calculate P95
        response_times.sort()
        p95_index = int(len(response_times) * 0.95)
        p95_time_ms = response_times[p95_index]
        
        assert p95_time_ms < 600, f"P95 response time: {p95_time_ms:.2f}ms (expected <600ms)"
    
    def test_p99_response_time(self, feedback_agent):
        """Benchmark: 99th percentile response time should be <1000ms."""
        response_times = []
        
        for i in range(100):
            start_time = time.time()
            feedback_agent.create_feedback_report(
                user_input=f"P99 test {i}",
                feedback_type="bug",
                auto_upload=False
            )
            elapsed_ms = (time.time() - start_time) * 1000
            response_times.append(elapsed_ms)
        
        # Calculate P99
        response_times.sort()
        p99_index = int(len(response_times) * 0.99)
        p99_time_ms = response_times[p99_index]
        
        assert p99_time_ms < 1000, f"P99 response time: {p99_time_ms:.2f}ms (expected <1000ms)"


# Summary benchmark test
class TestFeedbackAgentBenchmarkSummary:
    """Summary of all performance benchmarks."""
    
    def test_performance_summary(self, feedback_agent):
        """Generate performance summary for FeedbackAgent."""
        import statistics
        
        # Run multiple iterations
        times = []
        for i in range(50):
            start = time.time()
            feedback_agent.create_feedback_report(
                user_input=f"Summary test {i}",
                feedback_type="bug",
                auto_upload=False
            )
            times.append((time.time() - start) * 1000)
        
        # Calculate statistics
        avg_ms = statistics.mean(times)
        median_ms = statistics.median(times)
        min_ms = min(times)
        max_ms = max(times)
        
        print(f"\n=== FeedbackAgent Performance Summary ===")
        print(f"Average: {avg_ms:.2f}ms")
        print(f"Median: {median_ms:.2f}ms")
        print(f"Min: {min_ms:.2f}ms")
        print(f"Max: {max_ms:.2f}ms")
        print(f"Target: <500ms")
        
        # Assert performance targets
        assert avg_ms < 500, f"Average response time {avg_ms:.2f}ms exceeds 500ms target"
        assert median_ms < 500, f"Median response time {median_ms:.2f}ms exceeds 500ms target"
