"""
Tests for Master Orchestrator - Governance Integration
======================================================
Tests governance merger integration with master orchestrator.
ENHANCED for Task 2.2: Governance-to-TODO conversion

Author: GitHub Copilot (for CORTEX)
Created: 2026-01-08
Feature: feat04-core-orchestration
Phase: 2 Task: 2.2
TDD Phase: RED → GREEN → REFACTOR
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from src.orchestrators.core.master_orchestrator import MasterOrchestrator
from src.orchestrators.core.governance_merger import GovernanceMerger
from src.orchestrators.middleware.orchestrator_lifecycle import LifecycleState
from src.orchestrators.audit_logger import AuditCategory


class TestMasterOrchestratorGovernance:
    """Test master orchestrator governance integration"""
    
    @pytest.fixture
    def workspace_root(self, tmp_path):
        """Create temporary workspace"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        
        # Create cortex-brain structure
        brain_dir = workspace / "cortex-brain"
        brain_dir.mkdir()
        (brain_dir / "database").mkdir()
        
        # Create governance directories
        gov_dirs = [
            brain_dir / "tier0" / "governance",
            brain_dir / "tier1" / "governance",
            brain_dir / "tier2" / "governance",
            brain_dir / "tier3" / "governance"
        ]
        for d in gov_dirs:
            d.mkdir(parents=True, exist_ok=True)
        
        return workspace
    
    @pytest.fixture
    def master(self, workspace_root):
        """Create master orchestrator"""
        return MasterOrchestrator(workspace_root)
    
    @pytest.mark.ac_id("AC-GOV-005")
    def test_initializes_with_governance_orchestrator(self, master):
        """Should initialize with governance orchestrator registered"""
        assert master.has_orchestrator("governance")
    
    def test_has_governance_lifecycle_tracker(self, master):
        """Should have lifecycle tracker for governance"""
        lifecycle = master.get_lifecycle("governance")
        
        assert lifecycle is not None
        assert lifecycle.current_state == LifecycleState.READY
    
    def test_can_route_governance_requests(self, master):
        """Should route governance requests correctly"""
        result = master.execute("check governance rules")
        
        assert result.orchestrator == "governance"
        assert result.success is True
    
    def test_governance_request_returns_validation_result(self, master):
        """Should return validation result from governance"""
        result = master.execute("validate this rule")
        
        assert result.success is True
        assert result.result is not None
        assert "passed" in result.result
        assert "rules_checked" in result.result
    
    def test_governance_lifecycle_transitions(self, master):
        """Should properly manage governance lifecycle"""
        lifecycle = master.get_lifecycle("governance")
        initial_state = lifecycle.current_state
        
        result = master.execute("check governance")
        
        # Should return to READY after execution
        assert lifecycle.current_state == LifecycleState.READY
    
    def test_governance_error_handling(self, master):
        """Should handle governance errors gracefully"""
        # Governance orchestrator should handle any request
        result = master.execute("governance check invalid")
        
        assert result.orchestrator == "governance"
        # Should still succeed (stub implementation accepts all)
        assert result.success is True
    
    def test_governance_and_todo_coexist(self, master):
        """Should support both governance and TODO orchestrators"""
        # Execute governance request
        gov_result = master.execute("check governance")
        assert gov_result.orchestrator == "governance"
        
        # Execute TODO request
        todo_result = master.execute("create todo task")
        assert todo_result.orchestrator == "todo"
        
        # Both should succeed
        assert gov_result.success is True
        assert todo_result.success is True


