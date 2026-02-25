# Tutorial: Performance Analysis

**Time:** 45 minutes | **Level:** Advanced  
**Goal:** Analyze and optimize CORTEX performance

## Overview

Performance optimization requires systematic analysis to identify bottlenecks and opportunities. This tutorial covers profiling, benchmarking, and optimization.

## Prerequisites

- [Monitoring Dashboard](2-monitoring-dashboard.md) completed
- [Incident Response](3-incident-response.md) completed
- Profiling tools knowledge

## Step 1: Performance Profiling

```python
import cProfile
import pstats
from io import StringIO
import asyncio

class PerformanceProfiler:
    @staticmethod
    def profile_function(func, *args, **kwargs):
        """Profile a function."""
        profiler = cProfile.Profile()
        profiler.enable()
        
        result = func(*args, **kwargs)
        
        profiler.disable()
        
        stats = pstats.Stats(profiler, stream=StringIO())
        stats.sort_stats('cumulative')
        stats.print_stats(10)
        
        return result, stats
    
    @staticmethod
    def profile_orchestrator_call(orchestrator, intent):
        """Profile orchestrator execution."""
        import time
        
        start = time.perf_counter()
        
        result = orchestrator.process(intent)
        
        duration = time.perf_counter() - start
        
        return {
            "duration_ms": duration * 1000,
            "result": result
        }

# Usage
from cortex.types import Intent

orchestrator = HelloWorldOrchestrator()
intent = Intent(content="test", user_id="alice")

profile_result, stats = PerformanceProfiler.profile_function(
    orchestrator.process,
    intent
)
```

## Step 2: Benchmarking

```python
import time
from statistics import mean, stdev

class Benchmark:
    def __init__(self, name: str, iterations: int = 100):
        self.name = name
        self.iterations = iterations
        self.results = []
    
    def run(self, func, *args, **kwargs):
        """Run benchmark."""
        print(f"Running {self.name}...")
        
        for i in range(self.iterations):
            start = time.perf_counter()
            func(*args, **kwargs)
            duration = time.perf_counter() - start
            self.results.append(duration * 1000)  # ms
        
        return self.get_summary()
    
    def get_summary(self) -> dict:
        """Get benchmark summary."""
        return {
            "name": self.name,
            "iterations": self.iterations,
            "min_ms": min(self.results),
            "max_ms": max(self.results),
            "mean_ms": mean(self.results),
            "median_ms": self.results[len(self.results) // 2],
            "stdev_ms": stdev(self.results) if len(self.results) > 1 else 0
        }

# Usage
def test_orchestrator():
    orchestrator = HelloWorldOrchestrator()
    intent = Intent(content="test", user_id="alice")
    orchestrator.process(intent)

benchmark = Benchmark("HelloWorld Orchestrator", iterations=1000)
summary = benchmark.run(test_orchestrator)
print(f"Average latency: {summary['mean_ms']:.2f}ms")
```

## Step 3: Query Optimization

```python
class QueryOptimization:
    @staticmethod
    def analyze_slow_queries(threshold_ms: int = 100) -> list:
        """Identify slow queries."""
        # This would connect to database and analyze slow queries
        return [
            {
                "query": "SELECT * FROM knowledge WHERE domain = ?",
                "execution_time_ms": 245,
                "rows_scanned": 50000,
                "optimization": "Add index on domain column"
            },
            {
                "query": "SELECT * FROM audit_trail WHERE created_at > ?",
                "execution_time_ms": 367,
                "rows_scanned": 100000,
                "optimization": "Add index on created_at column"
            }
        ]
    
    @staticmethod
    def apply_optimizations(database):
        """Apply query optimizations."""
        optimizations = [
            "CREATE INDEX idx_knowledge_domain ON knowledge(domain);",
            "CREATE INDEX idx_audit_trail_created ON audit_trail(created_at);",
            "CREATE INDEX idx_orchestrator_user ON orchestrator_calls(user_id);"
        ]
        
        for opt in optimizations:
            print(f"Applying: {opt}")
            database.execute(opt)

# Usage
slow_queries = QueryOptimization.analyze_slow_queries()
for query in slow_queries:
    print(f"Query: {query['query']}")
    print(f"Time: {query['execution_time_ms']}ms")
    print(f"Optimization: {query['optimization']}")
```

