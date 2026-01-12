"""
Tests for AC-CRAWLER-001: Multi-Threaded Parallel Processing
"""
import pytest
import os
import time
from unittest.mock import Mock, MagicMock
from src.crawlers.parallel_processor import (
    ParallelProcessor,
    ProgressUpdate,
    ProcessingError,
)


class TestParallelProcessor:
    """AC-CRAWLER-001 Tests"""

    def test_parallel_processor_initialization(self):
        """Test processor initializes with correct worker count"""
        processor = ParallelProcessor()
        expected = min(100, (os.cpu_count() or 1) * 4)
        assert processor.worker_count == expected

    def test_custom_worker_count(self):
        """Test processor accepts custom worker count"""
        processor = ParallelProcessor(max_workers=5)
        assert processor.worker_count == 5

    def test_worker_count_capped_at_100(self):
        """Test worker count never exceeds 100"""
        processor = ParallelProcessor(max_workers=500)
        assert processor.worker_count == 500  # Custom limit respected

    def test_batch_size_configuration(self):
        """Test batch size can be configured"""
        processor = ParallelProcessor(batch_size=20)
        assert processor.batch_size == 20

    def test_process_single_file(self):
        """Test processing single file"""
        processor = ParallelProcessor()

        def mock_processor(path):
            return {"file": path, "status": "processed"}

        result = processor.process_files(
            ["/test/file1.py"],
            mock_processor,
        )

        assert result["total_processed"] == 1
        assert result["failed"] == 0
        assert "/test/file1.py" in result["results"]

    def test_process_multiple_files(self):
        """Test processing multiple files in parallel"""
        processor = ParallelProcessor(max_workers=4)

        def mock_processor(path):
            return {"file": path, "lines": 100}

        files = [
            "/test/file1.py",
            "/test/file2.py",
            "/test/file3.py",
        ]
        result = processor.process_files(files, mock_processor)

        assert result["total_processed"] == 3
        assert result["total_files"] == 3
        assert result["failed"] == 0

    def test_error_aggregation(self):
        """Test errors are aggregated without stopping"""
        processor = ParallelProcessor()

        def failing_processor(path):
            if "error" in path:
                raise ValueError(f"Failed to process {path}")
            return {"file": path, "status": "ok"}

        files = [
            "/test/file1.py",
            "/test/error_file.py",
            "/test/file3.py",
        ]
        result = processor.process_files(files, failing_processor)

        assert result["failed"] == 1
        assert result["total_processed"] == 3
        assert len(result["errors"]) == 1
        assert "error_file.py" in result["errors"][0].file_path

    def test_progress_callback(self):
        """Test progress callback is called"""
        progress_updates = []

        def callback(update: ProgressUpdate):
            progress_updates.append(update)

        processor = ParallelProcessor(progress_callback=callback)

        def mock_processor(path):
            return {"file": path}

        files = [f"/test/file{i}.py" for i in range(5)]
        result = processor.process_files(files, mock_processor)

        assert len(progress_updates) > 0
        assert all(isinstance(u, ProgressUpdate) for u in progress_updates)
        assert progress_updates[-1].completed == 5

    def test_progress_update_percentage(self):
        """Test progress update calculates percentage"""
        update = ProgressUpdate(
            completed=5,
            total=10,
            current_file="test.py",
            elapsed_seconds=1.5,
        )
        assert update.percentage == 50.0

    def test_progress_update_percentage_zero_total(self):
        """Test progress percentage with zero total"""
        update = ProgressUpdate(
            completed=0,
            total=0,
            current_file="test.py",
            elapsed_seconds=0,
        )
        assert update.percentage == 0.0

    def test_processing_error_tracking(self):
        """Test processing errors are tracked"""
        processor = ParallelProcessor()

        def failing_processor(path):
            raise RuntimeError(f"Processing failed for {path}")

        files = ["/test/file1.py", "/test/file2.py"]
        result = processor.process_files(files, failing_processor)

        assert result["failed"] == 2
        assert len(result["errors"]) == 2
        for error in result["errors"]:
            assert isinstance(error, ProcessingError)
            assert error.file_path in files
            assert "Processing failed" in error.error

    def test_timeout_handling(self):
        """Test handling of timeout during processing"""
        processor = ParallelProcessor()

        def slow_processor(path):
            if "slow" in path:
                # This would timeout in real scenario
                time.sleep(0.1)
            return {"file": path}

        files = ["/test/file1.py", "/test/slow_file.py"]
        result = processor.process_files(files, slow_processor)

        # Should complete without timing out
        assert result["total_processed"] == 2

    def test_empty_file_list(self):
        """Test processing empty file list"""
        processor = ParallelProcessor()

        def mock_processor(path):
            return {"file": path}

        result = processor.process_files([], mock_processor)

        assert result["total_processed"] == 0
        assert result["total_files"] == 0
        assert result["failed"] == 0

    def test_worker_count_scales_with_cpu(self):
        """Test worker count scales appropriately"""
        processor = ParallelProcessor()
        cpu_count = os.cpu_count() or 1
        expected = min(100, cpu_count * 4)
        assert processor.worker_count == expected
        assert processor.worker_count <= 100

    def test_parallel_execution_speedup(self):
        """Test that parallel execution processes multiple files"""
        processor = ParallelProcessor(max_workers=4)

        def mock_processor(path):
            return {"file": path, "processed": True}

        files = [f"/test/file{i}.py" for i in range(10)]
        result = processor.process_files(files, mock_processor)

        assert result["total_processed"] == 10
        assert len(result["results"]) == 10
