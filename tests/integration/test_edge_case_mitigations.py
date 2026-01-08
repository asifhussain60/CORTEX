"""
Edge Case Mitigation Tests - CORTEX 6.0

Tests all edge case mitigations from risk registry
Feature: feat07-integration Phase 1 Task 1.2

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
"""

import pytest
import threading
import time
from unittest.mock import Mock, MagicMock
from src.infrastructure.risk_mitigations import (
    EdgeCaseMitigations,
    FailureModeMitigations,
    RaceConditionMitigations,
    EmptyDagError,
    DagTooDeepError,
    OrphanedTaskError,
    MitigationRegistry,
    RiskCategory,
    Severity
)


# ==============================================================================
# EDGE CASE TESTS (EC-001 to EC-005)
# ==============================================================================

class TestEC001EmptyDagExecution:
    """EC-001: Empty DAG Execution mitigation tests"""
    
    def test_empty_dag_rejection(self):
        """Test that empty DAG raises EmptyDagError"""
        # Create empty DAG mock
        dag = Mock()
        dag.is_empty.return_value = True
        
        with pytest.raises(EmptyDagError, match="must contain at least one task"):
            EdgeCaseMitigations.validate_dag_not_empty(dag)
    
    def test_dag_with_empty_tasks_list(self):
        """Test that DAG with empty tasks list raises error"""
        dag = Mock()
        dag.is_empty.return_value = False
        dag.tasks = []
        
        with pytest.raises(EmptyDagError, match="no executable tasks"):
            EdgeCaseMitigations.validate_dag_not_empty(dag)
    
    def test_valid_dag_passes(self):
        """Test that valid DAG passes validation"""
        dag = Mock()
        dag.is_empty.return_value = False
        dag.tasks = [Mock(), Mock()]
        
        # Should not raise
        EdgeCaseMitigations.validate_dag_not_empty(dag)
    
    def test_none_dag_raises_error(self):
        """Test that None DAG raises error"""
        with pytest.raises(EmptyDagError):
            EdgeCaseMitigations.validate_dag_not_empty(None)


class TestEC002OrphanedTasks:
    """EC-002: Orphaned Tasks After Dependency Removal"""
    
    def test_orphan_prevention(self):
        """Test that orphaned tasks are identified and handled"""
        dag = Mock()
        dag.get_dependents.return_value = ['task2', 'task3']
        dag.mark_task_blocked = Mock()
        
        affected = EdgeCaseMitigations.handle_orphaned_tasks(dag, 'task1')
        
        assert affected == ['task2', 'task3']
        assert dag.mark_task_blocked.call_count == 2
    
    def test_no_dependents_returns_empty(self):
        """Test that task with no dependents returns empty list"""
        dag = Mock()
        dag.get_dependents.return_value = []
        
        affected = EdgeCaseMitigations.handle_orphaned_tasks(dag, 'task1')
        
        assert affected == []
    
    def test_dependent_tasks_marked_blocked(self):
        """Test that dependent tasks are marked as blocked"""
        dag = Mock()
        dag.get_dependents.return_value = ['dependent1']
        dag.mark_task_blocked = Mock()
        
        EdgeCaseMitigations.handle_orphaned_tasks(dag, 'parent_task')
        
        dag.mark_task_blocked.assert_called_once()
        # Verify the call arguments
        call_args = dag.mark_task_blocked.call_args[0]
        assert call_args[0] == 'dependent1'
        assert 'parent_task' in call_args[1]


class TestEC003UnicodeInTaskNames:
    """EC-003: Unicode in Task Names"""
    
    def test_unicode_task_names(self):
        """Test that Unicode characters are normalized"""
        # Test with emoji
        emoji_text = "Deploy 🚀 application"
        normalized = EdgeCaseMitigations.normalize_unicode(emoji_text)
        assert isinstance(normalized, str)
        assert "🚀" in normalized
    
    def test_accented_characters(self):
        """Test normalization of accented characters"""
        text = "Café résumé"
        normalized = EdgeCaseMitigations.normalize_unicode(text)
        assert isinstance(normalized, str)
        assert "é" in normalized
    
    def test_combining_characters(self):
        """Test combining characters are normalized to NFC form"""
        # e + combining acute accent
        combining = "e\u0301"
        normalized = EdgeCaseMitigations.normalize_unicode(combining)
        # Should be normalized to é (single character)
        assert normalized == "é"
    
    def test_non_string_input(self):
        """Test that non-string input is converted"""
        result = EdgeCaseMitigations.normalize_unicode(123)
        assert result == "123"
    
    def test_mixed_unicode(self):
        """Test mixed Unicode content"""
        text = "Test 测试 тест テスト"
        normalized = EdgeCaseMitigations.normalize_unicode(text)
        assert isinstance(normalized, str)
        assert "测试" in normalized
        assert "тест" in normalized
        assert "テスト" in normalized