## Step 4: Caching Strategy

```python
from functools import lru_cache
import hashlib

class CachingStrategy:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def cache_key(self, *args, **kwargs) -> str:
        """Generate cache key."""
        key_str = str(args) + str(kwargs)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get_or_execute(self, func, *args, **kwargs):
        """Get from cache or execute function."""
        key = self.cache_key(*args, **kwargs)
        
        if key in self.cache:
            cached_value, timestamp = self.cache[key]
            import time
            if time.time() - timestamp < self.ttl_seconds:
                self.cache_hits += 1
                return cached_value
        
        # Execute and cache
        result = func(*args, **kwargs)
        import time
        self.cache[key] = (result, time.time())
        self.cache_misses += 1
        
        return result
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        
        return {
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "hit_rate": hit_rate,
            "cache_size": len(self.cache)
        }

# Usage
cache = CachingStrategy()

def expensive_operation(x):
    import time
    time.sleep(0.1)  # Simulate expensive operation
    return x * 2

result = cache.get_or_execute(expensive_operation, 5)
print(cache.get_stats())
```

## Step 5: Load Testing

```python
import concurrent.futures
import time

class LoadTest:
    def __init__(self, orchestrator, intent_count: int = 1000):
        self.orchestrator = orchestrator
        self.intent_count = intent_count
        self.results = []
    
    def run_sequential(self):
        """Run sequential load test."""
        start = time.perf_counter()
        
        for i in range(self.intent_count):
            intent = Intent(
                content=f"test_{i}",
                user_id=f"user_{i % 10}"
            )
            self.orchestrator.process(intent)
        
        duration = time.perf_counter() - start
        
        return {
            "mode": "sequential",
            "total_time_s": duration,
            "requests_per_second": self.intent_count / duration,
            "avg_latency_ms": (duration * 1000) / self.intent_count
        }
    
    def run_concurrent(self, workers: int = 10):
        """Run concurrent load test."""
        start = time.perf_counter()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = []
            
            for i in range(self.intent_count):
                intent = Intent(
                    content=f"test_{i}",
                    user_id=f"user_{i % 10}"
                )
                future = executor.submit(self.orchestrator.process, intent)
                futures.append(future)
            
            # Wait for all to complete
            concurrent.futures.wait(futures)
        
        duration = time.perf_counter() - start
        
        return {
            "mode": "concurrent",
            "workers": workers,
            "total_time_s": duration,
            "requests_per_second": self.intent_count / duration,
            "avg_latency_ms": (duration * 1000) / self.intent_count
        }

# Usage
orchestrator = HelloWorldOrchestrator()
load_test = LoadTest(orchestrator, intent_count=1000)

seq_results = load_test.run_sequential()
print(f"Sequential: {seq_results['requests_per_second']:.1f} req/s")

concurrent_results = load_test.run_concurrent(workers=10)
print(f"Concurrent: {concurrent_results['requests_per_second']:.1f} req/s")
```

## Performance Optimization Checklist

- [ ] Identify bottlenecks with profiling
- [ ] Benchmark current performance
- [ ] Analyze slow queries
- [ ] Implement caching strategy
- [ ] Add indexes to database
- [ ] Optimize algorithms
- [ ] Run load tests
- [ ] Monitor production metrics

## Key Performance Metrics

| Metric | Target | Alert |
|--------|--------|-------|
| P95 Latency | < 500ms | > 1s |
| P99 Latency | < 1s | > 2s |
| Requests/sec | > 100 | < 50 |
| Error Rate | < 0.1% | > 1% |
| Cache Hit Rate | > 80% | < 60% |

## Next Steps

- [Operations Guide](../../04-guides/operations/0-overview.md) - Full ops guide
- [Deployment](../../04-guides/deployment/0-overview.md) - Production deployment
