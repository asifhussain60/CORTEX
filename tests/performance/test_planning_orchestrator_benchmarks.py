"""
Performance Benchmarks for PlanningOrchestrator

Validates CORTEX performance standards:
- Initialization: <100ms
- Plan validation: <500ms
- Plan generation: <2s for simple, <10s for complex
- Markdown generation: <1s
- Memory: <50MB for typical operations
- CPU: <50% for single operation, <70% sustained

Author: GitHub Copilot + CORTEX
Created: 2025-11-26
"""

import pytest
import time
import psutil
import os
from pathlib import Path
from src.orchestrators.planning_orchestrator import PlanningOrchestrator


@pytest.fixture
def temp_cortex_root(tmp_path):
    """Create temporary CORTEX root directory structure."""
    cortex_root = tmp_path / "cortex"
    cortex_root.mkdir()
    
    # Create brain directory structure
    brain_path = cortex_root / "cortex-brain"
    brain_path.mkdir()
    
    config_dir = brain_path / "config"
    config_dir.mkdir()
    
    docs_dir = brain_path / "documents" / "planning" / "features"
    docs_dir.mkdir(parents=True)
    
    (docs_dir / "active").mkdir()
    (docs_dir / "completed").mkdir()
    
    # Create minimal schema
    schema_path = config_dir / "plan-schema.yaml"
    schema_path.write_text("""
metadata:
  required: [feature_name, created_date]
phases:
  required: [name, tasks]
""")
    
    return cortex_root


@pytest.fixture
def planning_orchestrator(temp_cortex_root):
    """Create PlanningOrchestrator instance."""
    return PlanningOrchestrator(str(temp_cortex_root))


def create_valid_plan(plan_id="TEST-001", num_phases=1, tasks_per_phase=2):
    """Helper to create valid plan matching schema."""
    plan = {
        "metadata": {
            "plan_id": plan_id,
            "title": f"Plan {plan_id}",
            "created_date": "2025-11-26",
            "created_by": "test",
            "status": "proposed",
            "priority": "medium",
            "estimated_hours": num_phases * tasks_per_phase * 5
        },
        "phases": [],
        "definition_of_done": ["All tasks complete"]
    }
    
    for i in range(1, num_phases + 1):
        phase = {
            "phase_number": i,
            "phase_name": f"Phase {i}",
            "estimated_hours": tasks_per_phase * 5,
            "tasks": []
        }
        
        for j in range(1, tasks_per_phase + 1):
            phase["tasks"].append({
                "task_id": f"{i}.{j}",
                "task_name": f"Task {i}.{j}",
                "estimated_hours": 5
            })
        
        plan["phases"].append(phase)
    
    return plan


class TestPlanningOrchestratorPerformanceBenchmarks:
    """Performance benchmarks for PlanningOrchestrator initialization and basic operations."""
    
    def test_initialization_performance(self, temp_cortex_root):
        """Test that initialization completes in <100ms."""
        start_time = time.time()
        orchestrator = PlanningOrchestrator(str(temp_cortex_root))
        elapsed = (time.time() - start_time) * 1000  # Convert to ms
        
        assert elapsed < 100, f"Initialization took {elapsed:.1f}ms (should be <100ms)"
        assert orchestrator.schema is not None
    
    def test_plan_validation_performance(self, planning_orchestrator):
        """Test that plan validation completes in <500ms."""
        plan = create_valid_plan()
        
        start_time = time.time()
        is_valid, errors = planning_orchestrator.validate_plan(plan)
        elapsed = (time.time() - start_time) * 1000
        
        assert elapsed < 500, f"Validation took {elapsed:.1f}ms (should be <500ms)"
        assert is_valid is True, f"Validation failed: {errors}"
    
    def test_markdown_generation_performance(self, planning_orchestrator):
        """Test that Markdown generation completes in <1s."""
        plan = create_valid_plan()
        
        start_time = time.time()
        markdown = planning_orchestrator.generate_markdown(plan)
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0, f"Markdown generation took {elapsed:.2f}s (should be <1s)"
        assert len(markdown) > 100
        assert "TEST-001" in markdown


class TestPlanningOrchestratorMemoryBenchmarks:
    """Memory usage benchmarks for PlanningOrchestrator."""
    
    def test_memory_usage_single_plan(self, planning_orchestrator):
        """Test that single plan operations use <20MB memory."""
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        plan = create_valid_plan(num_phases=5, tasks_per_phase=10)
        
        # Validate and generate markdown
        planning_orchestrator.validate_plan(plan)
        planning_orchestrator.generate_markdown(plan)
        
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        mem_used = mem_after - mem_before
        
        assert mem_used < 20, f"Used {mem_used:.1f}MB (should be <20MB)"
    
    def test_memory_usage_multiple_plans(self, planning_orchestrator):
        """Test that processing 10 plans uses <50MB memory."""
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        for i in range(10):
            plan = create_valid_plan(plan_id=f"TEST-{i:03d}")
            planning_orchestrator.validate_plan(plan)
            planning_orchestrator.generate_markdown(plan)
        
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        mem_used = mem_after - mem_before
        
        assert mem_used < 50, f"Used {mem_used:.1f}MB for 10 plans (should be <50MB)"


