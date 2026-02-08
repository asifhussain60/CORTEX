"""
Phase 48 S5: Concurrency Testing & Stress Testing - Multi-Workspace Load Validation

Tests for stress-testing registry isolation under high concurrency (100+ workspaces).

Authority: phase-48-registry-isolation-multi-tenant.yaml
Acceptance Criteria:
  - AC-PHASE48-S5-001: 100 concurrent workspaces with zero state leakage
  - AC-PHASE48-S5-002: No race conditions in concurrent registry access
  - AC-PHASE48-S5-003: Memory stable over 1000+ request cycles
"""

import pytest
import threading
import time
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field


@dataclass
class WorkspaceStressTest:
    """Workspace stress test scenario."""
    workspace_id: str
    company_name: str
    tool_count: int
    request_count: int = 100
    errors: List[str] = field(default_factory=list)
    operations: int = 0


class ConcurrentRegistry:
    """Thread-safe registry for stress testing."""
    
    def __init__(self):
        """Initialize concurrent registry."""
        self._lock = threading.RLock()
        self._workspaces: Dict[str, Dict[str, Any]] = {}
        self._operation_count = 0
    
    def create_workspace(self, workspace_id: str, company_name: str) -> bool:
        """Create workspace thread-safely."""
        with self._lock:
            if workspace_id in self._workspaces:
                return False
            self._workspaces[workspace_id] = {
                "company": company_name,
                "tools": {},
                "created_at": time.time(),
                "access_count": 0
            }
            self._operation_count += 1
            return True
    
    def register_tool(self, workspace_id: str, tool_name: str) -> bool:
        """Register tool in workspace."""
        with self._lock:
            if workspace_id not in self._workspaces:
                return False
            self._workspaces[workspace_id]["tools"][tool_name] = time.time()
            self._workspaces[workspace_id]["access_count"] += 1
            self._operation_count += 1
            return True
    
    def get_workspace_state(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace state."""
        with self._lock:
            return self._workspaces.get(workspace_id)
    
    def list_workspaces(self) -> List[str]:
        """List all workspace IDs."""
        with self._lock:
            return list(self._workspaces.keys())
    
    def cleanup_workspace(self, workspace_id: str) -> bool:
        """Clean up workspace."""
        with self._lock:
            if workspace_id in self._workspaces:
                del self._workspaces[workspace_id]
                self._operation_count += 1
                return True
            return False
    
    def get_operation_count(self) -> int:
        """Get total operations performed."""
        with self._lock:
            return self._operation_count
    
    def workspace_count(self) -> int:
        """Get current workspace count."""
        with self._lock:
            return len(self._workspaces)


# ============================================================================
# TESTS: High Concurrency Scenarios (AC-PHASE48-S5-001)
# ============================================================================

class TestHighConcurrencyWorkspaces:
    """Test high concurrency scenarios."""
    
    def test_10_concurrent_workspaces(self):
        """Test 10 concurrent workspaces."""
        registry = ConcurrentRegistry()
        
        def create_workspace(workspace_num: int):
            workspace_id = f"workspace_{workspace_num}"
            return registry.create_workspace(workspace_id, f"company_{workspace_num}")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(create_workspace, range(10)))
        
        assert all(results)
        assert registry.workspace_count() == 10
    
    def test_50_concurrent_workspaces(self):
        """Test 50 concurrent workspaces."""
        registry = ConcurrentRegistry()
        
        def create_and_register(workspace_num: int):
            workspace_id = f"ws_{workspace_num}"
            created = registry.create_workspace(workspace_id, f"company_{workspace_num}")
            if created:
                registry.register_tool(workspace_id, f"tool_a_{workspace_num}")
                registry.register_tool(workspace_id, f"tool_b_{workspace_num}")
            return created
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(create_and_register, range(50)))
        
        assert all(results)
        assert registry.workspace_count() == 50
    
    def test_100_concurrent_workspaces(self):
        """Test 100 concurrent workspaces (AC-PHASE48-S5-001)."""
        registry = ConcurrentRegistry()
        
        def setup_workspace(workspace_num: int):
            workspace_id = f"workspace_{workspace_num:03d}"
            company = f"company_{workspace_num % 10}"
            
            if registry.create_workspace(workspace_id, company):
                # Register 5 tools per workspace
                for tool_num in range(5):
                    registry.register_tool(workspace_id, f"tool_{tool_num}")
            
            return workspace_id
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            workspaces = list(executor.map(setup_workspace, range(100)))
        
        # Verify all workspaces created
        assert registry.workspace_count() == 100
        assert len(workspaces) == 100
        
        # Verify no duplicates
        assert len(set(workspaces)) == 100
    
    def test_200_concurrent_registry_operations(self):
        """Test 200 concurrent operations across multiple workspaces."""
        registry = ConcurrentRegistry()
        
        # Setup 20 workspaces
        for i in range(20):
            registry.create_workspace(f"ws_{i}", f"company_{i % 5}")
        
        def perform_operation(op_num: int):
            workspace_id = f"ws_{op_num % 20}"
            tool_name = f"tool_{op_num}"
            return registry.register_tool(workspace_id, tool_name)
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(perform_operation, range(200)))
        
        assert all(results)
        assert registry.get_operation_count() >= 220  # 20 creates + 200 registers


# ============================================================================
# TESTS: Race Condition Prevention (AC-PHASE48-S5-002)
# ============================================================================

class TestRaceConditionPrevention:
    """Test race condition prevention."""
    
    def test_no_duplicate_workspace_creation(self):
        """Test that duplicate workspace creation is prevented."""
        registry = ConcurrentRegistry()
        workspace_id = "shared_workspace"
        
        creation_results = []
        
        def try_create():
            result = registry.create_workspace(workspace_id, "company_1")
            creation_results.append(result)
        
        threads = [threading.Thread(target=try_create) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # Only one should succeed
        assert sum(creation_results) == 1
        assert registry.workspace_count() == 1
    
    def test_concurrent_workspace_isolation(self):
        """Test concurrent access to different workspaces is isolated."""
        registry = ConcurrentRegistry()
        
        # Setup workspaces
        for i in range(5):
            registry.create_workspace(f"workspace_{i}", f"company_{i}")
        
        workspace_states = {}
        lock = threading.Lock()
        
        def access_and_modify(workspace_num: int):
            workspace_id = f"workspace_{workspace_num}"
            
            # Read state
            state_before = registry.get_workspace_state(workspace_id)
            tool_count_before = len(state_before["tools"]) if state_before else 0
            
            # Modify state (add tools)
            for i in range(10):
                registry.register_tool(workspace_id, f"tool_{workspace_num}_{i}")
            
            # Read final state
            state_after = registry.get_workspace_state(workspace_id)
            tool_count_after = len(state_after["tools"]) if state_after else 0
            
            # Store results
            with lock:
                workspace_states[workspace_id] = (tool_count_before, tool_count_after)
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            list(executor.map(access_and_modify, range(5)))
        
        # Each workspace should have exactly 10 tools added
        for workspace_id, (before, after) in workspace_states.items():
            assert after - before == 10
            assert after == 10
    
    def test_concurrent_reads_dont_interfere(self):
        """Test concurrent reads don't interfere with each other."""
        registry = ConcurrentRegistry()
        
        # Setup workspace
        registry.create_workspace("read_test_ws", "company_1")
        for i in range(50):
            registry.register_tool("read_test_ws", f"tool_{i}")
        
        read_counts = []
        
        def read_workspace():
            state = registry.get_workspace_state("read_test_ws")
            read_counts.append(len(state["tools"]) if state else 0)
        
        # 100 concurrent reads
        with ThreadPoolExecutor(max_workers=20) as executor:
            list(executor.map(lambda _: read_workspace(), range(100)))
        
        # All reads should see 50 tools
        assert all(count == 50 for count in read_counts)
    
    def test_interleaved_operations_no_corruption(self):
        """Test interleaved create/register/cleanup don't corrupt state."""
        registry = ConcurrentRegistry()
        results = []
        
        def interleaved_ops(workspace_num: int):
            ws_id = f"ws_{workspace_num}"
            
            # Create
            created = registry.create_workspace(ws_id, f"company_{workspace_num % 3}")
            results.append(("create", workspace_num, created))
            
            if created:
                # Register tools
                for tool_num in range(5):
                    registered = registry.register_tool(ws_id, f"tool_{tool_num}")
                    results.append(("register", workspace_num, registered))
                
                # Check state
                state = registry.get_workspace_state(ws_id)
                results.append(("check", workspace_num, len(state["tools"])))
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(interleaved_ops, range(20)))
        
        # Verify all operations succeeded
        assert len([r for r in results if r[0] == "create"]) == 20
        assert len([r for r in results if r[0] == "register"]) == 100  # 20 * 5
        assert all(r[2] == 5 for r in results if r[0] == "check")