class TestEC004DeepDagHandling:
    """EC-004: Extremely Deep DAG (>100 levels)"""
    
    def test_deep_dag_handling(self):
        """Test that extremely deep DAG is rejected"""
        dag = Mock()
        
        # Create a deep chain: root -> t1 -> t2 -> ... -> t101
        dag.get_root_tasks.return_value = ['root']
        
        # Mock get_dependents to create a chain of 101 tasks
        def get_dependents_mock(task_id):
            if task_id == 'root':
                return ['t1']
            task_num = int(task_id[1:]) if task_id.startswith('t') else 0
            if task_num < 101:
                return [f't{task_num + 1}']
            return []
        
        dag.get_dependents.side_effect = get_dependents_mock
        dag.tasks = [f't{i}' for i in range(102)]
        
        with pytest.raises(DagTooDeepError, match="exceeds maximum allowed depth"):
            EdgeCaseMitigations.validate_dag_depth(dag, max_depth=100)
    
    def test_shallow_dag_passes(self):
        """Test that shallow DAG passes validation"""
        dag = Mock()
        dag.get_root_tasks.return_value = ['root']
        dag.get_dependents.return_value = []
        dag.tasks = ['root', 't1', 't2']
        
        # Should not raise
        depth = EdgeCaseMitigations.validate_dag_depth(dag, max_depth=100)
        assert depth == 0
    
    def test_dag_without_tasks_attribute(self):
        """Test DAG without tasks attribute doesn't crash"""
        dag = Mock(spec=[])  # No attributes
        
        # Should not raise
        EdgeCaseMitigations.validate_dag_depth(dag)
    
    def test_iterative_algorithm_no_stack_overflow(self):
        """Test that iterative algorithm handles deep DAG without stack overflow"""
        dag = Mock()
        dag.get_root_tasks.return_value = ['root']
        
        # Create a valid deep DAG (under limit)
        def get_dependents_mock(task_id):
            if task_id == 'root':
                return ['t1']
            task_num = int(task_id[1:]) if task_id.startswith('t') else 0
            if task_num < 50:
                return [f't{task_num + 1}']
            return []
        
        dag.get_dependents.side_effect = get_dependents_mock
        dag.tasks = [f't{i}' for i in range(51)]
        
        # Should not raise and should return correct depth
        depth = EdgeCaseMitigations.validate_dag_depth(dag, max_depth=100)
        assert depth == 50


class TestEC005GovernanceConflictResolution:
    """EC-005: Governance Rule Conflict Deadlock"""
    
    def test_governance_deadlock_resolution(self):
        """Test that governance conflicts are resolved"""
        rule1 = {
            "category": "business_tier0",
            "rule": "Business rule",
            "created_at": "2026-01-01T00:00:00Z"
        }
        rule2 = {
            "category": "cortex_tier0",
            "rule": "CORTEX rule",
            "created_at": "2026-01-02T00:00:00Z"
        }
        
        # Business tier0 should win over CORTEX tier0
        result = EdgeCaseMitigations.resolve_governance_conflict(rule1, rule2)
        assert result == rule1
    
    def test_cortex_tier0_beats_company(self):
        """Test that CORTEX tier0 beats company practices"""
        rule1 = {
            "category": "cortex_tier0",
            "rule": "CORTEX rule",
            "created_at": "2026-01-01"
        }
        rule2 = {
            "category": "company_practices",
            "rule": "Company rule",
            "created_at": "2026-01-01"
        }
        
        result = EdgeCaseMitigations.resolve_governance_conflict(rule1, rule2)
        assert result == rule1
    
    def test_timestamp_tiebreaker(self):
        """Test that timestamp breaks ties"""
        rule1 = {
            "category": "cortex_tier0",
            "rule": "Older rule",
            "created_at": "2026-01-01T00:00:00Z"
        }
        rule2 = {
            "category": "cortex_tier0",
            "rule": "Newer rule",
            "created_at": "2026-01-02T00:00:00Z"
        }
        
        # Older rule should win
        result = EdgeCaseMitigations.resolve_governance_conflict(rule1, rule2)
        assert result == rule1
    
    def test_priority_order(self):
        """Test complete priority order"""
        rules = [
            {"category": "knowledge_practices", "created_at": "2026-01-01"},
            {"category": "company_practices", "created_at": "2026-01-01"},
            {"category": "cortex_tier0", "created_at": "2026-01-01"},
            {"category": "business_tier0", "created_at": "2026-01-01"},
        ]
        
        # Business should beat all others
        for other_rule in rules[:3]:
            result = EdgeCaseMitigations.resolve_governance_conflict(
                rules[3], other_rule
            )
            assert result == rules[3]


# ==============================================================================
# FAILURE MODE TESTS (FM-001 to FM-002)
# ==============================================================================

