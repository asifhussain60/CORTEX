"""
Test Suite for ParallelOrchestrationCoordinator (Feature 14)

Phase: 14.1 (RED)
Purpose: Validate parallel phase execution with dependency resolution and error isolation

Test Coverage:
- BasicParallelExecution: execute_parallel_phases with independent phases
- DependencyGraphResolution: DAG-based execution order with dependencies
- ResourceLocking: Concurrent file/resource access without conflicts
- ErrorIsolation: One phase failure doesn't cascade to independent phases
- PerformanceValidation: 2-3x speedup for independent phases vs sequential
- PhaseOrdering: Topological sort respects dependencies
- ConcurrentPhaseExecution: Multiple phases execute simultaneously

Author: Asif Hussain
Created: December 13, 2024
"""

import pytest
import asyncio
import time
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile
import shutil

from src.operations.utilities.parallel_orchestration_coordinator import (
    ParallelOrchestrationCoordinator,
    PhaseDefinition,
    DependencyError,
    ResourceLockError
)


class TestBasicParallelExecution:
    """Test basic parallel phase execution for independent phases."""
    
    @pytest.mark.asyncio
    async def test_execute_two_independent_phases_concurrently(self):
        """Test that two independent phases execute in parallel."""
        coordinator = ParallelOrchestrationCoordinator()
        
        execution_log = []
        
        async def phase_a():
            execution_log.append(('phase_a', 'start'))
            await asyncio.sleep(0.1)
            execution_log.append(('phase_a', 'end'))
            return {'status': 'success', 'phase': 'A'}
        
        async def phase_b():
            execution_log.append(('phase_b', 'start'))
            await asyncio.sleep(0.1)
            execution_log.append(('phase_b', 'end'))
            return {'status': 'success', 'phase': 'B'}
        
        phases = [
            PhaseDefinition(phase_id='A', phase_func=phase_a, dependencies=[]),
            PhaseDefinition(phase_id='B', phase_func=phase_b, dependencies=[])
        ]
        
        start_time = time.time()
        results = await coordinator.execute_parallel_phases(phases)
        elapsed = time.time() - start_time
        
        # Both phases should complete successfully
        assert len(results) == 2
        assert results['A']['status'] == 'success'
        assert results['B']['status'] == 'success'
        
        # Should take ~0.1s (parallel), not ~0.2s (sequential)
        assert elapsed < 0.15, f"Parallel execution took {elapsed}s (expected <0.15s)"
        
        # Both phases should start before either ends (proof of parallelism)
        starts = [log for log in execution_log if log[1] == 'start']
        first_end = next(log for log in execution_log if log[1] == 'end')
        first_end_index = execution_log.index(first_end)
        
        assert len(starts) == 2
        assert first_end_index >= 2, "Both phases should start before first phase ends"
    
    @pytest.mark.asyncio
    async def test_execute_three_independent_phases(self):
        """Test parallel execution of three independent phases."""
        coordinator = ParallelOrchestrationCoordinator()
        
        async def make_phase(phase_id: str):
            await asyncio.sleep(0.05)
            return {'phase_id': phase_id, 'status': 'completed'}
        
        phases = [
            PhaseDefinition(phase_id='A', phase_func=lambda: make_phase('A'), dependencies=[]),
            PhaseDefinition(phase_id='B', phase_func=lambda: make_phase('B'), dependencies=[]),
            PhaseDefinition(phase_id='C', phase_func=lambda: make_phase('C'), dependencies=[])
        ]
        
        start_time = time.time()
        results = await coordinator.execute_parallel_phases(phases)
        elapsed = time.time() - start_time
        
        assert len(results) == 3
        assert all(results[pid]['status'] == 'completed' for pid in ['A', 'B', 'C'])
        
        # Should take ~0.05s (parallel), not ~0.15s (sequential)
        assert elapsed < 0.1, f"Expected <0.1s, got {elapsed}s"
    
    @pytest.mark.asyncio
    async def test_empty_phase_list_returns_empty_results(self):
        """Test that empty phase list returns empty results dict."""
        coordinator = ParallelOrchestrationCoordinator()
        
        results = await coordinator.execute_parallel_phases([])
        
        assert results == {}


