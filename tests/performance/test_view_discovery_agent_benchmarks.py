"""
Performance benchmarks for ViewDiscoveryAgent

Validates CORTEX performance standards:
- Initialization: <100ms
- Single file parse: <500ms  
- Bulk parsing: 10 files <5s
- Memory: <20MB single, <50MB bulk
- CPU: <50% single, <70% sustained
- Scalability: 100 files <30s

Created: 2025-11-26
Author: Asif Hussain
"""

import pytest
import time
import psutil
import os
from pathlib import Path
from src.agents.view_discovery_agent import ViewDiscoveryAgent, discover_views_for_testing


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def tmp_path(tmp_path_factory):
    """Create temporary directory for test files."""
    return tmp_path_factory.mktemp("benchmark_tests")


@pytest.fixture
def create_razor_files():
    """Factory to create multiple Razor files for benchmarking."""
    def _create_files(directory: Path, count: int, elements_per_file: int = 5):
        """Create specified number of Razor files with elements."""
        files = []
        for i in range(count):
            content = f'@page "/page{i}"\n\n<div class="container">\n'
            
            for j in range(elements_per_file):
                content += f'  <input id="input{i}_{j}" type="text" placeholder="Field {j}" />\n'
                content += f'  <button id="btn{i}_{j}" class="btn">Button {j}</button>\n'
            
            content += '</div>\n'
            
            file_path = directory / f"Page{i}.razor"
            file_path.write_text(content, encoding='utf-8')
            files.append(file_path)
        
        return files
    
    return _create_files


@pytest.fixture
def process():
    """Get current process for resource monitoring."""
    return psutil.Process(os.getpid())


# ============================================================================
# TEST CLASS 1: Performance Benchmarks
# ============================================================================

class TestViewDiscoveryAgentPerformance:
    """Test core performance metrics."""
    
    def test_initialization_speed(self, tmp_path, benchmark_result={}):
        """Test initialization completes in <100ms."""
        iterations = 10
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            agent = ViewDiscoveryAgent(project_root=tmp_path)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"\n  Initialization avg: {avg_time:.2f}ms, max: {max_time:.2f}ms")
        
        assert avg_time < 100, f"Average initialization time {avg_time:.2f}ms exceeds 100ms"
        assert max_time < 150, f"Max initialization time {max_time:.2f}ms exceeds 150ms"
    
    def test_single_file_parse_speed(self, tmp_path, create_razor_files):
        """Test single file parsing completes in <500ms."""
        files = create_razor_files(tmp_path, 1, elements_per_file=10)
        agent = ViewDiscoveryAgent(project_root=tmp_path)
        
        iterations = 5
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            results = agent.discover_views(files, save_to_db=False)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"\n  Single file avg: {avg_time:.2f}ms, max: {max_time:.2f}ms")
        print(f"  Elements discovered: {len(results['elements_discovered'])}")
        
        assert avg_time < 500, f"Average parse time {avg_time:.2f}ms exceeds 500ms"
        assert max_time < 800, f"Max parse time {max_time:.2f}ms exceeds 800ms"
    
    def test_bulk_10_files_speed(self, tmp_path, create_razor_files):
        """Test bulk parsing of 10 files completes in <5s."""
        files = create_razor_files(tmp_path, 10, elements_per_file=5)
        agent = ViewDiscoveryAgent(project_root=tmp_path)
        
        start = time.perf_counter()
        results = agent.discover_views(files, save_to_db=False)
        end = time.perf_counter()
        
        elapsed = (end - start) * 1000  # Convert to ms
        avg_per_file = elapsed / 10
        
        print(f"\n  Total time: {elapsed:.2f}ms ({elapsed/1000:.2f}s)")
        print(f"  Avg per file: {avg_per_file:.2f}ms")
        print(f"  Files processed: {len(results['files_processed'])}")
        print(f"  Elements discovered: {len(results['elements_discovered'])}")
        
        assert elapsed < 5000, f"Bulk 10 files time {elapsed:.2f}ms exceeds 5000ms"
        assert avg_per_file < 800, f"Avg per file {avg_per_file:.2f}ms exceeds 800ms"


# ============================================================================
# TEST CLASS 2: Memory Usage Benchmarks
# ============================================================================

