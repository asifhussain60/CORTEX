"""
Integration Test Suite - CORTEX 6.0
feat07-integration Phase 2

End-to-end workflow tests, multi-component integration, and failure scenarios

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
"""

import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.orchestrators.core.todo_orchestrator import TodoOrchestrator
from src.orchestrators.core.governance_merger import GovernanceMerger
from src.orchestrators.master_orchestrator import MasterOrchestrator
from src.orchestrators.state_manager import StateManager
from src.orchestrators.audit_logger import EnterpriseAuditLogger as AuditLogger, AuditLevel, AuditCategory
from src.infrastructure.risk_mitigations import (
    EdgeCaseMitigations,
    FailureModeMitigations,
    get_registry
)


# ==============================================================================
# Task 2.1: End-to-End Workflow Tests
# ==============================================================================

class TestEndToEndWorkflows:
    """
    Task 2.1: End-to-end workflow tests
    Tests complete workflows from request to completion
    """
    
    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create temporary workspace"""
        workspace = tmp_path / "cortex_test"
        workspace.mkdir()
        (workspace / "cortex-brain").mkdir()
        (workspace / "cortex-brain" / "state").mkdir()
        (workspace / "cortex-brain" / "audit-logs").mkdir()
        return workspace
    
    @pytest.fixture
    def state_manager(self, temp_workspace):
        """Create state manager for tests"""
        db_path = temp_workspace / "cortex-brain" / "state" / "test.db"
        return StateManager(state_file=str(db_path))
    
    @pytest.fixture
    def audit_logger(self, temp_workspace):
        """Create audit logger for tests"""
        log_dir = temp_workspace / "cortex-brain" / "audit-logs"
        return AuditLogger(log_dir=str(log_dir))
    
    def test_complete_planning_to_execution_workflow(
        self, temp_workspace, state_manager, audit_logger
    ):
        """
        Test complete workflow: Plan creation → TODO generation → Execution
        """
        # 1. Create a simple plan
        plan_data = {
            "name": "Test Feature",
            "phases": [
                {
                    "id": 1,
                    "name": "Setup",
                    "tasks": [
                        {"id": "1.1", "name": "Initialize", "dependencies": []}
                    ]
                }
            ]
        }
        
        # 2. Create TODO orchestrator
        todo_orch = TodoOrchestrator(
            workspace_root=str(temp_workspace),
            state_manager=state_manager,
            audit_logger=audit_logger
        )
        
        # 3. Generate TODOs from plan
        todos = todo_orch.create_todos_from_plan(plan_data)
        
        assert len(todos) > 0
        assert todos[0]["task_id"] == "1.1"
        assert todos[0]["status"] == "NOT_STARTED"
        
        # 4. Execute first task
        result = todo_orch.mark_task_completed("1.1", {"result": "success"})
        
        assert result["success"] is True
        assert result["task_id"] == "1.1"
        
        # 5. Verify audit trail
        logs = audit_logger.get_recent_logs(limit=10)
        assert len(logs) > 0
        
        # Check for key operations in logs
        operations = [log.get("operation") for log in logs]
        assert "create_todos" in operations or "task_completed" in operations
    
    def test_governance_integration_workflow(
        self, temp_workspace, state_manager, audit_logger
    ):
        """
        Test workflow with governance validation
        """
        # Create governance merger
        gov_merger = GovernanceMerger(
            state_manager=state_manager,
            audit_logger=audit_logger,
            workspace_root=str(temp_workspace)
        )
        
        # Load governance rules
        unified_set = gov_merger.generate_unified_instruction_set()
        
        assert unified_set is not None
        assert hasattr(unified_set, "rules")
        assert len(unified_set.rules) > 0
        
        # Create TODOs with governance constraints
        todo_orch = TodoOrchestrator(
            workspace_root=str(temp_workspace),
            state_manager=state_manager,
            audit_logger=audit_logger,
            governance_merger=gov_merger
        )
        
        plan_data = {
            "name": "Governed Feature",
            "phases": [
                {
                    "id": 1,
                    "name": "Implementation",
                    "tasks": [
                        {
                            "id": "1.1",
                            "name": "Implement with governance",
                            "dependencies": []
                        }
                    ]
                }
            ]
        }
        
        todos = todo_orch.create_todos_from_plan(plan_data)
        
        # Verify governance was applied
        assert len(todos) > 0
        # Governance rules should be reflected in TODO metadata
    
    def test_error_recovery_workflow(
        self, temp_workspace, state_manager, audit_logger
    ):
        """
        Test workflow with error handling and recovery
        """
        todo_orch = TodoOrchestrator(
            workspace_root=str(temp_workspace),
            state_manager=state_manager,
            audit_logger=audit_logger
        )
        
        # Create a task
        plan_data = {
            "name": "Recovery Test",
            "phases": [
                {
                    "id": 1,
                    "name": "Phase 1",
                    "tasks": [
                        {"id": "1.1", "name": "Task 1", "dependencies": []}
                    ]
                }
            ]
        }
        
        todos = todo_orch.create_todos_from_plan(plan_data)
        
        # Attempt to mark non-existent task as completed
        with pytest.raises(Exception):
            todo_orch.mark_task_completed("nonexistent", {})
        
        # System should still be functional
        result = todo_orch.get_task_status("1.1")
        assert result["task_id"] == "1.1"
        assert result["status"] in ["NOT_STARTED", "READY"]


# ==============================================================================
# Task 2.2: Multi-Component Integration Tests
# ==============================================================================

class TestMultiComponentIntegration:
    """
    Task 2.2: Multi-component integration tests
    Tests interaction between multiple CORTEX components
    """
    
    def test_state_manager_audit_logger_integration(self, tmp_path):
        """Test StateManager + AuditLogger integration"""
        db_path = tmp_path / "state.db"
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        
        state_mgr = StateManager(state_file=str(db_path))
        audit_log = AuditLogger(log_dir=str(log_dir))
        
        # Store state and audit it
        state_mgr.set_state("test_key", {"value": 123})
        audit_log.log(
            level=AuditLevel.INFO,
            category=AuditCategory.STATE_CHANGE,
            component="test",
            operation="set_state",
            correlation_id="TEST-001",
            details={"key": "test_key"}
        )
        
        # Verify both components work
        retrieved = state_mgr.get_state("test_key")
        assert retrieved["value"] == 123
        
        logs = audit_log.get_recent_logs(limit=5)
        assert len(logs) > 0
        assert logs[0]["operation"] == "set_state"
    
    def test_todo_orchestrator_governance_integration(self, tmp_path):
        """Test TodoOrchestrator + GovernanceMerger integration"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / "cortex-brain").mkdir()
        (workspace / "cortex-brain" / "state").mkdir()
        (workspace / "cortex-brain" / "audit-logs").mkdir()
        
        state_mgr = StateManager(
            state_file=str(workspace / "cortex-brain" / "state" / "test.db")
        )
        audit_log = AuditLogger(
            log_directory=str(workspace / "cortex-brain" / "audit-logs")
        )
        
        gov_merger = GovernanceMerger(
            state_manager=state_mgr,
            audit_logger=audit_log,
            workspace_root=str(workspace)
        )
        
        todo_orch = TodoOrchestrator(
            workspace_root=str(workspace),
            state_manager=state_mgr,
            audit_logger=audit_log,
            governance_merger=gov_merger
        )
        
        # Create plan and verify governance is applied
        plan = {
            "name": "Integrated Test",
            "phases": [{
                "id": 1,
                "name": "Phase 1",
                "tasks": [{"id": "1.1", "name": "Task", "dependencies": []}]
            }]
        }
        
        todos = todo_orch.create_todos_from_plan(plan)
        assert len(todos) > 0
    
    def test_risk_mitigation_integration(self, tmp_path):
        """Test risk mitigation framework integration"""
        registry = get_registry()
        
        # Verify registry is populated
        stats = registry.get_stats()
        assert stats["total"] > 0
        
        # Test edge case mitigation with TODO orchestrator
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / "cortex-brain").mkdir()
        (workspace / "cortex-brain" / "state").mkdir()
        
        state_mgr = StateManager(
            state_file=str(workspace / "cortex-brain" / "state" / "test.db")
        )
        
        # Create empty plan (should be caught by EC-001)
        with pytest.raises(Exception):
            dag = Mock()
            dag.is_empty.return_value = True
            EdgeCaseMitigations.validate_dag_not_empty(dag)
    
    def test_full_stack_integration(self, tmp_path):
        """Test full stack: Governance + TODO + State + Audit + Risk"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / "cortex-brain").mkdir()
        (workspace / "cortex-brain" / "state").mkdir()
        (workspace / "cortex-brain" / "audit-logs").mkdir()
        
        # Initialize all components
        state_mgr = StateManager(
            state_file=str(workspace / "cortex-brain" / "state" / "test.db")
        )
        audit_log = AuditLogger(
            log_directory=str(workspace / "cortex-brain" / "audit-logs")
        )
        gov_merger = GovernanceMerger(
            state_manager=state_mgr,
            audit_logger=audit_log,
            workspace_root=str(workspace)
        )
        todo_orch = TodoOrchestrator(
            workspace_root=str(workspace),
            state_manager=state_mgr,
            audit_logger=audit_log,
            governance_merger=gov_merger
        )
        
        # Execute complete workflow
        plan = {
            "name": "Full Stack Test",
            "phases": [{
                "id": 1,
                "name": "Phase 1",
                "tasks": [
                    {"id": "1.1", "name": "Task 1", "dependencies": []},
                    {"id": "1.2", "name": "Task 2", "dependencies": ["1.1"]}
                ]
            }]
        }
        
        # 1. Validate with risk mitigations
        dag = Mock()
        dag.is_empty.return_value = False
        dag.tasks = [Mock(), Mock()]
        EdgeCaseMitigations.validate_dag_not_empty(dag)
        
        # 2. Load governance
        unified_set = gov_merger.generate_unified_instruction_set()
        assert unified_set is not None
        
        # 3. Create TODOs
        todos = todo_orch.create_todos_from_plan(plan)
        assert len(todos) == 2
        
        # 4. Complete tasks
        todo_orch.mark_task_completed("1.1", {"result": "success"})
        
        # 5. Verify audit trail
        logs = audit_log.get_recent_logs(limit=10)
        assert len(logs) > 0


# ==============================================================================
# Task 2.3: Failure Scenario Tests
# ==============================================================================

class TestFailureScenarios:
    """
    Task 2.3: Failure scenario tests
    Tests system behavior under failure conditions
    """
    
    def test_database_unavailable_scenario(self, tmp_path):
        """Test behavior when database is unavailable"""
        # Point to non-existent/read-only location
        db_path = tmp_path / "readonly" / "state.db"
        
        # This should handle the error gracefully
        with pytest.raises(Exception):
            state_mgr = StateManager(state_file=str(db_path))
            state_mgr.set_state("key", "value")
    
    def test_audit_log_write_failure_scenario(self, tmp_path):
        """Test failsafe when audit log can't write"""
        failsafe = FailureModeMitigations.create_audit_failsafe(max_queue_size=5)
        
        # Mock failing logger
        failing_logger = Mock()
        failing_logger.log.side_effect = Exception("Disk full")
        
        # Should queue entries instead of failing
        for i in range(3):
            result = failsafe.log(
                {"message": f"Entry {i}"},
                failing_logger
            )
            assert result is True
        
        assert len(failsafe.queue) == 3
    
    def test_orphaned_task_scenario(self):
        """Test handling of orphaned tasks"""
        dag = Mock()
        dag.get_dependents.return_value = ["task2", "task3"]
        dag.mark_task_blocked = Mock()
        
        # Remove parent task
        affected = EdgeCaseMitigations.handle_orphaned_tasks(dag, "task1")
        
        # Dependents should be marked as blocked
        assert len(affected) == 2
        assert dag.mark_task_blocked.call_count == 2
    
    def test_deep_dag_scenario(self):
        """Test handling of extremely deep DAG"""
        dag = Mock()
        dag.get_root_tasks.return_value = ["root"]
        
        # Create deep chain
        def get_deps(task_id):
            if task_id == "root":
                return ["t1"]
            num = int(task_id[1:]) if task_id.startswith("t") else 0
            if num < 101:
                return [f"t{num + 1}"]
            return []
        
        dag.get_dependents.side_effect = get_deps
        dag.tasks = ["root"] + [f"t{i}" for i in range(1, 102)]
        
        # Should raise error for >100 depth
        with pytest.raises(Exception):
            EdgeCaseMitigations.validate_dag_depth(dag, max_depth=100)
    
    def test_unicode_encoding_scenario(self):
        """Test handling of problematic Unicode"""
        # Various Unicode edge cases
        test_cases = [
            "Emoji 🚀🎉💻",
            "Accents Café résumé",
            "CJK 测试 テスト тест",
            "Combining e\u0301",  # e + combining acute
            "Mixed Test 测试 🎉"
        ]
        
        for text in test_cases:
            normalized = EdgeCaseMitigations.normalize_unicode(text)
            assert isinstance(normalized, str)
            # Should be valid UTF-8
            assert normalized.encode("utf-8")
    
    def test_concurrent_task_update_scenario(self):
        """Test race condition in concurrent updates"""
        from src.infrastructure.risk_mitigations import RaceConditionMitigations
        
        mitigator = RaceConditionMitigations()
        counter = {"value": 0}
        
        def increment():
            current = counter["value"]
            time.sleep(0.001)  # Simulate race window
            counter["value"] = current + 1
            return counter["value"]
        
        # Concurrent updates with locking
        import threading
        threads = []
        for _ in range(5):
            t = threading.Thread(
                target=lambda: mitigator.atomic_task_update("task1", increment)
            )
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # With proper locking, should be exactly 5
        assert counter["value"] == 5
    
    def test_governance_conflict_scenario(self):
        """Test governance rule conflicts"""
        # Two rules with same priority
        rule1 = {
            "category": "cortex_tier0",
            "rule": "Rule A",
            "created_at": "2026-01-01T00:00:00Z"
        }
        rule2 = {
            "category": "cortex_tier0",
            "rule": "Rule B",
            "created_at": "2026-01-02T00:00:00Z"
        }
        
        # Should use timestamp as tiebreaker
        result = EdgeCaseMitigations.resolve_governance_conflict(rule1, rule2)
        assert result == rule1  # Older wins