class TestDependencyGraphResolution:
    """Test DAG-based dependency resolution and execution ordering."""
    
    @pytest.mark.asyncio
    async def test_sequential_dependencies_execute_in_order(self):
        """Test that phases with sequential dependencies execute in correct order."""
        coordinator = ParallelOrchestrationCoordinator()
        
        execution_order = []
        
        async def phase_a():
            execution_order.append('A')
            return {'phase': 'A'}
        
        async def phase_b():
            execution_order.append('B')
            return {'phase': 'B'}
        
        async def phase_c():
            execution_order.append('C')
            return {'phase': 'C'}
        
        # A → B → C (sequential chain)
        phases = [
            PhaseDefinition(phase_id='C', phase_func=phase_c, dependencies=['B']),
            PhaseDefinition(phase_id='A', phase_func=phase_a, dependencies=[]),
            PhaseDefinition(phase_id='B', phase_func=phase_b, dependencies=['A'])
        ]
        
        results = await coordinator.execute_parallel_phases(phases)
        
        # Verify execution order
        assert execution_order == ['A', 'B', 'C']
        assert len(results) == 3
    
    @pytest.mark.asyncio
    async def test_diamond_dependency_pattern(self):
        """Test diamond dependency pattern: A → B,C → D."""
        coordinator = ParallelOrchestrationCoordinator()
        
        execution_order = []
        
        async def phase_a():
            execution_order.append('A')
            await asyncio.sleep(0.05)
            return {'phase': 'A'}
        
        async def phase_b():
            execution_order.append('B')
            await asyncio.sleep(0.05)
            return {'phase': 'B'}
        
        async def phase_c():
            execution_order.append('C')
            await asyncio.sleep(0.05)
            return {'phase': 'C'}
        
        async def phase_d():
            execution_order.append('D')
            return {'phase': 'D'}
        
        # Diamond: A → B,C → D
        phases = [
            PhaseDefinition(phase_id='A', phase_func=phase_a, dependencies=[]),
            PhaseDefinition(phase_id='B', phase_func=phase_b, dependencies=['A']),
            PhaseDefinition(phase_id='C', phase_func=phase_c, dependencies=['A']),
            PhaseDefinition(phase_id='D', phase_func=phase_d, dependencies=['B', 'C'])
        ]
        
        start_time = time.time()
        results = await coordinator.execute_parallel_phases(phases)
        elapsed = time.time() - start_time
        
        # A must execute first
        assert execution_order[0] == 'A'
        
        # B and C should execute after A (in any order)
        assert set(execution_order[1:3]) == {'B', 'C'}
        
        # D must execute last
        assert execution_order[3] == 'D'
        
        # B and C should run in parallel (total time ~0.1s, not ~0.15s)
        assert elapsed < 0.12, f"Expected <0.12s for parallel B+C, got {elapsed}s"
    
    @pytest.mark.asyncio
    async def test_circular_dependency_raises_error(self):
        """Test that circular dependencies are detected and raise DependencyError."""
        coordinator = ParallelOrchestrationCoordinator()
        
        async def dummy_phase():
            return {}
        
        # Circular: A → B → C → A
        phases = [
            PhaseDefinition(phase_id='A', phase_func=dummy_phase, dependencies=['C']),
            PhaseDefinition(phase_id='B', phase_func=dummy_phase, dependencies=['A']),
            PhaseDefinition(phase_id='C', phase_func=dummy_phase, dependencies=['B'])
        ]
        
        with pytest.raises(DependencyError, match="Circular dependency detected"):
            await coordinator.execute_parallel_phases(phases)
    
    @pytest.mark.asyncio
    async def test_missing_dependency_raises_error(self):
        """Test that missing phase dependencies raise DependencyError."""
        coordinator = ParallelOrchestrationCoordinator()
        
        async def phase_a():
            return {}
        
        # Phase B depends on non-existent phase Z
        phases = [
            PhaseDefinition(phase_id='A', phase_func=phase_a, dependencies=[]),
            PhaseDefinition(phase_id='B', phase_func=phase_a, dependencies=['Z'])
        ]
        
        with pytest.raises(DependencyError, match="Unknown dependency"):
            await coordinator.execute_parallel_phases(phases)


