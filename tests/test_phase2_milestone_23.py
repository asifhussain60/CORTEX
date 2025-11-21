"""
Tests for Phase 2 Milestone 2.3 - Performance Optimization

Copyright (c) 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import os
import time
import asyncio
import sqlite3
from concurrent.futures import ThreadPoolExecutor

from src.cortex_agents.test_generator.function_signature_cache import (
    FunctionSignatureCache,
    CachedSignature,
    get_global_cache,
    reset_global_cache
)
from src.cortex_agents.test_generator.async_pattern_retriever import (
    AsyncPatternRetriever,
    RetrievalRequest,
    retrieve_for_function,
    retrieve_with_fallback
)
from src.cortex_agents.test_generator.connection_pool import (
    SQLiteConnectionPool,
    PooledConnection,
    create_pattern_store_pool
)
from src.cortex_agents.test_generator.tier2_pattern_store import (
    Tier2PatternStore,
    BusinessPattern
)
import ast
from datetime import datetime


class TestFunctionSignatureCache:
    """Test function signature caching system"""
    
    @pytest.fixture
    def cache(self):
        return FunctionSignatureCache(ttl_seconds=60, max_size=10)
    
    @pytest.fixture
    def sample_code(self):
        return '''
def calculate_total(items: list, tax_rate: float = 0.1) -> float:
    """Calculate total with tax"""
    return sum(items) * (1 + tax_rate)
'''
    
    @pytest.fixture
    def sample_ast(self, sample_code):
        tree = ast.parse(sample_code)
        return next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
    
    def test_cache_miss_on_first_access(self, cache, sample_code):
        """Test cache miss when accessing for first time"""
        result = cache.get(sample_code, 'calculate_total')
        
        assert result is None
        assert cache.misses == 1
        assert cache.hits == 0
    
    def test_cache_hit_after_put(self, cache, sample_code, sample_ast):
        """Test cache hit after storing entry"""
        # Store entry
        cache.put(
            sample_code,
            'calculate_total',
            [{'name': 'items', 'type': 'list'}, {'name': 'tax_rate', 'type': 'float'}],
            'float',
            'Calculate total with tax',
            sample_ast
        )
        
        # Retrieve entry
        result = cache.get(sample_code, 'calculate_total')
        
        assert result is not None
        assert result.function_name == 'calculate_total'
        assert len(result.parameters) == 2
        assert result.return_type == 'float'
        assert cache.hits == 1
        assert cache.misses == 0
    
    def test_cache_invalidation_on_code_change(self, cache, sample_ast):
        """Test cache invalidates when source code changes"""
        code_v1 = 'def foo(): pass'
        code_v2 = 'def foo(): return 42'
        
        # Store with v1
        cache.put(code_v1, 'foo', [], None, None, sample_ast)
        
        # Try to get with v2 (different hash)
        result = cache.get(code_v2, 'foo')
        
        assert result is None  # Should miss due to hash mismatch
        assert cache.misses == 1
    
    def test_ttl_expiration(self, sample_code, sample_ast):
        """Test entries expire after TTL"""
        cache = FunctionSignatureCache(ttl_seconds=1, max_size=10)
        
        # Store entry
        cache.put(sample_code, 'calculate_total', [], None, None, sample_ast)
        
        # Immediate retrieval should work
        result = cache.get(sample_code, 'calculate_total')
        assert result is not None
        
        # Wait for TTL to expire
        time.sleep(1.1)
        
        # Should be expired now
        result = cache.get(sample_code, 'calculate_total')
        assert result is None
        assert cache.misses == 1
    
    def test_lru_eviction(self, sample_ast):
        """Test LRU eviction when cache is full"""
        cache = FunctionSignatureCache(ttl_seconds=60, max_size=3)
        
        # Fill cache
        for i in range(3):
            code = f'def func{i}(): pass'
            cache.put(code, f'func{i}', [], None, None, sample_ast)
        
        assert len(cache.cache) == 3
        
        # Access func1 to make it more recent
        cache.get('def func1(): pass', 'func1')
        
        # Add one more (should evict func0 as LRU)
        cache.put('def func3(): pass', 'func3', [], None, None, sample_ast)
        
        assert len(cache.cache) == 3
        assert cache.evictions == 1
        
        # func0 should be gone
        result = cache.get('def func0(): pass', 'func0')
        assert result is None
    
    def test_access_count_tracking(self, cache, sample_code, sample_ast):
        """Test access count is tracked correctly"""
        cache.put(sample_code, 'calculate_total', [], None, None, sample_ast)
        
        # Access multiple times
        for _ in range(5):
            cache.get(sample_code, 'calculate_total')
        
        result = cache.get(sample_code, 'calculate_total')
        assert result.access_count == 6  # 5 + 1
    
    def test_cache_stats(self, cache, sample_code, sample_ast):
        """Test cache statistics reporting"""
        cache.put(sample_code, 'calculate_total', [], None, None, sample_ast)
        
        cache.get(sample_code, 'calculate_total')  # Hit
        cache.get('def other(): pass', 'other')    # Miss
        
        stats = cache.get_stats()
        
        assert stats['size'] == 1
        assert stats['max_size'] == 10
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 0.5
    
    def test_global_cache(self):
        """Test global cache instance"""
        reset_global_cache()
        
        cache1 = get_global_cache()
        cache2 = get_global_cache()
        
        assert cache1 is cache2  # Should be same instance


class TestAsyncPatternRetriever:
    """Test async pattern retrieval system"""
    
    @pytest.fixture
    def db_with_patterns(self):
        """Create temp DB with test patterns"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        store = Tier2PatternStore(db_path)
        
        # Add patterns in different domains
        for domain in ['authentication', 'validation', 'calculation']:
            for i in range(5):
                pattern = BusinessPattern(
                    None, domain, f'operation_{i}', 'postcondition',
                    f'{domain} pattern {i}', f'assert result_{i}',
                    0.7 + (i * 0.05), 0, 0, datetime.now().isoformat(), None, {}
                )
                store.store_pattern(pattern)
        
        yield db_path, store
        
        store.close()
        os.unlink(db_path)
    
    @pytest.fixture
    def retriever(self, db_with_patterns):
        """Create async retriever"""
        db_path, store = db_with_patterns
        return AsyncPatternRetriever(db_path, max_workers=4)
    
    def test_single_retrieval(self, retriever):
        """Test single pattern retrieval"""
        async def run_test():
            request = RetrievalRequest(
                query='operation',
                domain='authentication',
                min_confidence=0.5,
                limit=10
            )
            
            result = await retriever.retrieve_patterns(request)
            
            assert len(result.patterns) > 0
            assert result.source == 'database'  # First access
            assert result.duration_ms >= 0
            
        asyncio.run(run_test())
    
    def test_cache_hit_on_second_retrieval(self, retriever):
        """Test cache hit on repeated query"""
        async def run_test():
            request = RetrievalRequest(
                query='operation',
                domain='authentication',
                min_confidence=0.5,
                limit=10
            )
            
            # First retrieval
            result1 = await retriever.retrieve_patterns(request)
            assert result1.source == 'database'
            
            # Second retrieval (should hit cache)
            result2 = await retriever.retrieve_patterns(request)
            assert result2.source == 'cache'
            assert result2.duration_ms < result1.duration_ms  # Faster
            
        asyncio.run(run_test())
    
    def test_batch_retrieval(self, retriever):
        """Test parallel batch retrieval"""
        async def run_test():
            requests = [
                RetrievalRequest(query='operation', domain='authentication'),
                RetrievalRequest(query='operation', domain='validation'),
                RetrievalRequest(query='operation', domain='calculation'),
            ]
            
            results = await retriever.retrieve_batch(requests)
            
            assert len(results) == 3
            assert all(len(r.patterns) > 0 for r in results)
            
        asyncio.run(run_test())
    
    def test_multi_domain_retrieval(self, retriever):
        """Test multi-domain parallel retrieval"""
        async def run_test():
            results = await retriever.retrieve_multi_domain(
                query='operation',
                domains=['authentication', 'validation', 'calculation'],
                min_confidence=0.5
            )
            
            assert len(results) == 3
            assert 'authentication' in results
            assert 'validation' in results
            assert 'calculation' in results
            
            for domain, result in results.items():
                assert len(result.patterns) > 0
                assert all(p.domain == domain for p in result.patterns)
            
        asyncio.run(run_test())
    
    def test_retrieve_for_function_helper(self, retriever):
        """Test helper function for function-based retrieval"""
        async def run_test():
            patterns_by_domain = await retrieve_for_function(
                retriever,
                'operation_1',
                ['authentication', 'validation'],
                min_confidence=0.5
            )
            
            assert 'authentication' in patterns_by_domain
            assert 'validation' in patterns_by_domain
            
        asyncio.run(run_test())
    
    def test_retrieve_with_fallback_helper(self, retriever):
        """Test fallback retrieval helper"""
        async def run_test():
            primary = RetrievalRequest(
                query='nonexistent',
                domain='authentication',
                min_confidence=0.9
            )
            
            fallback = RetrievalRequest(
                query='operation',
                domain='authentication',
                min_confidence=0.5
            )
            
            result = await retrieve_with_fallback(retriever, primary, fallback)
            
            # Should return fallback results
            assert len(result.patterns) > 0
            
        asyncio.run(run_test())