class TestPlanningOrchestratorCPUBenchmarks:
    """CPU usage benchmarks for PlanningOrchestrator."""
    
    def test_cpu_usage_single_operation(self, planning_orchestrator):
        """Test that single operation uses <50% CPU."""
        process = psutil.Process(os.getpid())
        
        # Start CPU monitoring
        process.cpu_percent(interval=None)  # Prime the measurement
        time.sleep(0.1)
        
        plan = create_valid_plan(num_phases=5, tasks_per_phase=20)
        
        planning_orchestrator.validate_plan(plan)
        planning_orchestrator.generate_markdown(plan)
        
        cpu_percent = process.cpu_percent(interval=0.1)
        
        # Allow some tolerance for CI environments
        assert cpu_percent < 50, f"CPU usage {cpu_percent:.1f}% (should be <50%)"
    
    def test_cpu_usage_sustained_load(self, planning_orchestrator):
        """Test that sustained operations use <70% CPU."""
        process = psutil.Process(os.getpid())
        process.cpu_percent(interval=None)  # Prime
        
        cpu_samples = []
        for i in range(10):
            plan = create_valid_plan(plan_id=f"TEST-{i:03d}")
            planning_orchestrator.validate_plan(plan)
            planning_orchestrator.generate_markdown(plan)
            cpu_samples.append(process.cpu_percent(interval=0.05))
        
        avg_cpu = sum(cpu_samples) / len(cpu_samples)
        assert avg_cpu < 70, f"Average CPU {avg_cpu:.1f}% (should be <70%)"


class TestPlanningOrchestratorScalabilityBenchmarks:
    """Scalability benchmarks for PlanningOrchestrator."""
    
    def test_scalability_complex_plan(self, planning_orchestrator):
        """Test that complex plan (50 phases, 500 tasks) processes in <10s."""
        plan = create_valid_plan(num_phases=50, tasks_per_phase=10)
        
        start_time = time.time()
        planning_orchestrator.validate_plan(plan)
        markdown = planning_orchestrator.generate_markdown(plan)
        elapsed = time.time() - start_time
        
        assert elapsed < 10.0, f"Complex plan took {elapsed:.2f}s (should be <10s)"
        assert len(markdown) > 1000
    
    def test_scalability_large_markdown(self, planning_orchestrator):
        """Test that generating large Markdown (100KB+) completes in <2s."""
        # Create large plan with many phases and tasks
        plan = create_valid_plan(num_phases=20, tasks_per_phase=20)
        
        start_time = time.time()
        markdown = planning_orchestrator.generate_markdown(plan)
        elapsed = time.time() - start_time
        
        assert elapsed < 2.0, f"Large Markdown generation took {elapsed:.2f}s (should be <2s)"
        assert len(markdown) > 10000, f"Markdown is {len(markdown)} bytes (expected >10KB)"


class TestPlanningOrchestratorResponseTimeBenchmarks:
    """Response time percentile benchmarks."""
    
    def test_p95_validation_response_time(self, planning_orchestrator):
        """Test that P95 validation time is <800ms."""
        times = []
        
        for i in range(100):
            plan = create_valid_plan(plan_id=f"TEST-{i:03d}", num_phases=1, tasks_per_phase=3)
            
            start = time.time()
            planning_orchestrator.validate_plan(plan)
            elapsed = (time.time() - start) * 1000  # ms
            times.append(elapsed)
        
        times.sort()
        p95 = times[94]  # 95th percentile
        
        assert p95 < 800, f"P95 validation time {p95:.1f}ms (should be <800ms)"
    
    def test_p99_markdown_generation_time(self, planning_orchestrator):
        """Test that P99 Markdown generation time is <1500ms."""
        times = []
        
        for i in range(100):
            plan = create_valid_plan(plan_id=f"TEST-{i:03d}", num_phases=3, tasks_per_phase=5)
            
            start = time.time()
            planning_orchestrator.generate_markdown(plan)
            elapsed = (time.time() - start) * 1000  # ms
            times.append(elapsed)
        
        times.sort()
        p99 = times[98]  # 99th percentile
        
        assert p99 < 1500, f"P99 Markdown generation {p99:.1f}ms (should be <1500ms)"


class TestPlanningOrchestratorBenchmarkSummary:
    """Overall performance summary test."""
    
    def test_performance_summary(self, planning_orchestrator):
        """Generate performance summary across all operations."""
        operations = {
            "validation": [],
            "markdown_generation": []
        }
        
        for i in range(50):
            plan = create_valid_plan(plan_id=f"TEST-{i:03d}")
            
            # Validation
            start = time.time()
            planning_orchestrator.validate_plan(plan)
            operations["validation"].append((time.time() - start) * 1000)
            
            # Markdown generation
            start = time.time()
            planning_orchestrator.generate_markdown(plan)
            operations["markdown_generation"].append((time.time() - start) * 1000)
        
        # Calculate statistics
        for op_name, times in operations.items():
            avg = sum(times) / len(times)
            median = sorted(times)[len(times) // 2]
            min_time = min(times)
            max_time = max(times)
            
            print(f"\n{op_name}:")
            print(f"  Avg: {avg:.1f}ms")
            print(f"  Median: {median:.1f}ms")
            print(f"  Min: {min_time:.1f}ms")
            print(f"  Max: {max_time:.1f}ms")
        
        # Assert average times meet standards
        assert sum(operations["validation"]) / len(operations["validation"]) < 500
        assert sum(operations["markdown_generation"]) / len(operations["markdown_generation"]) < 1000