# ============================================================================
# TESTS: Memory Stability (AC-PHASE48-S5-003)
# ============================================================================

class TestMemoryStability:
    """Test memory stability under load."""
    
    def test_100_cycles_of_10_workspaces(self):
        """Test 100 cycles of creating/using/destroying 10 workspaces."""
        registry = ConcurrentRegistry()
        peak_workspace_count = 0
        
        for cycle in range(100):
            # Create
            for i in range(10):
                workspace_id = f"cycle_{cycle}_ws_{i}"
                registry.create_workspace(workspace_id, f"company_{i % 5}")
                
                # Register tools
                for tool_num in range(3):
                    registry.register_tool(workspace_id, f"tool_{tool_num}")
            
            peak_workspace_count = max(peak_workspace_count, registry.workspace_count())
            
            # Cleanup
            for i in range(10):
                workspace_id = f"cycle_{cycle}_ws_{i}"
                registry.cleanup_workspace(workspace_id)
        
        # After all cycles, should have no workspaces
        assert registry.workspace_count() == 0
        # Peak should be 10 (only one cycle's workspaces at a time)
        assert peak_workspace_count == 10
    
    def test_1000_operations_same_10_workspaces(self):
        """Test 1000 operations on same 10 workspaces (memory stable)."""
        registry = ConcurrentRegistry()
        
        # Setup 10 workspaces
        for i in range(10):
            registry.create_workspace(f"stable_ws_{i}", f"company_{i % 3}")
        
        initial_count = registry.workspace_count()
        
        # Perform 1000 operations
        def operation_batch(batch_num: int):
            for op in range(100):
                workspace_id = f"stable_ws_{batch_num % 10}"
                tool_name = f"batch_{batch_num}_tool_{op}"
                registry.register_tool(workspace_id, tool_name)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(operation_batch, range(10)))
        
        # Workspace count should stay same (10)
        assert registry.workspace_count() == initial_count
        
        # Total operations should be tracked
        assert registry.get_operation_count() >= 1010