class TestFM002AuditLogFailsafe:
    """FM-002: Audit Log Write Failure"""
    
    def test_audit_failsafe(self):
        """Test that audit failsafe queues entries when primary logger fails"""
        failsafe = FailureModeMitigations.create_audit_failsafe(max_queue_size=10)
        
        # Mock failing primary logger
        primary_logger = Mock()
        primary_logger.log.side_effect = Exception("Disk full")
        
        entry = {"level": "INFO", "message": "Test"}
        result = failsafe.log(entry, primary_logger)
        
        assert result is True  # Should succeed via queue
        assert len(failsafe.queue) == 1
    
    def test_queue_overflow_handling(self):
        """Test that queue overflow is detected"""
        failsafe = FailureModeMitigations.create_audit_failsafe(max_queue_size=2)
        
        # Fill queue
        for i in range(3):
            result = failsafe.queue_entry({"message": f"Entry {i}"})
            if i < 2:
                assert result is True
            else:
                assert result is False  # Queue full
        
        assert failsafe.is_queue_full is True
    
    def test_queue_flush(self):
        """Test that queue can be flushed to primary logger"""
        failsafe = FailureModeMitigations.create_audit_failsafe()
        
        # Add entries to queue
        for i in range(5):
            failsafe.queue_entry({"message": f"Entry {i}"})
        
        # Mock working primary logger
        primary_logger = Mock()
        primary_logger.log = Mock()
        
        flushed = failsafe.flush_queue(primary_logger)
        
        assert flushed == 5
        assert len(failsafe.queue) == 0
        assert primary_logger.log.call_count == 5


# ==============================================================================
# RACE CONDITION TESTS (RC-001)
# ==============================================================================

class TestRC001ConcurrentTaskUpdates:
    """RC-001: Concurrent Task Status Updates"""
    
    def test_atomic_task_update(self):
        """Test that task updates are atomic"""
        mitigator = RaceConditionMitigations()
        
        counter = {"value": 0}
        
        def increment():
            current = counter["value"]
            time.sleep(0.001)  # Simulate race condition
            counter["value"] = current + 1
            return counter["value"]
        
        # Run concurrent updates
        threads = []
        for _ in range(10):
            t = threading.Thread(
                target=lambda: mitigator.atomic_task_update("task1", increment)
            )
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # With proper locking, final value should be 10
        assert counter["value"] == 10
    
    def test_different_tasks_independent_locks(self):
        """Test that different tasks use independent locks"""
        mitigator = RaceConditionMitigations()
        
        lock1 = mitigator.get_task_lock("task1")
        lock2 = mitigator.get_task_lock("task2")
        
        assert lock1 is not lock2
    
    def test_same_task_same_lock(self):
        """Test that same task always gets same lock"""
        mitigator = RaceConditionMitigations()
        
        lock1 = mitigator.get_task_lock("task1")
        lock2 = mitigator.get_task_lock("task1")
        
        assert lock1 is lock2


# ==============================================================================
# MITIGATION REGISTRY TESTS
# ==============================================================================

class TestMitigationRegistry:
    """Test the mitigation registry"""
    
    def test_registry_has_all_edge_cases(self):
        """Test that all 5 edge cases are registered"""
        from src.infrastructure.risk_mitigations import get_registry
        
        registry = get_registry()
        edge_cases = registry.list_by_category(RiskCategory.EDGE_CASE)
        
        assert len(edge_cases) >= 5
        
        # Check specific edge cases
        assert registry.get("EC-001") is not None
        assert registry.get("EC-002") is not None
        assert registry.get("EC-003") is not None
        assert registry.get("EC-004") is not None
        assert registry.get("EC-005") is not None
    
    def test_registry_has_failure_modes(self):
        """Test that failure modes are registered"""
        from src.infrastructure.risk_mitigations import get_registry
        
        registry = get_registry()
        failure_modes = registry.list_by_category(RiskCategory.FAILURE_MODE)
        
        assert len(failure_modes) >= 2
        assert registry.get("FM-001") is not None
        assert registry.get("FM-002") is not None
    
    def test_registry_stats(self):
        """Test registry statistics"""
        from src.infrastructure.risk_mitigations import get_registry
        
        registry = get_registry()
        stats = registry.get_stats()
        
        assert stats["total"] >= 7
        assert "by_category" in stats
        assert "by_severity" in stats
    
    def test_severity_filtering(self):
        """Test filtering by severity"""
        from src.infrastructure.risk_mitigations import get_registry
        
        registry = get_registry()
        critical = registry.list_by_severity(Severity.CRITICAL)
        
        assert len(critical) >= 2  # EC-002 and FM-001


# ==============================================================================
# INTEGRATION TESTS
# ==============================================================================

class TestEdgeCaseIntegration:
    """Integration tests for edge case mitigations"""
    
    def test_all_mitigations_registered(self):
        """Test that all critical mitigations are registered"""
        from src.infrastructure.risk_mitigations import get_registry
        
        registry = get_registry()
        
        critical_risks = ["EC-001", "EC-002", "EC-005", "FM-001", "FM-002"]
        for risk_id in critical_risks:
            mitigation = registry.get(risk_id)
            assert mitigation is not None, f"{risk_id} not registered"
            assert mitigation.status == "ACTIVE"
    
    def test_mitigation_coverage(self):
        """Test that we have good coverage of risk categories"""
        from src.infrastructure.risk_mitigations import get_registry
        
        registry = get_registry()
        stats = registry.get_stats()
        
        # Should have mitigations for multiple categories
        categories_with_mitigations = sum(
            1 for count in stats["by_category"].values() if count > 0
        )
        
        # We currently have EDGE_CASE and FAILURE_MODE categories covered
        assert categories_with_mitigations >= 2  # At least 2 categories covered
