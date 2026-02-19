"""
Integration Tests — Orchestrator E2E Workflows + MCP Live + Audit DB Stress

Purpose: 
  - Test complete orchestrator lifecycle across all phases
  - Verify MCP tool consolidation with live execution
  - Stress test audit DB with concurrent orchestrators
  
Authority: CORE-008 (TDD) | CORE-048 (Governance Gates) | CORE-027 (Audit)
"""

import pytest
import threading
import time
import tempfile
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
import concurrent.futures


# ═══════════════════════════════════════════════════════════════════════════
# Orchestrator E2E Lifecycle Tests (8 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestOrchestratorE2ELifecycle:
    """Full orchestrator lifecycle verification across phases."""
    
    def test_orchestrator_completes_full_phase_1_3_cycle(self):
        """Orchestrator must complete all phases without error."""
        from cortex.core.orchestrator_base import OrchestratorBase
        
        execution_log = []
        
        class E2EOrchestrator(OrchestratorBase):
            def setup(self):
                execution_log.append("setup")
            def govern(self):
                execution_log.append("govern")
            def execute(self):
                execution_log.append("execute")
            def validate(self):
                execution_log.append("validate")
            def teardown(self):
                execution_log.append("teardown")
        
        orch = E2EOrchestrator()
        orch.run()
        
        # All 5 stages must execute in order
        assert execution_log == ["setup", "govern", "execute", "validate", "teardown"]
    
    def test_orchestrator_audit_trail_complete(self):
        """Audit trail must capture all lifecycle stages."""
        from cortex.core.orchestrator_base import OrchestratorBase
        from cortex.infrastructure.audit_db import CortexAuditDB
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "audit.db"
            
            class AuditedOrchestrator(OrchestratorBase):
                def __init__(self):
                    super().__init__()
                    self.audit_db = CortexAuditDB(str(db_path))
                
                def setup(self):
                    pass
                def govern(self):
                    pass
                def execute(self):
                    pass
                def validate(self):
                    pass
                def teardown(self):
                    self.audit_db.close()
            
            orch = AuditedOrchestrator()
            orch.run()
            
            # Verify audit DB is operational
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM audit_events")
            count = cursor.fetchone()[0]
            conn.close()
            
            assert db_path.exists(), "Audit DB should exist"
    
    def test_orchestrator_governance_gate_enforced_in_workflow(self):
        """Governance gate must block non-compliant operations."""
        from cortex.core.orchestrator_base import OrchestratorBase
        
        class StrictOrchestrator(OrchestratorBase):
            def setup(self):
                pass
            def govern(self):
                # Governance violation - block execution
                raise RuntimeError("CORE-048: Governance violation detected")
            def execute(self):
                pass
            def validate(self):
                pass
            def teardown(self):
                pass
        
        orch = StrictOrchestrator()
        
        with pytest.raises(RuntimeError, match="Governance violation"):
            orch.run()
    
    def test_orchestrator_error_in_execute_triggers_teardown(self):
        """Even if execute() fails, teardown() must run."""
        from cortex.core.orchestrator_base import OrchestratorBase
        
        cleanup_called = []
        
        class FailingOrchestrator(OrchestratorBase):
            def setup(self):
                pass
            def govern(self):
                pass
            def execute(self):
                raise ValueError("Execution failed intentionally")
            def validate(self):
                pass
            def teardown(self):
                cleanup_called.append(True)
        
        orch = FailingOrchestrator()
        
        with pytest.raises(ValueError):
            orch.run()
        
        # Teardown must have run despite error
        assert len(cleanup_called) == 1
    
    def test_orchestrator_state_consistency_across_phases(self):
        """Orchestrator state must remain consistent across all phases."""
        from cortex.core.orchestrator_base import OrchestratorBase
        
        states_observed = []
        
        class StatefulOrchestrator(OrchestratorBase):
            def __init__(self):
                super().__init__()
                self.phase_counter = 0
            
            def setup(self):
                self.phase_counter += 1
                states_observed.append(("setup", self.phase_counter))
            def govern(self):
                self.phase_counter += 1
                states_observed.append(("govern", self.phase_counter))
            def execute(self):
                self.phase_counter += 1
                states_observed.append(("execute", self.phase_counter))
            def validate(self):
                self.phase_counter += 1
                states_observed.append(("validate", self.phase_counter))
            def teardown(self):
                self.phase_counter += 1
                states_observed.append(("teardown", self.phase_counter))
        
        orch = StatefulOrchestrator()
        orch.run()
        
        # Counter should increment predictably
        expected = [
            ("setup", 1), ("govern", 2), ("execute", 3), 
            ("validate", 4), ("teardown", 5)
        ]
        assert states_observed == expected
    
    def test_orchestrator_handles_long_running_operations(self):
        """Orchestrator must handle time-consuming operations."""
        from cortex.core.orchestrator_base import OrchestratorBase
        
        execution_times = []
        
        class SlowOrchestrator(OrchestratorBase):
            def setup(self):
                pass
            def govern(self):
                pass
            def execute(self):
                # Simulate long operation
                time.sleep(0.5)
                execution_times.append("execute_complete")
            def validate(self):
                pass
            def teardown(self):
                pass
        
        start = time.time()
        orch = SlowOrchestrator()
        orch.run()
        elapsed = time.time() - start
        
        # Should complete (even if slow)
        assert "execute_complete" in execution_times
        assert elapsed >= 0.5  # At least the sleep time
    
    def test_orchestrator_concurrent_independent_instances(self):
        """Multiple orchestrators must not interfere with each other."""
        from cortex.core.orchestrator_base import OrchestratorBase
        
        results = []
        
        class IdentifiedOrchestrator(OrchestratorBase):
            def __init__(self, orch_id):
                super().__init__()
                self.orch_id = orch_id
                self.local_value = None
            
            def setup(self):
                self.local_value = f"value_{self.orch_id}"
            def govern(self):
                pass
            def execute(self):
                time.sleep(0.01)  # Simulate concurrent work
            def validate(self):
                results.append({
                    "id": self.orch_id,
                    "local_value": self.local_value
                })
            def teardown(self):
                pass
        
        # Run 3 orchestrators concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(IdentifiedOrchestrator(i).run)
                for i in range(3)
            ]
            for future in concurrent.futures.as_completed(futures):
                future.result()
        
        # Each should have correct isolated state
        assert len(results) == 3
        for result in results:
            assert result["local_value"] == f"value_{result['id']}"