class TestViewDiscoveryAgentMemory:
    """Test memory usage stays within limits."""
    
    def test_single_file_memory_usage(self, tmp_path, create_razor_files, process):
        """Test single file parsing uses <20MB."""
        files = create_razor_files(tmp_path, 1, elements_per_file=20)
        
        # Baseline memory
        baseline_mb = process.memory_info().rss / 1024 / 1024
        
        agent = ViewDiscoveryAgent(project_root=tmp_path)
        results = agent.discover_views(files, save_to_db=False)
        
        # Peak memory
        peak_mb = process.memory_info().rss / 1024 / 1024
        memory_used = peak_mb - baseline_mb
        
        print(f"\n  Memory used: {memory_used:.2f}MB")
        print(f"  Elements discovered: {len(results['elements_discovered'])}")
        print(f"  Memory per element: {(memory_used * 1024) / len(results['elements_discovered']):.2f}KB")
        
        assert memory_used < 20, f"Memory usage {memory_used:.2f}MB exceeds 20MB"
    
    def test_bulk_files_memory_usage(self, tmp_path, create_razor_files, process):
        """Test bulk parsing uses <50MB."""
        files = create_razor_files(tmp_path, 20, elements_per_file=10)
        
        # Baseline memory
        baseline_mb = process.memory_info().rss / 1024 / 1024
        
        agent = ViewDiscoveryAgent(project_root=tmp_path)
        results = agent.discover_views(files, save_to_db=False)
        
        # Peak memory
        peak_mb = process.memory_info().rss / 1024 / 1024
        memory_used = peak_mb - baseline_mb
        
        print(f"\n  Memory used: {memory_used:.2f}MB")
        print(f"  Files processed: {len(results['files_processed'])}")
        print(f"  Elements discovered: {len(results['elements_discovered'])}")
        
        assert memory_used < 50, f"Memory usage {memory_used:.2f}MB exceeds 50MB"


# ============================================================================
# TEST CLASS 3: CPU Usage Benchmarks
# ============================================================================

class TestViewDiscoveryAgentCPU:
    """Test CPU usage stays within limits."""
    
    def test_single_file_cpu_usage(self, tmp_path, create_razor_files, process):
        """Test single file parsing uses <50% CPU."""
        files = create_razor_files(tmp_path, 1, elements_per_file=20)
        agent = ViewDiscoveryAgent(project_root=tmp_path)
        
        # Monitor CPU during operation
        cpu_samples = []
        
        def monitor_cpu():
            for _ in range(5):
                cpu_samples.append(process.cpu_percent(interval=0.1))
        
        import threading
        monitor = threading.Thread(target=monitor_cpu, daemon=True)
        monitor.start()
        
        results = agent.discover_views(files, save_to_db=False)
        
        monitor.join(timeout=2)
        
        if cpu_samples:
            avg_cpu = sum(cpu_samples) / len(cpu_samples)
            max_cpu = max(cpu_samples)
            
            print(f"\n  CPU avg: {avg_cpu:.1f}%, max: {max_cpu:.1f}%")
            print(f"  Elements discovered: {len(results['elements_discovered'])}")
            
            assert avg_cpu < 50, f"Average CPU {avg_cpu:.1f}% exceeds 50%"
    
    def test_sustained_cpu_usage(self, tmp_path, create_razor_files, process):
        """Test sustained parsing uses <70% CPU."""
        files = create_razor_files(tmp_path, 10, elements_per_file=10)
        agent = ViewDiscoveryAgent(project_root=tmp_path)
        
        # Monitor CPU during sustained operation
        cpu_samples = []
        
        def monitor_cpu():
            for _ in range(10):
                cpu_samples.append(process.cpu_percent(interval=0.1))
        
        import threading
        monitor = threading.Thread(target=monitor_cpu, daemon=True)
        monitor.start()
        
        results = agent.discover_views(files, save_to_db=False)
        
        monitor.join(timeout=3)
        
        if cpu_samples:
            avg_cpu = sum(cpu_samples) / len(cpu_samples)
            max_cpu = max(cpu_samples)
            
            print(f"\n  Sustained CPU avg: {avg_cpu:.1f}%, max: {max_cpu:.1f}%")
            print(f"  Files processed: {len(results['files_processed'])}")
            
            assert avg_cpu < 70, f"Average sustained CPU {avg_cpu:.1f}% exceeds 70%"


# ============================================================================
# TEST CLASS 4: Scalability Benchmarks
# ============================================================================