class TestResourceLocking:
    """Test concurrent resource access with locking."""
    
    @pytest.mark.asyncio
    async def test_file_resource_locking_prevents_conflicts(self):
        """Test that resource locking prevents concurrent file access conflicts."""
        coordinator = ParallelOrchestrationCoordinator()
        
        temp_dir = Path(tempfile.mkdtemp())
        test_file = temp_dir / "shared_resource.txt"
        test_file.write_text("initial")
        
        write_order = []
        
        async def write_phase_a():
            async with coordinator.acquire_resource_lock('file:shared_resource.txt'):
                write_order.append('A_start')
                await asyncio.sleep(0.1)
                content = test_file.read_text()
                test_file.write_text(content + "_A")
                write_order.append('A_end')
            return {'phase': 'A'}
        
        async def write_phase_b():
            async with coordinator.acquire_resource_lock('file:shared_resource.txt'):
                write_order.append('B_start')
                await asyncio.sleep(0.1)
                content = test_file.read_text()
                test_file.write_text(content + "_B")
                write_order.append('B_end')
            return {'phase': 'B'}
        
        phases = [
            PhaseDefinition(phase_id='A', phase_func=write_phase_a, dependencies=[]),
            PhaseDefinition(phase_id='B', phase_func=write_phase_b, dependencies=[])
        ]
        
        results = await coordinator.execute_parallel_phases(phases)
        
        # One phase should complete before the other starts (serialized by lock)
        assert write_order == ['A_start', 'A_end', 'B_start', 'B_end'] or \
               write_order == ['B_start', 'B_end', 'A_start', 'A_end']
        
        # File should contain both writes
        final_content = test_file.read_text()
        assert 'initial' in final_content
        assert '_A' in final_content
        assert '_B' in final_content
        
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_different_resources_dont_block_each_other(self):
        """Test that locks on different resources don't block each other."""
        coordinator = ParallelOrchestrationCoordinator()
        
        execution_log = []
        
        async def phase_resource_a():
            async with coordinator.acquire_resource_lock('resource_a'):
                execution_log.append('A_start')
                await asyncio.sleep(0.1)
                execution_log.append('A_end')
            return {}
        
        async def phase_resource_b():
            async with coordinator.acquire_resource_lock('resource_b'):
                execution_log.append('B_start')
                await asyncio.sleep(0.1)
                execution_log.append('B_end')
            return {}
        
        phases = [
            PhaseDefinition(phase_id='A', phase_func=phase_resource_a, dependencies=[]),
            PhaseDefinition(phase_id='B', phase_func=phase_resource_b, dependencies=[])
        ]
        
        start_time = time.time()
        results = await coordinator.execute_parallel_phases(phases)
        elapsed = time.time() - start_time
        
        # Different resources should execute in parallel
        assert elapsed < 0.15, f"Expected parallel execution <0.15s, got {elapsed}s"
        
        # Both should start before either ends
        starts = [log for log in execution_log if 'start' in log]
        assert len(starts) == 2
        first_end_index = min(execution_log.index('A_end'), execution_log.index('B_end'))
        assert first_end_index >= 2


class TestErrorIsolation:
    """Test that phase failures are isolated and don't cascade."""
    
    @pytest.mark.asyncio
    async def test_independent_phase_failure_doesnt_affect_others(self):
        """Test that failure in one independent phase doesn't stop others."""
        coordinator = ParallelOrchestrationCoordinator()
        
        async def phase_a_success():
            await asyncio.sleep(0.05)
            return {'status': 'success', 'phase': 'A'}
        
        async def phase_b_failure():
            await asyncio.sleep(0.05)
            raise ValueError("Phase B failed!")
        
        async def phase_c_success():
            await asyncio.sleep(0.05)
            return {'status': 'success', 'phase': 'C'}
        
        phases = [
            PhaseDefinition(phase_id='A', phase_func=phase_a_success, dependencies=[]),
            PhaseDefinition(phase_id='B', phase_func=phase_b_failure, dependencies=[]),
            PhaseDefinition(phase_id='C', phase_func=phase_c_success, dependencies=[])
        ]
        
        results = await coordinator.execute_parallel_phases(phases)
        
        # A and C should succeed
        assert results['A']['status'] == 'success'
        assert results['C']['status'] == 'success'
        
        # B should have error recorded
        assert 'error' in results['B']
        assert 'Phase B failed!' in results['B']['error']
    
    @pytest.mark.asyncio
    async def test_dependent_phase_skips_when_dependency_fails(self):
        """Test that phases depending on failed phases are skipped."""
        coordinator = ParallelOrchestrationCoordinator()
        
        async def phase_a_failure():
            raise RuntimeError("Phase A failed")
        
        async def phase_b_dependent():
            return {'status': 'success', 'phase': 'B'}
        
        # B depends on A
        phases = [
            PhaseDefinition(phase_id='A', phase_func=phase_a_failure, dependencies=[]),
            PhaseDefinition(phase_id='B', phase_func=phase_b_dependent, dependencies=['A'])
        ]
        
        results = await coordinator.execute_parallel_phases(phases)
        
        # A should have error
        assert 'error' in results['A']
        
        # B should be skipped due to failed dependency
        assert results['B']['status'] == 'skipped'
        assert 'dependency failed' in results['B'].get('reason', '').lower()
    
    @pytest.mark.asyncio
    async def test_partial_failure_in_diamond_pattern(self):
        """Test partial failure in diamond pattern: A → B(fail),C → D."""
        coordinator = ParallelOrchestrationCoordinator()
        
        async def phase_a():
            return {'phase': 'A'}
        
        async def phase_b_failure():
            raise Exception("B failed")
        
        async def phase_c():
            return {'phase': 'C'}
        
        async def phase_d():
            return {'phase': 'D'}
        
        phases = [
            PhaseDefinition(phase_id='A', phase_func=phase_a, dependencies=[]),
            PhaseDefinition(phase_id='B', phase_func=phase_b_failure, dependencies=['A']),
            PhaseDefinition(phase_id='C', phase_func=phase_c, dependencies=['A']),
            PhaseDefinition(phase_id='D', phase_func=phase_d, dependencies=['B', 'C'])
        ]
        
        results = await coordinator.execute_parallel_phases(phases)
        
        # A and C should succeed
        assert 'error' not in results['A']
        assert 'error' not in results['C']
        
        # B should fail
        assert 'error' in results['B']
        
        # D should be skipped (depends on failed B)
        assert results['D']['status'] == 'skipped'