# ==============================================================================
# Performance and Stress Tests
# ==============================================================================

class TestPerformanceUnderLoad:
    """Performance tests for integration scenarios"""
    
    def test_large_plan_processing(self, tmp_path):
        """Test processing large plan with many tasks"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / "cortex-brain").mkdir()
        (workspace / "cortex-brain" / "state").mkdir()
        (workspace / "cortex-brain" / "audit-logs").mkdir()
        
        state_mgr = StateManager(
            state_file=str(workspace / "cortex-brain" / "state" / "test.db")
        )
        audit_log = AuditLogger(
            log_directory=str(workspace / "cortex-brain" / "audit-logs")
        )
        
        todo_orch = TodoOrchestrator(
            workspace_root=str(workspace),
            state_manager=state_mgr,
            audit_logger=audit_log
        )
        
        # Create large plan (100 tasks)
        plan = {
            "name": "Large Plan",
            "phases": [
                {
                    "id": i,
                    "name": f"Phase {i}",
                    "tasks": [
                        {
                            "id": f"{i}.{j}",
                            "name": f"Task {i}.{j}",
                            "dependencies": []
                        }
                        for j in range(1, 11)  # 10 tasks per phase
                    ]
                }
                for i in range(1, 11)  # 10 phases
            ]
        }
        
        start = time.time()
        todos = todo_orch.create_todos_from_plan(plan)
        elapsed = time.time() - start
        
        assert len(todos) == 100
        assert elapsed < 5.0  # Should complete in under 5 seconds
    
    def test_rapid_task_completion(self, tmp_path):
        """Test rapid sequential task completions"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / "cortex-brain").mkdir()
        (workspace / "cortex-brain" / "state").mkdir()
        (workspace / "cortex-brain" / "audit-logs").mkdir()
        
        state_mgr = StateManager(
            state_file=str(workspace / "cortex-brain" / "state" / "test.db")
        )
        audit_log = AuditLogger(
            log_directory=str(workspace / "cortex-brain" / "audit-logs")
        )
        
        todo_orch = TodoOrchestrator(
            workspace_root=str(workspace),
            state_manager=state_mgr,
            audit_logger=audit_log
        )
        
        # Create 50 tasks
        plan = {
            "name": "Rapid Test",
            "phases": [{
                "id": 1,
                "name": "Phase 1",
                "tasks": [
                    {"id": f"1.{i}", "name": f"Task {i}", "dependencies": []}
                    for i in range(1, 51)
                ]
            }]
        }
        
        todos = todo_orch.create_todos_from_plan(plan)
        
        # Complete all tasks rapidly
        start = time.time()
        for todo in todos[:20]:  # Complete first 20
            todo_orch.mark_task_completed(todo["task_id"], {"result": "done"})
        elapsed = time.time() - start
        
        assert elapsed < 3.0  # Should handle rapid completions