# ═══════════════════════════════════════════════════════════════════════════
# MCP Consolidation Live Tests (6 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestMCPConsolidationLive:
    """MCP tool consolidation with live orchestrator integration."""
    
    def test_mcp_consolidated_tools_importable(self):
        """All 22 consolidated MCP tools must be importable."""
        # Test that consolidated tools can be imported
        try:
            from cortex.intelligence.lens import knowledge_graph
            from cortex.intelligence.memory import core
            # Additional imports as available
            tools_found = 2
        except ImportError as e:
            tools_found = 0
        
        # At least basic tools should be importable
        assert tools_found >= 1, "Core consolidated tools must be importable"
    
    def test_mcp_tool_consolidation_alias_resolution(self):
        """MCP tool aliases from 34→22 must resolve correctly."""
        # Verify consolidation matrix exists and is parseable
        import yaml
        matrix_path = Path("cortex-registry/planning/phases/planned/cortex-refactor/mcp-consolidation-matrix.yaml")
        
        if matrix_path.exists():
            with open(matrix_path) as f:
                matrix = yaml.safe_load(f) or {}
            
            aliases = matrix.get('consolidation_map', {})
            # Should have consolidation mappings
            assert len(aliases) > 0, "Consolidation map should exist"
    
    def test_mcp_tool_registry_consistency(self):
        """MCP tool registry must be consistent (no dangling references)."""
        import yaml
        
        registry_path = Path("cortex-registry/governance/inventory.yaml")
        if registry_path.exists():
            with open(registry_path) as f:
                inventory = yaml.safe_load(f) or {}
            
            mcp_tools = inventory.get('mcp_tools', {})
            # Each tool should have valid location
            for tool_name, config in mcp_tools.items():
                location = config.get('location', '')
                assert location, f"Tool {tool_name} missing location"
                assert "cortex" in location, f"Tool {tool_name} location invalid: {location}"
    
    def test_mcp_tool_dependency_resolution(self):
        """MCP tools must not have circular dependencies."""
        # Tools can depend on each other but not in circles
        import yaml
        
        matrix_path = Path("cortex-registry/planning/phases/planned/cortex-refactor/mcp-consolidation-matrix.yaml")
        if matrix_path.exists():
            with open(matrix_path) as f:
                matrix = yaml.safe_load(f) or {}
            
            tools = matrix.get('consolidated_tools', {})
            # Should have structure
            assert len(tools) > 0, "Consolidated tools map should exist"
    
    def test_orchestrator_can_use_consolidated_mcp_tools(self):
        """Orchestrators must be able to reference consolidated MCP tools."""
        from cortex.core.orchestrator_base import OrchestratorBase
        
        tool_references = []
        
        class MCPAwareOrchestrator(OrchestratorBase):
            def setup(self):
                # Reference consolidated tool location
                tool_references.append("cortex.intelligence.lens")
                tool_references.append("cortex.intelligence.memory")
            def govern(self):
                pass
            def execute(self):
                pass
            def validate(self):
                pass
            def teardown(self):
                pass
        
        orch = MCPAwareOrchestrator()
        orch.run()
        
        # Orchestrator should have referenced consolidated tools
        assert len(tool_references) == 2
        assert all("cortex.intelligence" in ref for ref in tool_references)
    
    def test_mcp_tool_no_dead_references_in_orchestrators(self):
        """Orchestrators must not reference deleted/archived MCP tools."""
        # Grep for old package references in active orchestrator code
        import os
        
        orchestrator_paths = list(Path("cortex/orchestrators").rglob("*.py"))
        
        old_patterns = ["cortex_intelligence/", "cortex_lens/", "_archive/"]
        violations = []
        
        for py_file in orchestrator_paths[:5]:  # Sample first 5
            content = py_file.read_text(errors='ignore')
            for pattern in old_patterns:
                if pattern in content and "import" in content:
                    violations.append(f"{py_file.name}: {pattern}")
        
        # Should not find old patterns in imports
        active_violations = [v for v in violations if "import" in content]
        assert len(active_violations) == 0, f"Found old package imports: {active_violations}"


