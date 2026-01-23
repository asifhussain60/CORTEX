"""
Refactoring Orchestrator Tests - TDD First (CORE-008)

Tests for RefactoringOrchestrator:
- AC-AR-012-01: Registry integration
- AC-AR-012-02: MCP tool exposure
- AC-AR-012-03: Audit logging with hash chain
- AC-AR-012-04: SOLID analysis capability
- AC-AR-012-05: Refactoring plan generation

Author: Asif Hussain
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any

from cortex.brain.core.result import Result, Ok, Err
from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator, OperationMode


class TestRefactoringOrchestratorInterface:
    """AC-AR-012-01: Verify interface compliance."""

    def test_implements_i_orchestrator(self):
        """Orchestrator implements IOrchestrator interface."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        
        orchestrator = RefactoringOrchestrator()
        assert isinstance(orchestrator, IOrchestrator)

    def test_get_name_returns_string(self):
        """get_name returns orchestrator name."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        
        orchestrator = RefactoringOrchestrator()
        name = orchestrator.get_name()
        
        assert isinstance(name, str)
        assert name == "RefactoringOrchestrator"

    def test_get_version_returns_semver(self):
        """get_version returns semantic version."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        
        orchestrator = RefactoringOrchestrator()
        version = orchestrator.get_version()
        
        assert isinstance(version, str)
        assert version.count(".") == 2  # semver format

    def test_get_mode_returns_operation_mode(self):
        """get_mode returns OperationMode enum."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        
        orchestrator = RefactoringOrchestrator()
        mode = orchestrator.get_mode()
        
        assert isinstance(mode, OperationMode)
        assert mode == OperationMode.EXECUTION


class TestRefactoringOrchestratorInitialization:
    """AC-AR-012-01: Initialization tests."""

    def test_initialize_returns_result(self):
        """initialize returns Result type."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        
        orchestrator = RefactoringOrchestrator()
        result = orchestrator.initialize()
        
        assert isinstance(result, Result)

    def test_initialize_success_on_first_call(self):
        """First initialization succeeds."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        
        orchestrator = RefactoringOrchestrator()
        result = orchestrator.initialize()
        
        assert result.is_ok()

    def test_initialize_fails_on_second_call(self):
        """Double initialization returns error."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        
        orchestrator = RefactoringOrchestrator()
        orchestrator.initialize()
        result = orchestrator.initialize()
        
        assert result.is_err()

    def test_singleton_pattern(self):
        """Singleton returns same instance."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        
        RefactoringOrchestrator.reset_instance()
        instance1 = RefactoringOrchestrator.instance()
        instance2 = RefactoringOrchestrator.instance()
        
        assert instance1 is instance2
        RefactoringOrchestrator.reset_instance()


class TestRefactoringOrchestratorMCPTools:
    """AC-AR-012-02: MCP tool exposure tests."""

    def test_get_mcp_tools_returns_result(self):
        """get_mcp_tools returns Result."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        
        orchestrator = RefactoringOrchestrator()
        result = orchestrator.get_mcp_tools()
        
        assert isinstance(result, Result)
        assert result.is_ok()

    def test_mcp_tools_contains_analyze_god_class(self):
        """MCP tools include analyze_god_class."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        
        orchestrator = RefactoringOrchestrator()
        result = orchestrator.get_mcp_tools()
        tools = result.unwrap()
        
        assert "analyze_god_class" in tools

    def test_mcp_tools_contains_generate_refactoring_plan(self):
        """MCP tools include generate_refactoring_plan."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        
        orchestrator = RefactoringOrchestrator()
        result = orchestrator.get_mcp_tools()
        tools = result.unwrap()
        
        assert "generate_refactoring_plan" in tools

    def test_mcp_tools_contains_apply_solid_decomposition(self):
        """MCP tools include apply_solid_decomposition."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        
        orchestrator = RefactoringOrchestrator()
        result = orchestrator.get_mcp_tools()
        tools = result.unwrap()
        
        assert "apply_solid_decomposition" in tools


class TestRefactoringOrchestratorAuditTrail:
    """AC-AR-012-03: Audit logging tests."""

    def test_get_audit_trail_returns_result(self):
        """get_audit_trail returns Result."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        
        orchestrator = RefactoringOrchestrator()
        result = orchestrator.get_audit_trail()
        
        assert isinstance(result, Result)
        assert result.is_ok()

    def test_audit_trail_records_initialization(self):
        """Initialization is recorded in audit trail."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        
        orchestrator = RefactoringOrchestrator()
        orchestrator.initialize()
        
        result = orchestrator.get_audit_trail()
        trail = result.unwrap()
        
        assert len(trail) >= 1
        assert trail[0].operation == "INITIALIZE"

    def test_audit_entries_have_hash_chain(self):
        """Audit entries maintain hash chain."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        
        orchestrator = RefactoringOrchestrator()
        orchestrator.initialize()
        orchestrator.execute_operation("analyze_god_class", {"file_path": "test.py"})
        
        result = orchestrator.get_audit_trail()
        trail = result.unwrap()
        
        assert len(trail) >= 2
        # Second entry's previous_hash matches first entry's current_hash
        assert trail[1].previous_hash == trail[0].current_hash


class TestRefactoringOrchestratorOperations:
    """AC-AR-012-04/05: Refactoring operation tests."""

    def test_execute_operation_returns_result(self):
        """execute_operation returns Result."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        
        orchestrator = RefactoringOrchestrator()
        result = orchestrator.execute_operation(
            "analyze_god_class",
            {"file_path": "test.py"},
        )
        
        assert isinstance(result, Result)

    def test_analyze_god_class_identifies_violations(self):
        """analyze_god_class returns SOLID violations."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        
        orchestrator = RefactoringOrchestrator()
        result = orchestrator.execute_operation(
            "analyze_god_class",
            {
                "file_path": "test.py",
                "content": """
class GodClass:
    def do_everything(self):
        self.save_to_db()
        self.send_email()
        self.render_html()
        self.validate_input()
""",
            },
        )
        
        assert result.is_ok()
        analysis = result.unwrap()
        assert "violations" in analysis
        assert "SRP" in str(analysis["violations"])

    def test_generate_refactoring_plan_creates_phases(self):
        """generate_refactoring_plan returns phased plan."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        
        orchestrator = RefactoringOrchestrator()
        result = orchestrator.execute_operation(
            "generate_refactoring_plan",
            {
                "god_classes": ["Program.cs", "AppComponent.ts"],
                "target_architecture": "clean_architecture",
            },
        )
        
        assert result.is_ok()
        plan = result.unwrap()
        assert "phases" in plan
        assert len(plan["phases"]) > 0

    def test_unknown_operation_returns_error(self):
        """Unknown operation returns Err."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )
        
        orchestrator = RefactoringOrchestrator()
        result = orchestrator.execute_operation(
            "nonexistent_operation",
            {},
        )
        
        assert result.is_err()
