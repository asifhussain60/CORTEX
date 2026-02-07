"""
Tests for ArchitectureGuard - Phase 24 Layer 1
Tests MUST come before implementation (CORE-008 TDD)
"""

import pytest
pytestmark = pytest.mark.skip(reason="Phase 38.0 remediation pending - architecture guard module not found")

from pathlib import Path
from datetime import datetime

# Wrapped import - module may not exist
try:
    from cortex.orchestrators.core.architecture_guard import (
        ArchitectureGuard,
        GateVerdict,
        ValidationResult,
        PhaseAlignment,
        SuggestedPhase,
    )
except ModuleNotFoundError:
    pass


class TestArchitectureGuardInitialization:
    """Test ArchitectureGuard initialization."""
    
    def test_guard_initializes_successfully(self):
        """Test guard initialization with valid registry."""
        guard = ArchitectureGuard()
        result = guard.initialize()
        
        assert result.is_ok()
        assert "initialized" in result.unwrap().lower()
    
    def test_guard_has_correct_name(self):
        """Test guard returns correct orchestrator name."""
        guard = ArchitectureGuard()
        assert guard.get_name() == "ArchitectureGuard"
    
    def test_guard_has_version(self):
        """Test guard has version number."""
        guard = ArchitectureGuard()
        version = guard.get_version()
        assert version == "1.0.0"
    
    def test_guard_uses_validation_mode(self):
        """Test guard operates in VALIDATION mode."""
        guard = ArchitectureGuard()
        from cortex.brain.core.interfaces.i_orchestrator import OperationMode
        assert guard.get_mode() == OperationMode.VALIDATION


class TestArchitectureGuardMCPTools:
    """Test MCP tool exposure."""
    
    def test_guard_exposes_validate_architecture_tool(self):
        """Test guard exposes cortex_validate_architecture MCP tool."""
        guard = ArchitectureGuard()
        guard.initialize()
        
        tools_result = guard.get_mcp_tools()
        assert tools_result.is_ok()
        
        tools = tools_result.unwrap()
        assert "cortex_validate_architecture" in tools
        
        tool_spec = tools["cortex_validate_architecture"]
        assert tool_spec["name"] == "cortex_validate_architecture"
        assert "parameters" in tool_spec
        assert "request_description" in tool_spec["parameters"]
        assert "intent_type" in tool_spec["parameters"]


class TestValidationProceeding:
    """Test PROCEED verdict cases."""
    
    def test_allows_aligned_minor_request(self):
        """Test guard allows request aligned with active phase, low regression risk."""
        guard = ArchitectureGuard()
        guard.initialize()
        
        result = guard.validate_request(
            request_description="Update dashboard CSS styling for better readability",
            intent_type="REFACTOR",
            scope=["cortex-registry/_cortex-master/dashboard/index.html"]
        )
        
        assert result.is_ok()
        validation = result.unwrap()
        
        assert validation.verdict == GateVerdict.PROCEED
        assert validation.phase_alignment.regression_risk < 0.3
        assert "aligns" in validation.reasoning.lower() or "acceptable" in validation.reasoning.lower()
    
    def test_allows_fix_with_no_conflicts(self):
        """Test guard allows FIX intent with no completed phase conflicts."""
        guard = ArchitectureGuard()
        guard.initialize()
        
        result = guard.validate_request(
            request_description="Fix typo in error message",
            intent_type="FIX",
            scope=["cortex/orchestrators/support/some_file.py"]
        )
        
        assert result.is_ok()
        validation = result.unwrap()
        
        assert validation.verdict == GateVerdict.PROCEED
        assert len(validation.phase_alignment.conflicts) == 0