class TestViewDiscoveryAgentScalability:
    """Test scalability with large numbers of files."""
    
    def test_100_files_scalability(self, tmp_path, create_razor_files):
        """Test parsing 100 files completes in <30s."""
        files = create_razor_files(tmp_path, 100, elements_per_file=5)
        agent = ViewDiscoveryAgent(project_root=tmp_path)
        
        start = time.perf_counter()
        results = agent.discover_views(files, save_to_db=False)
        end = time.perf_counter()
        
        elapsed_s = end - start
        throughput = 100 / elapsed_s
        avg_per_file_ms = (elapsed_s * 1000) / 100
        
        print(f"\n  Total time: {elapsed_s:.2f}s")
        print(f"  Throughput: {throughput:.1f} files/sec")
        print(f"  Avg per file: {avg_per_file_ms:.2f}ms")
        print(f"  Total elements: {len(results['elements_discovered'])}")
        
        assert elapsed_s < 30, f"100 files took {elapsed_s:.2f}s, exceeds 30s"
        assert throughput > 3, f"Throughput {throughput:.1f} files/sec below minimum 3/sec"
    
    def test_large_file_handling(self, tmp_path):
        """Test handling large file with many elements."""
        # Create file with 100 elements
        content = '@page "/large"\n\n<div class="container">\n'
        for i in range(100):
            content += f'  <input id="input{i}" type="text" />\n'
            content += f'  <button id="btn{i}" class="btn">Button {i}</button>\n'
            content += f'  <select id="select{i}"><option>Option</option></select>\n'
        content += '</div>\n'
        
        file_path = tmp_path / "LargePage.razor"
        file_path.write_text(content, encoding='utf-8')
        
        agent = ViewDiscoveryAgent(project_root=tmp_path)
        
        start = time.perf_counter()
        results = agent.discover_views([file_path], save_to_db=False)
        end = time.perf_counter()
        
        elapsed_ms = (end - start) * 1000
        
        print(f"\n  Parse time: {elapsed_ms:.2f}ms")
        print(f"  Elements discovered: {len(results['elements_discovered'])}")
        print(f"  Time per element: {elapsed_ms / len(results['elements_discovered']):.2f}ms")
        
        assert elapsed_ms < 2000, f"Large file parse {elapsed_ms:.2f}ms exceeds 2000ms"
        assert len(results['elements_discovered']) >= 200, "Should discover at least 200 elements"


# ============================================================================
# TEST CLASS 5: Database Performance
# ============================================================================

class TestViewDiscoveryAgentDatabasePerformance:
    """Test database operation performance."""
    
    def test_database_save_speed(self, tmp_path, create_razor_files):
        """Test database saves complete quickly."""
        import sqlite3
        import tempfile
        
        # Create temp database
        db_fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(db_fd)
        db_path = Path(db_path)
        
        # Create schema
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE tier2_element_mappings (
                project_name TEXT,
                component_path TEXT,
                element_id TEXT,
                element_type TEXT,
                data_testid TEXT,
                css_classes TEXT,
                selector_strategy TEXT,
                selector_priority INTEGER,
                user_facing_text TEXT,
                line_number INTEGER,
                attributes TEXT,
                discovered_at TIMESTAMP,
                last_verified TIMESTAMP,
                PRIMARY KEY (project_name, component_path, line_number)
            )
        """)
        conn.commit()
        conn.close()
        
        try:
            files = create_razor_files(tmp_path, 10, elements_per_file=10)
            agent = ViewDiscoveryAgent(project_root=tmp_path, db_path=db_path)
            
            # Discover first
            results = agent.discover_views(files, save_to_db=False)
            elements = results['elements_discovered']
            
            # Time database save
            start = time.perf_counter()
            success = agent.save_to_database("TestProject", elements)
            end = time.perf_counter()
            
            elapsed_ms = (end - start) * 1000
            per_element_ms = elapsed_ms / len(elements)
            
            print(f"\n  Save time: {elapsed_ms:.2f}ms")
            print(f"  Elements saved: {len(elements)}")
            print(f"  Time per element: {per_element_ms:.2f}ms")
            
            assert success, "Database save failed"
            assert elapsed_ms < 1000, f"DB save {elapsed_ms:.2f}ms exceeds 1000ms"
            assert per_element_ms < 10, f"Per-element save {per_element_ms:.2f}ms exceeds 10ms"
        
        finally:
            db_path.unlink()
    
    def test_database_load_speed(self, tmp_path, create_razor_files):
        """Test database loads complete quickly."""
        import sqlite3
        import tempfile
        
        # Create temp database
        db_fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(db_fd)
        db_path = Path(db_path)
        
        # Create schema
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE tier2_element_mappings (
                project_name TEXT,
                component_path TEXT,
                element_id TEXT,
                element_type TEXT,
                data_testid TEXT,
                css_classes TEXT,
                selector_strategy TEXT,
                selector_priority INTEGER,
                user_facing_text TEXT,
                line_number INTEGER,
                attributes TEXT,
                discovered_at TIMESTAMP,
                last_verified TIMESTAMP,
                PRIMARY KEY (project_name, component_path, line_number)
            )
        """)
        conn.commit()
        conn.close()
        
        try:
            files = create_razor_files(tmp_path, 10, elements_per_file=10)
            agent = ViewDiscoveryAgent(project_root=tmp_path, db_path=db_path)
            
            # Save first
            results = agent.discover_views(files, save_to_db=True, project_name="TestProject")
            
            # Time database load
            start = time.perf_counter()
            elements = agent.load_from_database("TestProject")
            end = time.perf_counter()
            
            elapsed_ms = (end - start) * 1000
            per_element_ms = elapsed_ms / len(elements)
            
            print(f"\n  Load time: {elapsed_ms:.2f}ms")
            print(f"  Elements loaded: {len(elements)}")
            print(f"  Time per element: {per_element_ms:.2f}ms")
            
            assert len(elements) > 0, "No elements loaded"
            assert elapsed_ms < 500, f"DB load {elapsed_ms:.2f}ms exceeds 500ms"
            assert per_element_ms < 5, f"Per-element load {per_element_ms:.2f}ms exceeds 5ms"
        
        finally:
            db_path.unlink()