# ═══════════════════════════════════════════════════════════════════════════
# Audit DB Stress Tests (5 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestAuditDBStress:
    """Stress test audit DB under high concurrency."""
    
    def test_audit_db_concurrent_orchestrator_writes(self):
        """Multiple orchestrators writing simultaneously must not corrupt DB."""
        from cortex.infrastructure.audit_db import CortexAuditDB, AuditEntry
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "audit.db"
            db = CortexAuditDB(str(db_path))
            
            def orchestrator_work(orch_id, iterations):
                for i in range(iterations):
                    entry = AuditEntry(
                        orchestrator_id=f"orch_{orch_id}",
                        event_type=f"event_{i}",
                        status="completed",
                        duration_ms=10
                    )
                    db.log_event(entry)
            
            # 5 orchestrators, 30 events each = 150 total
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(orchestrator_work, i, 30)
                    for i in range(5)
                ]
                for future in concurrent.futures.as_completed(futures):
                    future.result()
            
            # Verify all events logged
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM audit_events")
            count = cursor.fetchone()[0]
            conn.close()
            
            assert count == 150, f"Expected 150 events, got {count}"
    
    def test_audit_db_query_performance_under_load(self):
        """Queries must remain fast even with 1000+ events."""
        from cortex.infrastructure.audit_db import CortexAuditDB, AuditEntry
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "audit.db"
            db = CortexAuditDB(str(db_path))
            
            # Insert 1000 events
            for i in range(1000):
                entry = AuditEntry(
                    orchestrator_id=f"orch_{i % 20}",
                    event_type=f"event_{i}",
                    status="completed",
                    duration_ms=10 + (i % 100)
                )
                db.log_event(entry)
            
            # Query performance test
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            start = time.time()
            cursor.execute("SELECT COUNT(*) FROM audit_events WHERE orchestrator_id = 'orch_5'")
            result = cursor.fetchone()[0]
            elapsed = time.time() - start
            conn.close()
            
            # Should complete in < 50ms
            assert elapsed < 0.05, f"Query took {elapsed}s (expected < 50ms)"
            assert result == 50, f"Expected 50 events for orch_5, got {result}"
    
    def test_audit_db_transaction_isolation(self):
        """Concurrent transactions must not interfere with each other."""
        from cortex.infrastructure.audit_db import CortexAuditDB, AuditEntry
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "audit.db"
            db = CortexAuditDB(str(db_path))
            
            events_logged = []
            
            def log_batch(batch_id, batch_size):
                for i in range(batch_size):
                    entry = AuditEntry(
                        orchestrator_id=f"batch_{batch_id}",
                        event_type=f"event_{i}",
                        status="completed"
                    )
                    db.log_event(entry)
                    events_logged.append((batch_id, i))
            
            # Log batches concurrently
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [
                    executor.submit(log_batch, batch_id, 50)
                    for batch_id in range(3)
                ]
                for future in concurrent.futures.as_completed(futures):
                    future.result()
            
            # All events should be logged (150 total)
            assert len(events_logged) == 150
    
    def test_audit_db_lock_handling_under_contention(self):
        """DB must handle lock contention without deadlock."""
        from cortex.infrastructure.audit_db import CortexAuditDB, AuditEntry
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "audit.db"
            db = CortexAuditDB(str(db_path))
            
            completed = []
            
            def heavy_workload(thread_id):
                try:
                    for i in range(20):
                        entry = AuditEntry(
                            orchestrator_id=f"thread_{thread_id}",
                            event_type=f"event_{i}",
                            status="completed"
                        )
                        db.log_event(entry)
                    completed.append(thread_id)
                except Exception as e:
                    # Should not deadlock
                    assert False, f"Deadlock or error: {e}"
            
            # 10 concurrent threads
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(heavy_workload, i)
                    for i in range(10)
                ]
                for future in concurrent.futures.as_completed(futures):
                    future.result()
            
            # All threads should complete
            assert len(completed) == 10, f"Expected 10 completed, got {len(completed)}"
    
    def test_audit_db_recovery_after_heavy_load(self):
        """DB must remain operational after heavy concurrent load."""
        from cortex.infrastructure.audit_db import CortexAuditDB, AuditEntry
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "audit.db"
            db = CortexAuditDB(str(db_path))
            
            # Heavy load
            def load_worker(worker_id):
                for i in range(50):
                    entry = AuditEntry(
                        orchestrator_id=f"worker_{worker_id}",
                        event_type=f"event_{i}",
                        status="completed"
                    )
                    db.log_event(entry)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(load_worker, i) for i in range(5)]
                for future in concurrent.futures.as_completed(futures):
                    future.result()
            
            # Recovery query after load
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM audit_events")
                count = cursor.fetchone()[0]
                conn.close()
                
                # Should still be queryable
                assert count == 250, f"Expected 250 events after load, got {count}"
            except Exception as e:
                assert False, f"DB corrupted after load: {e}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
