"""
Tests for UniversalCollectorBase

Tests language-agnostic data collection foundation with:
- File discovery and filtering
- Parallel processing with worker pools
- File chunking for large codebases
- Progress tracking and cancellation
- Error isolation per file
- Caching and incremental analysis

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)

TDD Approach: RED → GREEN → REFACTOR
Phase: RED (Tests written first, expected to fail)
"""

import pytest
import tempfile
import time
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import Mock, patch


class TestUniversalCollectorBaseInitialization:
    """Test collector initialization and configuration"""
    
    def test_collector_requires_project_root(self):
        """Collector must be initialized with valid project root"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with pytest.raises(ValueError, match="project_root.*required"):
            UniversalCollectorBase(project_root=None)
    
    def test_collector_accepts_path_or_string(self):
        """Collector should accept both Path and string for project_root"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with string path
            collector1 = UniversalCollectorBase(project_root=tmpdir)
            assert collector1.project_root == Path(tmpdir)
            
            # Test with Path object
            collector2 = UniversalCollectorBase(project_root=Path(tmpdir))
            assert collector2.project_root == Path(tmpdir)
    
    def test_collector_validates_project_root_exists(self):
        """Collector should validate that project root exists"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with pytest.raises(FileNotFoundError):
            UniversalCollectorBase(project_root="/nonexistent/path/12345")
    
    def test_collector_has_default_configuration(self):
        """Collector should have sensible default configuration"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = UniversalCollectorBase(project_root=tmpdir)
            
            assert collector.max_workers > 0
            assert collector.chunk_size > 0
            assert collector.enable_caching is True
            assert collector.cache_dir is not None


class TestFileDiscovery:
    """Test file discovery and filtering"""
    
    def test_discover_all_files_in_directory(self):
        """Should discover all files recursively"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file structure
            Path(tmpdir, "file1.py").write_text("print('hello')")
            Path(tmpdir, "dir1").mkdir()
            Path(tmpdir, "dir1", "file2.cs").write_text("// test")
            Path(tmpdir, "dir1", "dir2").mkdir()
            Path(tmpdir, "dir1", "dir2", "file3.ts").write_text("console.log()")
            
            collector = UniversalCollectorBase(project_root=tmpdir)
            files = collector.discover_files()
            
            assert len(files) == 3
            assert any(f.name == "file1.py" for f in files)
            assert any(f.name == "file2.cs" for f in files)
            assert any(f.name == "file3.ts" for f in files)
    
    def test_filter_files_by_extension(self):
        """Should filter files by extension"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.py").write_text("# python")
            Path(tmpdir, "test.cs").write_text("// csharp")
            Path(tmpdir, "test.txt").write_text("text")
            
            collector = UniversalCollectorBase(project_root=tmpdir)
            files = collector.discover_files(extensions=[".py", ".cs"])
            
            assert len(files) == 2
            assert not any(f.suffix == ".txt" for f in files)
    
    def test_exclude_directories(self):
        """Should exclude specified directories"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "src", "main.py").write_text("# main")
            Path(tmpdir, "node_modules").mkdir()
            Path(tmpdir, "node_modules", "lib.js").write_text("// lib")
            Path(tmpdir, ".git").mkdir()
            Path(tmpdir, ".git", "config").write_text("git")
            
            collector = UniversalCollectorBase(project_root=tmpdir)
            files = collector.discover_files(exclude_dirs=["node_modules", ".git"])
            
            assert len(files) == 1
            assert files[0].name == "main.py"
    
    def test_default_exclusions(self):
        """Should exclude common directories by default"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files in excluded directories
            for dirname in ["node_modules", "__pycache__", ".git", "bin", "obj"]:
                Path(tmpdir, dirname).mkdir()
                Path(tmpdir, dirname, "file.txt").write_text("test")
            
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "src", "main.py").write_text("# main")
            
            collector = UniversalCollectorBase(project_root=tmpdir)
            files = collector.discover_files()
            
            # Should only find main.py
            assert len(files) == 1
            assert files[0].name == "main.py"