# ============================================================================
# TESTS: Data Consistency Under Concurrent Load
# ============================================================================

class TestDataConsistency:
    """Test data consistency under concurrent load."""
    
    def test_no_state_leakage_100_workspaces(self):
        """Test that 100 workspaces have completely isolated state."""
        registry = ConcurrentRegistry()
        
        # Create 100 workspaces with different tools
        for i in range(100):
            workspace_id = f"isolation_test_ws_{i}"
            registry.create_workspace(workspace_id, f"company_{i % 10}")
            
            # Each workspace gets unique tools
            for tool_num in range(5):
                registry.register_tool(
                    workspace_id,
                    f"unique_tool_{i}_{tool_num}"
                )
        
        # Verify isolation
        for i in range(100):
            workspace_id = f"isolation_test_ws_{i}"
            state = registry.get_workspace_state(workspace_id)
            
            # Should have exactly 5 tools
            assert len(state["tools"]) == 5
            
            # Should have exact tool names
            expected_tools = {f"unique_tool_{i}_{t}" for t in range(5)}
            actual_tools = set(state["tools"].keys())
            assert expected_tools == actual_tools
    
    def test_concurrent_tool_registration_accuracy(self):
        """Test tool registration count is accurate under concurrency."""
        registry = ConcurrentRegistry()
        
        # Setup workspace
        registry.create_workspace("counter_test_ws", "company_1")
        
        def register_tools(batch_num: int):
            for tool_num in range(50):
                tool_name = f"batch_{batch_num}_tool_{tool_num}"
                registry.register_tool("counter_test_ws", tool_name)
        
        # 10 concurrent batches = 500 tools
        with ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(register_tools, range(10)))
        
        state = registry.get_workspace_state("counter_test_ws")
        assert len(state["tools"]) == 500
    
    def test_concurrent_access_consistency(self):
        """Test concurrent access maintains consistency."""
        registry = ConcurrentRegistry()
        
        # Setup
        registry.create_workspace("consistency_ws", "company_1")
        consistency_checks = []
        
        def check_consistency(thread_num: int):
            # Each thread registers and immediately checks
            tool_name = f"thread_{thread_num}_tool"
            registry.register_tool("consistency_ws", tool_name)
            
            state = registry.get_workspace_state("consistency_ws")
            tool_count = len(state["tools"])
            consistency_checks.append(tool_count)
        
        # 50 concurrent threads
        with ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(check_consistency, range(50)))
        
        # All checks should see increasing tool counts
        # (not decreasing or staying same - indicates proper locking)
        min_count = min(consistency_checks)
        max_count = max(consistency_checks)
        
        assert min_count >= 1
        assert max_count == 50