class TestGovernanceMergerConnection:
    """Test Task 2.2: connect_governance() method"""
    
    @pytest.fixture
    def workspace_root(self, tmp_path):
        """Create temporary workspace"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        brain_dir = workspace / "cortex-brain"
        brain_dir.mkdir()
        (brain_dir / "database").mkdir()
        return workspace
    
    @pytest.fixture
    def master(self, workspace_root):
        """Create master orchestrator"""
        return MasterOrchestrator(workspace_root)
    
    @pytest.fixture
    def mock_governance_merger(self, workspace_root):
        """Create mock governance merger"""
        merger = Mock(spec=GovernanceMerger)
        merger.validate_rules = Mock(return_value=[])
        return merger
    
    def test_connect_governance_registers_merger(self, master, mock_governance_merger):
        """Should register GovernanceMerger"""
        # Act
        master.connect_governance(mock_governance_merger)
        
        # Assert
        assert master._governance_merger is not None
        assert master._governance_merger == mock_governance_merger
    
    def test_connect_governance_logs_operation(self, master, mock_governance_merger):
        """Should log governance connection to audit trail"""
        with patch.object(master.logger, 'info') as mock_log:
            # Act
            master.connect_governance(mock_governance_merger)
            
            # Assert
            mock_log.assert_called_once()
            call_kwargs = mock_log.call_args[1]
            assert call_kwargs['category'] == AuditCategory.EXECUTION
            assert call_kwargs['operation'] == 'connect_governance'


class TestGovernanceRuleValidation:
    """Test Task 2.2: _validate_governance_rules() method"""
    
    @pytest.fixture
    def workspace_root(self, tmp_path):
        """Create temporary workspace"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        brain_dir = workspace / "cortex-brain"
        brain_dir.mkdir()
        (brain_dir / "database").mkdir()
        return workspace
    
    @pytest.fixture
    def master(self, workspace_root):
        """Create master orchestrator"""
        return MasterOrchestrator(workspace_root)
    
    @pytest.fixture
    def mock_governance_merger(self):
        """Create mock governance merger"""
        merger = Mock(spec=GovernanceMerger)
        merger.validate_rules = Mock(return_value=[])
        return merger
    
    def test_validate_rules_with_no_violations(self, master, mock_governance_merger):
        """Should return empty list when no violations"""
        # Arrange
        master.connect_governance(mock_governance_merger)
        context = {'request_type': 'planning', 'has_yaml_plan': True}
        mock_governance_merger.validate_rules.return_value = []
        
        # Act
        violations = master._validate_governance_rules(context)
        
        # Assert
        assert violations == []
        mock_governance_merger.validate_rules.assert_called_once_with(context)
    
    def test_validate_rules_with_violations(self, master, mock_governance_merger):
        """Should return violations when governance rules violated"""
        # Arrange
        master.connect_governance(mock_governance_merger)
        context = {'request_type': 'implementation', 'has_yaml_plan': False}
        expected_violations = ["YAML_FIRST: No YAML plan found"]
        mock_governance_merger.validate_rules.return_value = expected_violations
        
        # Act
        violations = master._validate_governance_rules(context)
        
        # Assert
        assert violations == expected_violations
        assert len(violations) == 1
    
    def test_validate_rules_without_merger_registered(self, master):
        """Should return empty list if no governance merger registered"""
        # Arrange
        context = {'request_type': 'implementation'}
        
        # Act
        violations = master._validate_governance_rules(context)
        
        # Assert
        assert violations == []
    
    def test_validate_rules_logs_operation(self, master, mock_governance_merger):
        """Should log validation operation to audit trail"""
        # Arrange
        master.connect_governance(mock_governance_merger)
        context = {'request_type': 'planning'}
        
        with patch.object(master.logger, 'info') as mock_log:
            # Act
            master._validate_governance_rules(context)
            
            # Assert
            # Should have at least one call for validation (might have more from other operations)
            assert mock_log.call_count >= 1