# ============================================================================
# TEST CLASS 6: Response Time Percentiles
# ============================================================================

class TestViewDiscoveryAgentResponseTimes:
    """Test P95 and P99 response times."""
    
    def test_p95_parse_time(self, tmp_path, create_razor_files):
        """Test P95 parse time <800ms."""
        files = create_razor_files(tmp_path, 1, elements_per_file=15)
        agent = ViewDiscoveryAgent(project_root=tmp_path)
        
        # Run 100 iterations
        times = []
        for _ in range(100):
            start = time.perf_counter()
            results = agent.discover_views(files, save_to_db=False)
            end = time.perf_counter()
            times.append((end - start) * 1000)
        
        times.sort()
        p50 = times[49]
        p95 = times[94]
        p99 = times[98]
        
        print(f"\n  P50: {p50:.2f}ms")
        print(f"  P95: {p95:.2f}ms")
        print(f"  P99: {p99:.2f}ms")
        
        assert p95 < 800, f"P95 {p95:.2f}ms exceeds 800ms"
    
    def test_p99_parse_time(self, tmp_path, create_razor_files):
        """Test P99 parse time <1500ms."""
        files = create_razor_files(tmp_path, 1, elements_per_file=15)
        agent = ViewDiscoveryAgent(project_root=tmp_path)
        
        # Run 100 iterations
        times = []
        for _ in range(100):
            start = time.perf_counter()
            results = agent.discover_views(files, save_to_db=False)
            end = time.perf_counter()
            times.append((end - start) * 1000)
        
        times.sort()
        p99 = times[98]
        max_time = max(times)
        
        print(f"\n  P99: {p99:.2f}ms")
        print(f"  Max: {max_time:.2f}ms")
        
        assert p99 < 1500, f"P99 {p99:.2f}ms exceeds 1500ms"


# ============================================================================
# TEST CLASS 7: Performance Summary
# ============================================================================

class TestViewDiscoveryAgentPerformanceSummary:
    """Generate performance summary report."""
    
    def test_performance_summary(self, tmp_path, create_razor_files, process):
        """Generate comprehensive performance summary."""
        # Create subdirectories
        (tmp_path / "set1").mkdir(exist_ok=True)
        (tmp_path / "set10").mkdir(exist_ok=True)
        
        files_1 = create_razor_files(tmp_path / "set1", 1, elements_per_file=10)
        files_10 = create_razor_files(tmp_path / "set10", 10, elements_per_file=5)
        
        agent = ViewDiscoveryAgent(project_root=tmp_path)
        
        # Initialization
        start = time.perf_counter()
        agent_init = ViewDiscoveryAgent(project_root=tmp_path)
        init_time = (time.perf_counter() - start) * 1000
        
        # Single file
        baseline_mem = process.memory_info().rss / 1024 / 1024
        start = time.perf_counter()
        result_1 = agent.discover_views(files_1, save_to_db=False)
        single_time = (time.perf_counter() - start) * 1000
        single_mem = (process.memory_info().rss / 1024 / 1024) - baseline_mem
        
        # Bulk files
        baseline_mem = process.memory_info().rss / 1024 / 1024
        start = time.perf_counter()
        result_10 = agent.discover_views(files_10, save_to_db=False)
        bulk_time = (time.perf_counter() - start) * 1000
        bulk_mem = (process.memory_info().rss / 1024 / 1024) - baseline_mem
        
        print("\n" + "="*70)
        print("ViewDiscoveryAgent Performance Summary")
        print("="*70)
        print(f"Initialization:        {init_time:>8.2f}ms  (target: <100ms)")
        print(f"Single file parse:     {single_time:>8.2f}ms  (target: <500ms)")
        print(f"Bulk 10 files:         {bulk_time:>8.2f}ms  (target: <5000ms)")
        print(f"Single file memory:    {single_mem:>8.2f}MB  (target: <20MB)")
        print(f"Bulk files memory:     {bulk_mem:>8.2f}MB  (target: <50MB)")
        print(f"Elements discovered:   {len(result_1['elements_discovered']) + len(result_10['elements_discovered']):>8}")
        print("="*70)
        
        # All benchmarks should pass
        assert init_time < 100
        assert single_time < 500
        assert bulk_time < 5000
        assert single_mem < 20
        assert bulk_mem < 50


# ============================================================================
# RUN BENCHMARKS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
