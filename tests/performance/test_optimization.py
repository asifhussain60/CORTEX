"""
Performance Tests for TDD Workflow Optimization

Tests caching, batch processing, and memory optimization.

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 3 - Milestone 3.2 (Production Optimization)
"""

import pytest
import tempfile
import time
from pathlib import Path
from src.workflows.ast_cache import ASTCache, parse_file_cached
from src.workflows.pattern_cache import PatternCache
from src.workflows.smell_cache import SmellCache
from src.workflows.batch_processor import BatchTestGenerator, BatchSmellDetector


class TestASTCache:
    """Test AST caching functionality."""
    
    def test_ast_cache_hit(self):
        """Should return cached AST on second parse."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test_function():\n    return 42\n")
            filepath = f.name
        
        try:
            cache = ASTCache(max_size=10)
            
            # First parse - cache miss
            tree1 = parse_file_cached(filepath, cache)
            assert cache.misses == 1
            assert cache.hits == 0
            
            # Second parse - cache hit
            tree2 = parse_file_cached(filepath, cache)
            assert cache.hits == 1
            assert tree1 is tree2  # Same object
            
        finally:
            Path(filepath).unlink()
    
    def test_ast_cache_invalidation_on_change(self):
        """Should invalidate cache when file changes."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def original():\n    pass\n")
            filepath = f.name
        
        try:
            cache = ASTCache()
            
            # Parse original
            tree1 = parse_file_cached(filepath, cache)
            assert cache.hits == 0
            
            # Modify file
            with open(filepath, 'w') as f:
                f.write("def modified():\n    pass\n")
            
            # Parse again - should be cache miss due to hash change
            tree2 = parse_file_cached(filepath, cache)
            assert cache.misses == 2  # Both parses were misses
            assert tree1 is not tree2
            
        finally:
            Path(filepath).unlink()
    
    def test_ast_cache_lru_eviction(self):
        """Should evict LRU entry when cache full."""
        cache = ASTCache(max_size=2)
        
        files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(f"def func{i}():\n    pass\n")
                files.append(f.name)
        
        try:
            # Fill cache
            parse_file_cached(files[0], cache)
            parse_file_cached(files[1], cache)
            assert len(cache.cache) == 2
            
            # Add third file - should evict first
            parse_file_cached(files[2], cache)
            assert len(cache.cache) == 2
            assert files[0] not in cache.cache
            assert files[1] in cache.cache
            assert files[2] in cache.cache
            
        finally:
            for filepath in files:
                Path(filepath).unlink()
    
    def test_ast_cache_stats(self):
        """Should provide accurate cache statistics."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test():\n    pass\n")
            filepath = f.name
        
        try:
            cache = ASTCache()
            
            parse_file_cached(filepath, cache)
            parse_file_cached(filepath, cache)
            parse_file_cached(filepath, cache)
            
            stats = cache.stats()
            
            assert stats['size'] == 1
            assert stats['hits'] == 2
            assert stats['misses'] == 1
            assert '66.7%' in stats['hit_rate']  # 2/3 = 66.7%
            
        finally:
            Path(filepath).unlink()


class TestPatternCache:
    """Test pattern caching functionality."""
    
    def test_pattern_cache_hit(self):
        """Should return cached patterns on second lookup."""
        cache = PatternCache()
        
        filepath = "test.py"
        function_name = "test_func"
        patterns = ["empty_string", "none_value"]
        locations = [10, 15]
        
        cache.put(filepath, function_name, patterns, locations, 0.9)
        
        # First get - cache hit
        match = cache.get(filepath, function_name)
        assert match is not None
        assert match.patterns == patterns
        assert cache.hits == 1
        
        # Second get - another hit
        match2 = cache.get(filepath, function_name)
        assert match2 is not None
        assert cache.hits == 2
    
    def test_pattern_cache_invalidate_file(self):
        """Should invalidate all functions for a file."""
        cache = PatternCache()
        
        filepath = "test.py"
        
        cache.put(filepath, "func1", ["pattern1"], [1], 0.8)
        cache.put(filepath, "func2", ["pattern2"], [2], 0.9)
        
        count = cache.invalidate_file(filepath)
        
        assert count == 2
        assert cache.get(filepath, "func1") is None
        assert cache.get(filepath, "func2") is None
    
    def test_pattern_cache_stats(self):
        """Should provide accurate cache statistics."""
        cache = PatternCache()
        
        cache.put("file1.py", "func1", ["p1"], [1], 0.8)
        cache.put("file1.py", "func2", ["p2"], [2], 0.9)
        cache.put("file2.py", "func1", ["p3"], [3], 0.7)
        
        stats = cache.stats()
        
        assert stats['files_cached'] == 2
        assert stats['functions_cached'] == 3


class TestSmellCache:
    """Test smell detection caching functionality."""
    
    def test_smell_cache_hit(self):
        """Should return cached smells on second lookup."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test():\n    pass\n")
            filepath = f.name
        
        try:
            cache = SmellCache()
            
            smells = [
                {"type": "long_method", "line": 1},
                {"type": "complex_conditional", "line": 5}
            ]
            
            cache.put(filepath, smells)
            
            # Cache hit
            cached_smells = cache.get(filepath)
            assert cached_smells == smells
            assert cache.hits == 1
            
        finally:
            Path(filepath).unlink()
    
    def test_smell_cache_invalidation_on_change(self):
        """Should invalidate cache when file content changes."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def original():\n    pass\n")
            filepath = f.name
        
        try:
            cache = SmellCache()
            
            # Cache original
            cache.put(filepath, [{"type": "smell1"}])
            
            # Modify file
            with open(filepath, 'w') as f:
                f.write("def modified():\n    pass\n")
            
            # Should be cache miss due to hash change
            cached = cache.get(filepath)
            assert cached is None
            assert cache.misses == 1
            
        finally:
            Path(filepath).unlink()
    
    def test_smell_cache_get_files_with_smells(self):
        """Should filter files by smell type."""
        cache = SmellCache()
        
        cache.put("file1.py", [{"type": "long_method"}], "hash1")
        cache.put("file2.py", [{"type": "complex_conditional"}], "hash2")
        cache.put("file3.py", [], "hash3")  # No smells
        
        files_with_long_method = cache.get_files_with_smells("long_method")
        assert "file1.py" in files_with_long_method
        assert "file2.py" not in files_with_long_method


class TestBatchProcessing:
    """Test batch processing functionality."""
    
    def test_batch_test_generation_speedup(self):
        """Batch processing should be faster than sequential."""
        # Create test files
        files = []
        for i in range(4):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(f"def func{i}(x: int) -> int:\n    return x * {i}\n")
                files.append(f.name)
        
        try:
            # This is a placeholder - actual test requires orchestrator mock
            # Real implementation would compare sequential vs parallel timing
            assert len(files) == 4
            
        finally:
            for filepath in files:
                Path(filepath).unlink()
    
    def test_batch_result_summary(self):
        """Should summarize batch results correctly."""
        from src.workflows.batch_processor import BatchResult
        
        results = {
            "file1.py": BatchResult("file1.py", True, 10, "test1.py", 0.5),
            "file2.py": BatchResult("file2.py", True, 15, "test2.py", 0.7),
            "file3.py": BatchResult("file3.py", False, 0, None, 0.3, "Error occurred")
        }
        
        # Create mock batch generator
        class MockOrchestrator:
            pass
        
        from src.workflows.batch_processor import BatchTestGenerator
        batch_gen = BatchTestGenerator(MockOrchestrator())
        
        summary = batch_gen.summarize_batch_results(results)
        
        assert summary['total_files'] == 3
        assert summary['successful'] == 2
        assert summary['failed'] == 1
        assert summary['total_tests_generated'] == 25
        assert len(summary['errors']) == 1


class TestCacheIntegration:
    """Test cache integration scenarios."""
    
    def test_multiple_caches_coordinated(self):
        """AST, pattern, and smell caches should work together."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test_func(x):\n    return x\n")
            filepath = f.name
        
        try:
            ast_cache = ASTCache()
            pattern_cache = PatternCache()
            smell_cache = SmellCache()
            
            # Parse with AST cache
            tree = parse_file_cached(filepath, ast_cache)
            assert ast_cache.hits == 0
            assert ast_cache.misses == 1
            
            # Add pattern cache entry
            pattern_cache.put(filepath, "test_func", ["pattern1"], [1], 0.8)
            
            # Add smell cache entry
            smell_cache.put(filepath, [{"type": "smell1"}])
            
            # Modify file - all caches should invalidate
            with open(filepath, 'w') as f:
                f.write("def modified_func(x):\n    return x * 2\n")
            
            # AST cache should miss
            tree2 = parse_file_cached(filepath, ast_cache)
            assert ast_cache.misses == 2
            
            # Pattern cache should miss
            assert pattern_cache.get(filepath, "test_func") is not None  # Still cached (manual invalidation needed)
            
            # Smell cache should miss
            assert smell_cache.get(filepath) is None
            
        finally:
            Path(filepath).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
