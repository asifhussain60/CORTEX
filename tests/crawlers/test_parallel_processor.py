"""
Tests for Parallel Processor

Author: CORTEX Application Health Dashboard
"""

import pytest
import time
from pathlib import Path
from src.crawlers.parallel_processor import ParallelProcessor, ProcessingResult


class TestParallelProcessorInitialization:
    """Test parallel processor initialization"""
    
    def test_processor_creation(self):
        """Test processor can be created"""
        processor = ParallelProcessor()
        assert processor is not None
    
    def test_auto_detect_workers(self):
        """Test auto-detection of worker count"""
        processor = ParallelProcessor()
        assert processor.max_workers > 0
        assert processor.max_workers <= 100
    
    def test_custom_worker_count(self):
        """Test custom worker count"""
        processor = ParallelProcessor(max_workers=50)
        assert processor.max_workers == 50


class TestParallelProcessorBasicProcessing:
    """Test basic file processing"""
    
    def test_process_empty_list(self):
        """Test processing empty file list"""
        processor = ParallelProcessor(max_workers=4)
        
        def dummy_func(path):
            return {'path': path}
        
        result = processor.process_files([], dummy_func)
        assert result.total_files == 0
        assert result.processed_files == 0
        assert len(result.results) == 0
    
    def test_process_single_file(self):
        """Test processing single file"""
        processor = ParallelProcessor(max_workers=4)
        
        def process_func(path):
            return {'path': path, 'processed': True}
        
        result = processor.process_files(['file1.txt'], process_func)
        assert result.total_files == 1
        assert result.processed_files == 1
        assert len(result.results) == 1
        assert result.results[0]['path'] == 'file1.txt'
    
    def test_process_multiple_files(self):
        """Test processing multiple files"""
        processor = ParallelProcessor(max_workers=4)
        
        def process_func(path):
            return {'path': path}
        
        files = [f'file{i}.txt' for i in range(10)]
        result = processor.process_files(files, process_func)
        
        assert result.total_files == 10
        assert result.processed_files == 10
        assert len(result.results) == 10


class TestParallelProcessorErrorHandling:
    """Test error handling in parallel processing"""
    
    def test_handle_processing_error(self):
        """Test handling of processing errors"""
        processor = ParallelProcessor(max_workers=4)
        
        def failing_func(path):
            if 'error' in path:
                raise ValueError(f"Error processing {path}")
            return {'path': path}
        
        files = ['file1.txt', 'error.txt', 'file2.txt']
        result = processor.process_files(files, failing_func)
        
        assert result.total_files == 3
        assert result.processed_files == 2
        assert result.failed_files == 1
        assert len(result.errors) == 1
        assert 'error.txt' in result.errors[0]['file']
    
    def test_all_files_fail(self):
        """Test when all files fail processing"""
        processor = ParallelProcessor(max_workers=4)
        
        def always_fails(path):
            raise RuntimeError("Always fails")
        
        files = ['file1.txt', 'file2.txt']
        result = processor.process_files(files, always_fails)
        
        assert result.processed_files == 0
        assert result.failed_files == 2
        assert len(result.errors) == 2


class TestParallelProcessorProgressTracking:
    """Test progress tracking"""
    
    def test_progress_callback(self):
        """Test progress callback is called"""
        processor = ParallelProcessor(max_workers=4)
        
        progress_updates = []
        
        def track_progress(current, total):
            progress_updates.append((current, total))
        
        def process_func(path):
            time.sleep(0.01)  # Small delay
            return {'path': path}
        
        files = [f'file{i}.txt' for i in range(5)]
        result = processor.process_files(files, process_func, track_progress)
        
        assert len(progress_updates) == 5
        assert progress_updates[-1] == (5, 5)  # Final update
    
    def test_progress_without_callback(self):
        """Test processing works without progress callback"""
        processor = ParallelProcessor(max_workers=4)
        
        def process_func(path):
            return {'path': path}
        
        files = ['file1.txt', 'file2.txt']
        result = processor.process_files(files, process_func, None)
        
        assert result.processed_files == 2


class TestParallelProcessorPerformanceMetrics:
    """Test performance metrics calculation"""
    
    def test_elapsed_time_tracked(self):
        """Test elapsed time is tracked"""
        processor = ParallelProcessor(max_workers=4)
        
        def slow_func(path):
            time.sleep(0.01)
            return {'path': path}
        
        result = processor.process_files(['file1.txt'], slow_func)
        assert result.elapsed_time > 0
    
    def test_throughput_calculation(self):
        """Test throughput is calculated"""
        processor = ParallelProcessor(max_workers=4)
        
        def process_func(path):
            return {'path': path}
        
        files = [f'file{i}.txt' for i in range(20)]
        result = processor.process_files(files, process_func)
        
        assert result.throughput > 0
        assert result.processed_files / result.elapsed_time == pytest.approx(result.throughput, rel=0.01)


class TestParallelProcessorBatchProcessing:
    """Test batch processing functionality"""
    
    def test_batch_processing(self):
        """Test processing files in batches"""
        processor = ParallelProcessor(max_workers=4)
        
        def process_func(path):
            return {'path': path}
        
        files = [f'file{i}.txt' for i in range(50)]
        result = processor.process_in_batches(files, process_func, batch_size=10)
        
        assert result.total_files == 50
        assert result.processed_files == 50
        assert len(result.results) == 50
    
    def test_batch_progress_tracking(self):
        """Test progress tracking across batches"""
        processor = ParallelProcessor(max_workers=4)
        
        progress_updates = []
        
        def track_progress(current, total):
            progress_updates.append((current, total))
        
        def process_func(path):
            return {'path': path}
        
        files = [f'file{i}.txt' for i in range(25)]
        result = processor.process_in_batches(files, process_func, batch_size=10, progress_callback=track_progress)
        
        assert len(progress_updates) == 25
        assert progress_updates[-1][1] == 25  # Total should be 25