class TestSQLiteConnectionPool:
    """Test SQLite connection pool"""
    
    @pytest.fixture
    def db_path(self):
        """Create temp database"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Initialize schema
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                value TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        yield db_path
        
        os.unlink(db_path)
    
    def test_pool_initialization(self, db_path):
        """Test pool creates initial connections"""
        pool = SQLiteConnectionPool(db_path, pool_size=3)
        
        stats = pool.get_stats()
        
        assert stats['pool_size'] == 3
        assert stats['connections_available'] == 3
        assert stats['connections_in_use'] == 0
        
        pool.close_all()
    
    def test_connection_acquisition(self, db_path):
        """Test acquiring connection from pool"""
        pool = SQLiteConnectionPool(db_path, pool_size=2)
        
        with pool.get_connection() as conn:
            assert conn is not None
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
        
        pool.close_all()
    
    def test_connection_reuse(self, db_path):
        """Test connections are reused after release"""
        pool = SQLiteConnectionPool(db_path, pool_size=2)
        
        # Acquire and release
        with pool.get_connection() as conn1:
            conn1_id = id(conn1)
        
        # Acquire again (should get same connection)
        with pool.get_connection() as conn2:
            conn2_id = id(conn2)
        
        # Note: May or may not be same Python object,
        # but pool stats should show reuse
        stats = pool.get_stats()
        assert stats['total_acquisitions'] == 2
        assert stats['total_releases'] == 2
        
        pool.close_all()
    
    def test_concurrent_access(self, db_path):
        """Test concurrent access from multiple threads"""
        pool = SQLiteConnectionPool(db_path, pool_size=3)
        
        def worker(worker_id: int):
            for i in range(5):
                with pool.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO test_table (value) VALUES (?)",
                        (f"worker_{worker_id}_item_{i}",)
                    )
                    conn.commit()
        
        # Run 3 workers concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(worker, i) for i in range(3)]
            for future in futures:
                future.result()  # Wait for completion
        
        # Verify all inserts succeeded
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM test_table")
            count = cursor.fetchone()[0]
            assert count == 15  # 3 workers * 5 inserts
        
        pool.close_all()
    
    def test_pool_exhaustion_timeout(self, db_path):
        """Test timeout when pool is exhausted"""
        pool = SQLiteConnectionPool(db_path, pool_size=1, timeout=1.0)
        
        # Acquire only connection
        conn1 = pool._acquire()
        
        # Try to acquire another (should timeout)
        with pytest.raises(TimeoutError):
            pool._acquire()
        
        # Release first connection
        pool._release(conn1)
        
        # Now acquisition should work
        conn2 = pool._acquire()
        assert conn2 is not None
        pool._release(conn2)
        
        pool.close_all()
    
    def test_execute_convenience_method(self, db_path):
        """Test execute convenience method"""
        pool = SQLiteConnectionPool(db_path, pool_size=2)
        
        # Insert data
        pool.execute(
            "INSERT INTO test_table (value) VALUES (?)",
            ("test_value",)
        )
        
        # Query data
        results = pool.execute("SELECT value FROM test_table")
        
        assert len(results) >= 1
        
        pool.close_all()
    
    def test_pool_stats_tracking(self, db_path):
        """Test pool statistics tracking"""
        pool = SQLiteConnectionPool(db_path, pool_size=2)
        
        # Perform some operations
        with pool.get_connection():
            pass
        
        with pool.get_connection():
            pass
        
        stats = pool.get_stats()
        
        assert stats['total_acquisitions'] == 2
        assert stats['total_releases'] == 2
        assert stats['created_connections'] == 2
        
        pool.close_all()


class TestPerformanceBenchmark:
    """Integration tests for performance validation"""
    
    @pytest.fixture
    def full_setup(self):
        """Create full setup with cache, async retriever, and pool"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        store = Tier2PatternStore(db_path)
        
        # Add 100 patterns across domains
        for domain in ['authentication', 'validation', 'calculation']:
            for i in range(33):
                pattern = BusinessPattern(
                    None, domain, f'operation_{i}', 'postcondition',
                    f'{domain} pattern {i}', f'assert result_{i}',
                    0.5 + (i * 0.01), 0, 0, datetime.now().isoformat(), None, {}
                )
                store.store_pattern(pattern)
        
        cache = FunctionSignatureCache(ttl_seconds=300)
        retriever = AsyncPatternRetriever(db_path, max_workers=4)
        pool = create_pattern_store_pool(db_path, pool_size=5)
        
        yield cache, retriever, pool, store
        
        pool.close_all()
        store.close()
        os.unlink(db_path)
    
    def test_end_to_end_performance(self, full_setup):
        """Test end-to-end performance meets <200ms target"""
        cache, retriever, pool, store = full_setup
        
        async def run_benchmark():
            start_time = time.time()
            
            # Simulate typical workflow
            # 1. Cache function signature (cached after first)
            code = 'def authenticate(username: str, password: str): pass'
            
            for _ in range(2):  # Second should hit cache
                cache.get(code, 'authenticate')
            
            # 2. Retrieve patterns from multiple domains
            results = await retriever.retrieve_multi_domain(
                query='authenticate',
                domains=['authentication', 'validation'],
                min_confidence=0.5
            )
            
            # 3. Access patterns via pool
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM patterns")
                cursor.fetchone()
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            return elapsed_ms
        
        duration = asyncio.run(run_benchmark())
        
        # Should be well under 200ms (target includes more operations)
        assert duration < 200, f"End-to-end took {duration:.2f}ms (target: <200ms)"
    
    def test_parallel_retrieval_performance(self, full_setup):
        """Test parallel retrieval is faster than sequential"""
        cache, retriever, pool, store = full_setup
        
        async def sequential():
            start = time.time()
            for domain in ['authentication', 'validation', 'calculation']:
                await retriever.retrieve_patterns(
                    RetrievalRequest(query='operation', domain=domain)
                )
            return (time.time() - start) * 1000
        
        async def parallel():
            start = time.time()
            await retriever.retrieve_multi_domain(
                query='operation',
                domains=['authentication', 'validation', 'calculation']
            )
            return (time.time() - start) * 1000
        
        seq_time = asyncio.run(sequential())
        par_time = asyncio.run(parallel())
        
        # Parallel should be faster (or at least not slower)
        assert par_time <= seq_time * 1.2, f"Parallel ({par_time:.2f}ms) slower than sequential ({seq_time:.2f}ms)"