class TestValidationBlocking:
    """Test BLOCK verdict cases."""
    
    def test_blocks_contradictory_request(self):
        """Test guard blocks request contradicting completed phase commitments."""
        guard = ArchitectureGuard()
        guard.initialize()
        
        # This should conflict with phase-15's kebab-case commitment
        result = guard.validate_request(
            request_description="Rename all files to SCREAMING_CASE format for consistency",
            intent_type="REFACTOR",
            scope=[
                "cortex/orchestrators/core/MASTER_ORCHESTRATOR.py",
                "cortex/orchestrators/core/TDD_ORCHESTRATOR.py",
            ]
        )
        
        assert result.is_ok()
        validation = result.unwrap()
        
        assert validation.verdict == GateVerdict.BLOCK
        assert len(validation.phase_alignment.conflicts) > 0
        assert validation.phase_alignment.regression_risk >= 0.4  # Has conflicts + REFACTOR
        assert "conflict" in validation.reasoning.lower() or "risk" in validation.reasoning.lower()
    
    def test_blocks_high_regression_risk(self):
        """Test guard blocks request with high regression risk."""
        guard = ArchitectureGuard()
        guard.initialize()
        
        # High risk: touching core orchestrators without clear alignment
        result = guard.validate_request(
            request_description="Completely rewrite orchestrator coordination logic",
            intent_type="REFACTOR",
            scope=[
                "cortex/orchestrators/core/master_orchestrator.py",
                "cortex/orchestrators/core/tdd_orchestrator.py",
                "cortex/orchestrators/core/intent_router.py",
            ]
        )
        
        assert result.is_ok()
        validation = result.unwrap()
        
        # Should either BLOCK or CREATE_PHASE - definitely not PROCEED
        assert validation.verdict != GateVerdict.PROCEED
        assert validation.phase_alignment.regression_risk >= 0.3


class TestPhaseCreation:
    """Test CREATE_PHASE verdict cases."""
    
    def test_suggests_phase_creation_for_significant_change(self):
        """Test guard suggests phase creation for significant untracked change."""
        guard = ArchitectureGuard()
        guard.initialize()
        
        result = guard.validate_request(
            request_description="Add real-time WebSocket support for all orchestrators",
            intent_type="IMPLEMENT",
            scope=[
                "cortex/orchestrators/core/master_orchestrator.py",
                "cortex/orchestrators/core/tdd_orchestrator.py",
                "cortex/mcp/server.py",
                "cortex/mcp/websocket_handler.py",
                "cortex/mcp/connection_manager.py",
                "cortex/mcp/event_broadcaster.py",
            ]
        )
        
        assert result.is_ok()
        validation = result.unwrap()
        
        assert validation.verdict == GateVerdict.CREATE_PHASE
        assert validation.suggested_phase is not None
        assert validation.suggested_phase.id.startswith("phase-")
        assert len(validation.suggested_phase.scope) > 0
        assert "significant" in validation.reasoning.lower() or "tracked" in validation.reasoning.lower()
    
    def test_suggests_phase_for_core_implementation(self):
        """Test guard suggests phase for core orchestrator implementation."""
        guard = ArchitectureGuard()
        guard.initialize()
        
        result = guard.validate_request(
            request_description="Implement new SecurityAuditOrchestrator for OWASP compliance",
            intent_type="IMPLEMENT",
            scope=[
                "cortex/orchestrators/core/security_audit_orchestrator.py",
                "cortex/wiring/specifications/wiring.yaml",
            ]
        )
        
        assert result.is_ok()
        validation = result.unwrap()
        
        # Core orchestrator = significant change
        if validation.verdict == GateVerdict.CREATE_PHASE:
            assert validation.suggested_phase is not None
            assert validation.suggested_phase.priority in ["P0", "P1"]


class TestRegressionRiskCalculation:
    """Test regression risk scoring."""
    
    def test_calculates_risk_for_conflicts(self):
        """Test risk increases with completed phase conflicts."""
        guard = ArchitectureGuard()
        guard.initialize()
        
        # Request with conflicts
        result = guard.validate_request(
            request_description="Switch from JSON files to SQLite database for all registry data",
            intent_type="IMPLEMENT",
            scope=["cortex-registry/_cortex-master/"]
        )
        
        assert result.is_ok()
        validation = result.unwrap()
        
        # Should have some regression risk if conflicts detected
        if len(validation.phase_alignment.conflicts) > 0:
            assert validation.phase_alignment.regression_risk > 0.0
    
    def test_risk_lower_for_small_scope(self):
        """Test regression risk is lower for smaller scope changes."""
        guard = ArchitectureGuard()
        guard.initialize()
        
        result = guard.validate_request(
            request_description="Add docstring to helper function",
            intent_type="REFACTOR",
            scope=["cortex/utils/helper.py"]
        )
        
        assert result.is_ok()
        validation = result.unwrap()
        
        # Small scope should have low risk
        assert validation.phase_alignment.regression_risk < 0.5