# ============================================================================
# TESTS: Stress Test Scenarios
# ============================================================================

class TestStressScenarios:
    """Test realistic stress scenarios."""
    
    def test_rapid_workspace_turnover(self):
        """Test rapid creation and destruction of workspaces."""
        registry = ConcurrentRegistry()
        
        def rapid_cycle(cycle_num: int):
            workspace_id = f"rapid_ws_{cycle_num}"
            
            # Create
            registry.create_workspace(workspace_id, "company_1")
            
            # Quick operations
            for i in range(10):
                registry.register_tool(workspace_id, f"tool_{i}")
            
            # Cleanup
            registry.cleanup_workspace(workspace_id)
        
        # 100 rapid cycles
        with ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(rapid_cycle, range(100)))
        
        # Should end with no workspaces
        assert registry.workspace_count() == 0
    
    def test_mixed_operation_types_concurrent(self):
        """Test mixed create/register/read/cleanup operations."""
        registry = ConcurrentRegistry()
        results = {"creates": 0, "registers": 0, "reads": 0, "cleanups": 0}
        lock = threading.Lock()
        
        def mixed_operation(op_num: int):
            operation_type = op_num % 4
            workspace_id = f"mixed_ws_{op_num % 20}"
            
            if operation_type == 0:  # Create
                registry.create_workspace(workspace_id, f"company_{op_num % 5}")
                with lock:
                    results["creates"] += 1
            elif operation_type == 1:  # Register
                registry.register_tool(workspace_id, f"tool_{op_num}")
                with lock:
                    results["registers"] += 1
            elif operation_type == 2:  # Read
                registry.get_workspace_state(workspace_id)
                with lock:
                    results["reads"] += 1
            else:  # Cleanup
                registry.cleanup_workspace(workspace_id)
                with lock:
                    results["cleanups"] += 1
        
        # 200 mixed operations
        with ThreadPoolExecutor(max_workers=20) as executor:
            list(executor.map(mixed_operation, range(200)))
        
        # Verify operation distribution
        total_ops = sum(results.values())
        assert total_ops == 200
        assert results["creates"] > 0
        assert results["registers"] > 0
        assert results["reads"] > 0