class TestGovernanceViolationToTODO:
    """Test Task 2.2: _governance_violation_to_todo() method"""
    
    @pytest.fixture
    def workspace_root(self, tmp_path):
        """Create temporary workspace"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        brain_dir = workspace / "cortex-brain"
        brain_dir.mkdir()
        (brain_dir / "database").mkdir()
        return workspace
    
    @pytest.fixture
    def master(self, workspace_root):
        """Create master orchestrator"""
        return MasterOrchestrator(workspace_root)
    
    def test_converts_yaml_first_violation_to_todo(self, master):
        """Should convert YAML_FIRST violation to TODO with P0_CRITICAL priority"""
        # Arrange
        violation = "YAML_FIRST: Implementation without YAML plan detected"
        
        # Act
        todo = master._governance_violation_to_todo(violation)
        
        # Assert
        assert todo['title'] == 'Governance Violation: YAML_FIRST'
        assert 'Implementation without YAML plan' in todo['description']
        assert todo['priority'] == 'P0_CRITICAL'
        assert todo['category'] == 'GOVERNANCE_VIOLATION'
        assert todo['rule'] == 'YAML_FIRST'
    
    def test_converts_tdd_enforcement_violation_to_todo(self, master):
        """Should convert TDD_ENFORCEMENT violation to TODO"""
        # Arrange
        violation = "TDD_ENFORCEMENT: Tests not written before implementation"
        
        # Act
        todo = master._governance_violation_to_todo(violation)
        
        # Assert
        assert todo['title'] == 'Governance Violation: TDD_ENFORCEMENT'
        assert 'Tests not written' in todo['description']
        assert todo['priority'] == 'P0_CRITICAL'
        assert todo['category'] == 'GOVERNANCE_VIOLATION'
    
    def test_converts_git_isolation_violation_to_todo(self, master):
        """Should convert GIT_ISOLATION violation to TODO with P1_HIGH priority"""
        # Arrange
        violation = "GIT_ISOLATION: CORTEX code committed to user repo"
        
        # Act
        todo = master._governance_violation_to_todo(violation)
        
        # Assert
        assert todo['title'] == 'Governance Violation: GIT_ISOLATION'
        assert todo['priority'] == 'P1_HIGH'
        assert todo['category'] == 'GOVERNANCE_VIOLATION'
    
    def test_converts_unknown_violation_to_todo_with_default_priority(self, master):
        """Should handle unknown violations with default P2_MEDIUM priority"""
        # Arrange
        violation = "UNKNOWN_RULE: Some violation"
        
        # Act
        todo = master._governance_violation_to_todo(violation)
        
        # Assert
        assert todo['title'] == 'Governance Violation: UNKNOWN_RULE'
        assert todo['priority'] == 'P2_MEDIUM'
        assert todo['category'] == 'GOVERNANCE_VIOLATION'
    
    def test_todo_includes_all_required_fields(self, master):
        """Should include all required fields in TODO"""
        # Arrange
        violation = "HOLISTIC_DISCOVERY: Duplicate file created"
        
        # Act
        todo = master._governance_violation_to_todo(violation)
        
        # Assert
        assert 'title' in todo
        assert 'description' in todo
        assert 'priority' in todo
        assert 'category' in todo
        assert 'rule' in todo
        assert 'created_by' in todo
        assert todo['created_by'] == 'master_orchestrator'
    
    def test_converts_multiple_violations_to_todos(self, master):
        """Should convert multiple violations to multiple TODOs"""
        # Arrange
        violations = [
            "YAML_FIRST: No plan found",
            "TDD_ENFORCEMENT: No tests",
            "GIT_ISOLATION: Wrong repo"
        ]
        
        # Act
        todos = [master._governance_violation_to_todo(v) for v in violations]
        
        # Assert
        assert len(todos) == 3
        assert todos[0]['rule'] == 'YAML_FIRST'
        assert todos[1]['rule'] == 'TDD_ENFORCEMENT'
        assert todos[2]['rule'] == 'GIT_ISOLATION'
    
    def test_violation_to_todo_logs_operation(self, master):
        """Should log TODO creation to audit trail"""
        # Arrange
        violation = "YAML_FIRST: No plan"
        
        with patch.object(master.logger, 'info') as mock_log:
            # Act
            master._governance_violation_to_todo(violation)
            
            # Assert
            assert mock_log.call_count >= 1


class TestGovernanceIntegrationFlow:
    """Test complete governance-to-TODO integration flow"""
    
    @pytest.fixture
    def workspace_root(self, tmp_path):
        """Create temporary workspace"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        brain_dir = workspace / "cortex-brain"
        brain_dir.mkdir()
        (brain_dir / "database").mkdir()
        return workspace
    
    @pytest.fixture
    def master(self, workspace_root):
        """Create master orchestrator"""
        return MasterOrchestrator(workspace_root)
    
    @pytest.fixture
    def mock_governance_merger(self):
        """Create mock governance merger"""
        merger = Mock(spec=GovernanceMerger)
        merger.validate_rules = Mock(return_value=[])
        return merger
    
    def test_complete_governance_to_todo_flow(self, master, mock_governance_merger):
        """Should complete full flow: connect → validate → convert to TODOs"""
        # Arrange
        master.connect_governance(mock_governance_merger)
        mock_governance_merger.validate_rules.return_value = [
            "YAML_FIRST: No YAML plan",
            "TDD_ENFORCEMENT: No tests"
        ]
        
        # Act
        context = {'request_type': 'implementation', 'has_yaml_plan': False}
        violations = master._validate_governance_rules(context)
        todos = [master._governance_violation_to_todo(v) for v in violations]
        
        # Assert
        assert len(violations) == 2
        assert len(todos) == 2
        assert all(todo['category'] == 'GOVERNANCE_VIOLATION' for todo in todos)
        assert todos[0]['priority'] == 'P0_CRITICAL'
        assert todos[1]['priority'] == 'P0_CRITICAL'
