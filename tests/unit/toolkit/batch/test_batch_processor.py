"""Tests for canonical BatchProcessor — Consolidation of 4 duplicate implementations.

TDD Phase: RED → Tests written before implementation
Authority: phase-toolkit-consolidation.yaml Sub-phase S3
CORE-008: TDD mandatory
CORE-035: Single canonical implementation (merges 4 duplicates)

Merges:
    1. tests/unit/phase4/test_brt027_performance_optimization.py (BatchProcessor)
    2. cortex/core/knowledge/bulk_ingestion.py (BulkIngestionPipeline batching)
    3. cortex/lens/lens_tiered_mcp_api.py (LensStreamTier3 batching)
    4. CortexXdistPlugin (test runner batching)

AC_START: AC-TOOLKIT-BATCH-PROCESSOR-TEST-001
"""

from __future__ import annotations

import time
from typing import Any, List

import pytest

from cortex.toolkit.batch.batch_processor import (
    BatchProcessor,
    BatchTrigger,
    BatchResult,
)


class TestBatchProcessorInitialization:
    """Test BatchProcessor initialization."""
    
    def test_default_initialization(self):
        """BatchProcessor must initialize with default size and timeout."""
        processor = BatchProcessor()
        
        assert processor.batch_size == 100
        assert processor.timeout_ms == 5000
        assert processor.get_batch_size() == 0
    
    def test_custom_batch_size(self):
        """BatchProcessor must accept custom batch size."""
        processor = BatchProcessor(batch_size=50)
        
        assert processor.batch_size == 50
    
    def test_custom_timeout(self):
        """BatchProcessor must accept custom timeout."""
        processor = BatchProcessor(timeout_ms=2000)
        
        assert processor.timeout_ms == 2000
    
    def test_thread_safety(self):
        """BatchProcessor must be thread-safe."""
        processor = BatchProcessor()
        
        # Should have Lock for concurrent access
        assert hasattr(processor, "_lock")


class TestBatchProcessorSizeTrigger:
    """Test batch size trigger (fills batch before processing)."""
    
    def test_add_single_item(self):
        """Adding single item must not trigger flush."""
        processor = BatchProcessor(batch_size=3)
        
        trigger = processor.add("item1")
        
        assert trigger == BatchTrigger.NONE
        assert processor.get_batch_size() == 1
    
    def test_add_until_full(self):
        """Adding items until full must trigger size-based flush."""
        processor = BatchProcessor(batch_size=3)
        
        processor.add("item1")
        processor.add("item2")
        trigger = processor.add("item3")
        
        assert trigger == BatchTrigger.SIZE
        assert processor.get_batch_size() == 3
    
    def test_flush_clears_batch(self):
        """Flushing must return items and clear internal batch."""
        processor = BatchProcessor(batch_size=5)
        
        processor.add("item1")
        processor.add("item2")
        
        batch = processor.flush()
        
        assert len(batch) == 2
        assert "item1" in batch
        assert "item2" in batch
        assert processor.get_batch_size() == 0


class TestBatchProcessorTimeoutTrigger:
    """Test timeout trigger (processes partial batches after delay)."""
    
    def test_timeout_trigger(self):
        """Timeout must trigger flush even if batch not full."""
        processor = BatchProcessor(batch_size=100, timeout_ms=100)
        
        processor.add("item1")
        time.sleep(0.15)  # Exceed 100ms timeout
        
        trigger = processor.add("item2")
        
        assert trigger == BatchTrigger.TIMEOUT
    
    def test_timeout_reset_after_flush(self):
        """Timeout timer must reset after flush."""
        processor = BatchProcessor(batch_size=10, timeout_ms=100)
        
        processor.add("item1")
        processor.flush()  # Reset timer
        
        processor.add("item2")
        time.sleep(0.05)  # Less than timeout
        trigger = processor.add("item3")
        
        assert trigger == BatchTrigger.NONE