class TestFileChunking:
    """Test file chunking for parallel processing"""
    
    def test_chunk_files_into_batches(self):
        """Should split files into equal-sized chunks"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create 10 files
            for i in range(10):
                Path(tmpdir, f"file{i}.py").write_text(f"# {i}")
            
            collector = UniversalCollectorBase(project_root=tmpdir)
            files = collector.discover_files()
            chunks = collector.chunk_files(files, chunk_size=3)
            
            assert len(chunks) == 4  # 3 + 3 + 3 + 1
            assert len(chunks[0]) == 3
            assert len(chunks[1]) == 3
            assert len(chunks[2]) == 3
            assert len(chunks[3]) == 1
    
    def test_chunk_size_from_configuration(self):
        """Should use chunk_size from collector configuration"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(20):
                Path(tmpdir, f"file{i}.py").write_text(f"# {i}")
            
            collector = UniversalCollectorBase(project_root=tmpdir, chunk_size=5)
            files = collector.discover_files()
            chunks = collector.chunk_files(files)
            
            assert len(chunks) == 4  # 5 + 5 + 5 + 5
            assert all(len(chunk) == 5 for chunk in chunks)


class TestParallelProcessing:
    """Test parallel file processing"""
    
    def test_process_files_in_parallel(self):
        """Should process files concurrently using worker pool"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            for i in range(10):
                Path(tmpdir, f"file{i}.py").write_text(f"# File {i}\nprint('test')")
            
            collector = UniversalCollectorBase(project_root=tmpdir, max_workers=4)
            files = collector.discover_files()
            
            # Mock processing function
            def process_func(file_path):
                return {"path": str(file_path), "lines": 2}
            
            results = collector.process_parallel(files, process_func)
            
            assert len(results) == 10
            assert all(r["lines"] == 2 for r in results)
    
    def test_parallel_processing_respects_max_workers(self):
        """Should not exceed max_workers limit"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(20):
                Path(tmpdir, f"file{i}.py").write_text("# test")
            
            collector = UniversalCollectorBase(project_root=tmpdir, max_workers=2)
            files = collector.discover_files()
            
            # Track concurrent executions
            active_workers = []
            max_concurrent = 0
            
            def track_worker(file_path):
                active_workers.append(1)
                nonlocal max_concurrent
                max_concurrent = max(max_concurrent, len(active_workers))
                time.sleep(0.01)  # Simulate work
                active_workers.pop()
                return {"path": str(file_path)}
            
            collector.process_parallel(files, track_worker)
            
            assert max_concurrent <= 2
    
    def test_error_isolation_in_parallel_processing(self):
        """Errors in one file should not stop processing of other files"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(5):
                Path(tmpdir, f"file{i}.py").write_text(f"# {i}")
            
            collector = UniversalCollectorBase(project_root=tmpdir)
            files = collector.discover_files()
            
            def process_with_error(file_path):
                if "file2" in str(file_path):
                    raise ValueError("Simulated error")
                return {"path": str(file_path), "success": True}
            
            results = collector.process_parallel(files, process_with_error, ignore_errors=True)
            
            # Should have 4 successful results (file2 failed)
            successful = [r for r in results if r.get("success")]
            assert len(successful) == 4


class TestProgressTracking:
    """Test progress tracking and reporting"""
    
    def test_progress_callback_invoked(self):
        """Should invoke progress callback during processing"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(10):
                Path(tmpdir, f"file{i}.py").write_text("# test")
            
            progress_updates = []
            
            def progress_callback(current, total, message):
                progress_updates.append((current, total, message))
            
            collector = UniversalCollectorBase(project_root=tmpdir)
            files = collector.discover_files()
            
            collector.process_parallel(
                files,
                lambda f: {"path": str(f)},
                progress_callback=progress_callback
            )
            
            assert len(progress_updates) > 0
            assert progress_updates[-1][0] == 10  # Final progress
            assert progress_updates[-1][1] == 10  # Total files
    
    def test_progress_percentage_calculation(self):
        """Should calculate progress percentage correctly"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(100):
                Path(tmpdir, f"file{i}.py").write_text("# test")
            
            percentages = []
            
            def track_progress(current, total, message):
                percentages.append((current / total) * 100)
            
            collector = UniversalCollectorBase(project_root=tmpdir)
            files = collector.discover_files()
            
            collector.process_parallel(
                files,
                lambda f: {"path": str(f)},
                progress_callback=track_progress
            )
            
            # Should reach 100%
            assert percentages[-1] == 100.0


class TestCaching:
    """Test caching and incremental analysis"""
    
    def test_cache_directory_created(self):
        """Should create cache directory if not exists"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = UniversalCollectorBase(project_root=tmpdir, enable_caching=True)
            
            assert collector.cache_dir.exists()
            assert collector.cache_dir.is_dir()
    
    def test_file_hash_calculation(self):
        """Should calculate consistent hash for file content"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.py")
            test_file.write_text("print('hello')")
            
            collector = UniversalCollectorBase(project_root=tmpdir)
            
            hash1 = collector.calculate_file_hash(test_file)
            hash2 = collector.calculate_file_hash(test_file)
            
            assert hash1 == hash2
            assert len(hash1) > 0
    
    def test_cache_stores_and_retrieves_results(self):
        """Should cache and retrieve analysis results"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.py")
            test_file.write_text("print('test')")
            
            collector = UniversalCollectorBase(project_root=tmpdir, enable_caching=True)
            
            # Store result
            test_result = {"lines": 1, "complexity": 1}
            collector.cache_result(test_file, test_result)
            
            # Retrieve result
            cached = collector.get_cached_result(test_file)
            
            assert cached == test_result
    
    def test_cache_invalidation_on_file_change(self):
        """Should invalidate cache when file content changes"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.py")
            test_file.write_text("print('version 1')")
            
            collector = UniversalCollectorBase(project_root=tmpdir, enable_caching=True)
            
            # Cache initial result
            collector.cache_result(test_file, {"version": 1})
            
            # Modify file
            test_file.write_text("print('version 2')")
            
            # Should return None (cache invalidated)
            cached = collector.get_cached_result(test_file)
            assert cached is None
    
    def test_skip_cached_files_in_incremental_mode(self):
        """Should skip analysis of cached files in incremental mode"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files
            file1 = Path(tmpdir, "file1.py")
            file2 = Path(tmpdir, "file2.py")
            file1.write_text("# test 1")
            file2.write_text("# test 2")
            
            collector = UniversalCollectorBase(
                project_root=tmpdir,
                enable_caching=True,
                incremental=True
            )
            
            # Cache result for file1
            collector.cache_result(file1, {"cached": True})
            
            files = [file1, file2]
            processed_count = 0
            
            def count_processing(file_path):
                nonlocal processed_count
                processed_count += 1
                return {"processed": True}
            
            results = collector.process_parallel(files, count_processing)
            
            # Should only process file2 (file1 was cached)
            assert processed_count == 1