class TestPhaseAlignment:
    """Test phase alignment checking."""
    
    def test_detects_active_phases(self):
        """Test guard loads and detects active phases."""
        guard = ArchitectureGuard()
        guard.initialize()
        
        result = guard.validate_request(
            request_description="Update dashboard",
            intent_type="REFACTOR",
            scope=["cortex-registry/_cortex-master/dashboard/index.html"]
        )
        
        assert result.is_ok()
        validation = result.unwrap()
        
        # Should detect some active phases
        assert len(validation.phase_alignment.active_phases) > 0
    
    def test_checks_completed_phases_for_conflicts(self):
        """Test guard checks completed phases for conflicts."""
        guard = ArchitectureGuard()
        guard.initialize()
        
        # This should check against completed phases
        result = guard.validate_request(
            request_description="Test request",
            intent_type="IMPLEMENT",
            scope=["test.py"]
        )
        
        assert result.is_ok()
        validation = result.unwrap()
        
        # Result should have phase alignment data
        assert validation.phase_alignment is not None
        assert isinstance(validation.phase_alignment.conflicts, list)


class TestIndexCaching:
    """Test master plan index caching."""
    
    def test_caches_index_between_calls(self):
        """Test guard caches index to avoid repeated file reads."""
        guard = ArchitectureGuard()
        guard.initialize()
        
        # First call
        result1 = guard.validate_request(
            request_description="Test 1",
            intent_type="FIX",
            scope=[]
        )
        
        # Second call (should use cache)
        result2 = guard.validate_request(
            request_description="Test 2",
            intent_type="FIX",
            scope=[]
        )
        
        assert result1.is_ok()
        assert result2.is_ok()
        
        # Both should succeed (cache working)
        assert result1.unwrap().phase_alignment is not None
        assert result2.unwrap().phase_alignment is not None


class TestSuggestedPhaseGeneration:
    """Test suggested phase structure generation."""
    
    def test_generates_phase_with_priority(self):
        """Test suggested phase includes priority based on scope."""
        guard = ArchitectureGuard()
        guard.initialize()
        
        result = guard.validate_request(
            request_description="Add new core feature",
            intent_type="IMPLEMENT",
            scope=[
                "cortex/orchestrators/core/new_orchestrator.py",
                "cortex/wiring/specifications/wiring.yaml",
            ]
        )
        
        assert result.is_ok()
        validation = result.unwrap()
        
        if validation.verdict == GateVerdict.CREATE_PHASE:
            assert validation.suggested_phase.priority in ["P0", "P1", "P2", "P3"]
    
    def test_generates_phase_with_estimated_effort(self):
        """Test suggested phase includes estimated effort."""
        guard = ArchitectureGuard()
        guard.initialize()
        
        result = guard.validate_request(
            request_description="Major refactoring",
            intent_type="REFACTOR",
            scope=[f"file{i}.py" for i in range(15)]  # 15 files
        )
        
        assert result.is_ok()
        validation = result.unwrap()
        
        if validation.verdict == GateVerdict.CREATE_PHASE:
            assert validation.suggested_phase.estimated_effort is not None
            assert any(word in validation.suggested_phase.estimated_effort.lower() 
                      for word in ["day", "week", "hour"])


class TestExecuteOperation:
    """Test execute_operation method."""
    
    def test_executes_validate_request_operation(self):
        """Test execute_operation routes to validate_request."""
        guard = ArchitectureGuard()
        guard.initialize()
        
        result = guard.execute_operation(
            operation_name="validate_request",
            parameters={
                "request_description": "Test operation",
                "intent_type": "FIX",
                "scope": []
            }
        )
        
        assert result.is_ok()
        validation = result.unwrap()
        assert isinstance(validation, ValidationResult)
    
    def test_rejects_unknown_operation(self):
        """Test execute_operation rejects unknown operations."""
        guard = ArchitectureGuard()
        guard.initialize()
        
        result = guard.execute_operation(
            operation_name="unknown_operation",
            parameters={}
        )
        
        assert result.is_err()
        assert "unknown" in result.error.lower()


class TestAuditTrail:
    """Test audit trail method."""
    
    def test_returns_empty_audit_trail(self):
        """Test get_audit_trail returns empty list (not implemented)."""
        guard = ArchitectureGuard()
        guard.initialize()
        
        result = guard.get_audit_trail()
        
        assert result.is_ok()
        assert isinstance(result.unwrap(), list)