class TestPerformanceValidation:
    """Test performance improvements from parallel execution."""
    
    @pytest.mark.asyncio
    async def test_parallel_speedup_for_independent_phases(self):
        """Test 2-3x speedup for independent phases vs sequential."""
        coordinator = ParallelOrchestrationCoordinator()
        
        async def slow_phase(phase_id: str):
            await asyncio.sleep(0.1)
            return {'phase_id': phase_id}
        
        # 5 independent phases, each taking 0.1s
        phases = [
            PhaseDefinition(
                phase_id=f'phase_{i}',
                phase_func=lambda i=i: slow_phase(f'phase_{i}'),
                dependencies=[]
            )
            for i in range(5)
        ]
        
        start_time = time.time()
        results = await coordinator.execute_parallel_phases(phases)
        elapsed = time.time() - start_time
        
        # Sequential would take 0.5s (5 * 0.1s)
        # Parallel should take ~0.1s (all at once)
        # Speedup: ~5x
        assert elapsed < 0.15, f"Expected <0.15s (parallel), got {elapsed}s"
        assert len(results) == 5
    
    @pytest.mark.asyncio
    async def test_benchmark_sequential_vs_parallel_execution(self):
        """Benchmark sequential vs parallel execution for performance comparison."""
        coordinator = ParallelOrchestrationCoordinator()
        
        async def compute_phase(phase_id: str):
            await asyncio.sleep(0.05)
            return {'phase_id': phase_id}
        
        phases = [
            PhaseDefinition(
                phase_id=f'phase_{i}',
                phase_func=lambda i=i: compute_phase(f'phase_{i}'),
                dependencies=[]
            )
            for i in range(10)
        ]
        
        # Parallel execution
        parallel_start = time.time()
        results = await coordinator.execute_parallel_phases(phases)
        parallel_elapsed = time.time() - parallel_start
        
        # Sequential execution (for comparison)
        sequential_start = time.time()
        for phase in phases:
            await phase.phase_func()
        sequential_elapsed = time.time() - sequential_start
        
        speedup = sequential_elapsed / parallel_elapsed
        
        # Should achieve at least 2x speedup
        assert speedup >= 2.0, f"Speedup: {speedup:.2f}x (expected ≥2x)"


class TestPhaseOrdering:
    """Test topological sort and phase ordering."""
    
    @pytest.mark.asyncio
    async def test_topological_sort_respects_dependencies(self):
        """Test that topological sort produces valid execution order."""
        coordinator = ParallelOrchestrationCoordinator()
        
        execution_order = []
        
        async def make_phase(phase_id: str):
            execution_order.append(phase_id)
            return {'phase_id': phase_id}
        
        # Complex dependency graph:
        # A → C → E
        # B → D → E
        phases = [
            PhaseDefinition(phase_id='E', phase_func=lambda: make_phase('E'), dependencies=['C', 'D']),
            PhaseDefinition(phase_id='C', phase_func=lambda: make_phase('C'), dependencies=['A']),
            PhaseDefinition(phase_id='D', phase_func=lambda: make_phase('D'), dependencies=['B']),
            PhaseDefinition(phase_id='A', phase_func=lambda: make_phase('A'), dependencies=[]),
            PhaseDefinition(phase_id='B', phase_func=lambda: make_phase('B'), dependencies=[])
        ]
        
        results = await coordinator.execute_parallel_phases(phases)
        
        # A and B should come before C and D
        assert execution_order.index('A') < execution_order.index('C')
        assert execution_order.index('B') < execution_order.index('D')
        
        # C and D should come before E
        assert execution_order.index('C') < execution_order.index('E')
        assert execution_order.index('D') < execution_order.index('E')


# Pytest fixtures
@pytest.fixture
def temp_dir():
    """Create a temporary directory for test resources."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)