class TestPerformanceOptimizations:
    """Test performance optimizations"""
    
    def test_streaming_analysis_for_large_files(self):
        """Should use streaming for files larger than threshold"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create large file (> 1MB)
            large_file = Path(tmpdir, "large.py")
            large_file.write_text("# " + "x" * (2 * 1024 * 1024))  # 2MB
            
            collector = UniversalCollectorBase(project_root=tmpdir)
            
            # Should detect as large file
            assert collector.is_large_file(large_file, threshold_mb=1)
    
    def test_memory_efficient_file_reading(self):
        """Should read files in chunks to conserve memory"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.py")
            test_file.write_text("line1\nline2\nline3\nline4\nline5")
            
            collector = UniversalCollectorBase(project_root=tmpdir)
            
            lines_processed = 0
            for chunk in collector.read_file_chunks(test_file, chunk_size=2):
                lines_processed += len(chunk.splitlines())
            
            assert lines_processed == 5


class TestErrorHandling:
    """Test error handling and recovery"""
    
    def test_graceful_handling_of_missing_files(self):
        """Should handle files that disappear during processing"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = UniversalCollectorBase(project_root=tmpdir)
            
            nonexistent = Path(tmpdir, "nonexistent.py")
            
            def process_func(file_path):
                return {"path": str(file_path)}
            
            # Should not crash
            results = collector.process_parallel([nonexistent], process_func, ignore_errors=True)
            assert len(results) == 0  # No results for missing file
    
    def test_timeout_for_slow_processing(self):
        """Should timeout files that take too long to process"""
        from src.dashboard.collectors.universal_collector_base import UniversalCollectorBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.py").write_text("# test")
            
            collector = UniversalCollectorBase(project_root=tmpdir, file_timeout=0.1)
            files = collector.discover_files()
            
            def slow_process(file_path):
                time.sleep(1)  # Too slow
                return {"path": str(file_path)}
            
            results = collector.process_parallel(files, slow_process, ignore_errors=True)
            
            # Should timeout and return empty or error result
            assert len(results) == 0 or results[0].get("error") is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