class TestBatchProcessorEdgeCases:
    """Test edge cases and error handling."""
    
    def test_flush_empty_batch(self):
        """Flushing empty batch must return empty list."""
        processor = BatchProcessor()
        
        batch = processor.flush()
        
        assert batch == []
        assert processor.get_batch_size() == 0
    
    def test_multiple_flushes(self):
        """Multiple flushes must work correctly."""
        processor = BatchProcessor(batch_size=2)
        
        processor.add("A")
        batch1 = processor.flush()
        
        processor.add("B")
        batch2 = processor.flush()
        
        assert batch1 == ["A"]
        assert batch2 == ["B"]
    
    def test_none_items_allowed(self):
        """None items must be accepted (for optional values)."""
        processor = BatchProcessor(batch_size=3)
        
        processor.add(None)
        processor.add("item")
        processor.add(None)
        
        batch = processor.flush()
        
        assert len(batch) == 3
        assert None in batch


class TestBatchProcessorProcessing:
    """Test batch processing with callback functions."""
    
    def test_process_batch_with_callback(self):
        """Processor must support processing batches via callback."""
        processor = BatchProcessor(batch_size=3)
        
        results = []
        
        def callback(items: List[Any]) -> None:
            results.extend([f"processed_{item}" for item in items])
        
        processor.add("A")
        processor.add("B")
        processor.add("C")  # Trigger size flush
        
        batch = processor.flush()
        callback(batch)
        
        assert "processed_A" in results
        assert "processed_B" in results
        assert "processed_C" in results


class TestBatchResult:
    """Test BatchResult dataclass."""
    
    def test_batch_result_creation(self):
        """BatchResult must track batch metadata."""
        result = BatchResult(
            batch_id="BATCH-001",
            items=["A", "B", "C"],
            trigger=BatchTrigger.SIZE,
            processing_time_ms=123.45
        )
        
        assert result.batch_id == "BATCH-001"
        assert len(result.items) == 3
        assert result.trigger == BatchTrigger.SIZE
        assert result.processing_time_ms == 123.45


class TestBatchProcessorIntegration:
    """Integration tests simulating real use cases."""
    
    def test_high_throughput_scenario(self):
        """Simulate high-throughput ingestion (BulkIngestionPipeline use case)."""
        processor = BatchProcessor(batch_size=1000, timeout_ms=5000)
        
        # Add 2500 items (2 full batches + 500 partial)
        for i in range(2500):
            trigger = processor.add(f"item_{i}")
            
            if trigger != BatchTrigger.NONE:
                batch = processor.flush()
                assert len(batch) == 1000
        
        # Flush remaining
        final_batch = processor.flush()
        assert len(final_batch) == 500
    
    def test_streaming_scenario(self):
        """Simulate streaming analysis (LensStreamTier3 use case)."""
        processor = BatchProcessor(batch_size=10, timeout_ms=1000)
        
        file_paths = [f"file_{i}.py" for i in range(25)]
        
        batches_processed = 0
        for path in file_paths:
            trigger = processor.add(path)
            
            if trigger != BatchTrigger.NONE:
                batch = processor.flush()
                batches_processed += 1
                assert len(batch) == 10
        
        # Flush remaining
        final_batch = processor.flush()
        assert len(final_batch) == 5
        assert batches_processed == 2  # 2 full batches of 10
    
    def test_test_runner_scenario(self):
        """Simulate pytest batch execution (CortexXdistPlugin use case)."""
        processor = BatchProcessor(batch_size=500, timeout_ms=60000)
        
        # Simulate test collection (15,739 tests)
        test_count = 15739
        
        for i in range(test_count):
            trigger = processor.add(f"test_{i}")
            
            if trigger == BatchTrigger.SIZE:
                batch = processor.flush()
                assert len(batch) == 500
        
        # Flush remaining
        final_batch = processor.flush()
        assert len(final_batch) == test_count % 500


# AC_COMPLETE: AC-TOOLKIT-BATCH-PROCESSOR-TEST-001 ✅ Tests written (RED phase)
